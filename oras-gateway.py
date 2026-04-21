#!/usr/bin/env python3
# simple proxy for oras artifacts
import http.server
import oras.client

import argparse
from urllib.parse import urlparse
import base64
from collections import namedtuple


def is_loopback(ip):
    return ip == "localhost" or ip == "127.0.0.1"


def get_basic_auth(headers):
    # Authorization: Basic Zm9vOmJhcgo=
    if "Authorization" in headers:
        fields = headers["Authorization"].split(" ", 1)
        if len(fields) == 2 and fields[0] == "Basic":
            decoded = base64.b64decode(fields[1].encode()).decode()
            username, password = decoded.split(":")
            auth = namedtuple("auth", ["username", "password"])
            return auth(username, password)
    return None


class ORASServer(http.server.BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.do(False)

    def do_GET(self):
        self.do(True)

    def do(self, content):
        package = self.path.replace("/oras/", "", 1)
        url = urlparse("oras://" + package)
        client = oras.client.OrasClient(
            hostname=url.netloc, insecure=is_loopback(url.hostname)
        )
        auth = get_basic_auth(self.headers)
        if auth:
            client.login(auth.username, auth.password, hostname=url.netloc)
        artifact = ""
        blob = None
        try:
            manifest = client.get_manifest(package)
            assert len(manifest["layers"]) == 1
            layer = manifest["layers"][0]
            artifact = layer["annotations"]["org.opencontainers.image.title"]
            if content:
                blob = client.get_blob(
                    package, digest=layer["digest"], stream=True, head=False
                )
        except ValueError as e:
            self.send_error(500, str(e))
            return

        self.send_response(200)
        self.send_header("Content-type", layer["mediaType"])
        self.send_header("Content-length", layer["size"])
        self.send_header("Content-disposition", "attachment; filename=%s" % artifact)
        self.end_headers()
        if content:
            self.wfile.write(blob.content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--host", default="localhost", help="host")
    parser.add_argument("--port", type=int, default=8080, help="port")
    args = parser.parse_args()
    server = http.server.HTTPServer((args.host, args.port), ORASServer)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
