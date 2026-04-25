# oras-gateway

Download an ORAS (OCI Registry As Storage) artifact with curl:

oras://localhost:5000/artifact:latest

`ORAS_GATEWAY=http://localhost:8080`

curl http://localhost:8080/oras/localhost:5000/artifact:latest

## Similar

Inspired by ipfs:// and `$IPFS_GATEWAY`

As in <https://curl.se/docs/ipfs.html>

## Use Case

Allows you to pull artifacts from a registry, without a client.

```console
$ curl --head $ORAS_GATEWAY/oras/localhost:5000/artifact
...
Content-Type: application/vnd.oci.image.layer.v1.tar
Content-Length: 12
Content-Digest: sha-256=:qUiQTy8PR5uPgZdpSzAYSw0u0cHNKh7A+4XSmaGSpEc=:
Content-Disposition: attachment; filename=artifact.txt
...
$ curl -RLOJ $ORAS_GATEWAY/oras/localhost:5000/artifact
...
curl: Saved to filename 'artifact.txt'
$ echo "qUiQTy8PR5uPgZdpSzAYSw0u0cHNKh7A+4XSmaGSpEc=" | base64 -d | hexdump -C
00000000  a9 48 90 4f 2f 0f 47 9b  8f 81 97 69 4b 30 18 4b  |.H.O/.G....iK0.K|
00000010  0d 2e d1 c1 cd 2a 1e c0  fb 85 d2 99 a1 92 a4 47  |.....*.........G|
00000020
$ sha256sum artifact.txt
a948904f2f0f479b8f8197694b30184b0d2ed1c1cd2a1ec0fb85d299a192a447  artifact.txt
```

Compare with `oras pull localhost:5000/artifact:latest` command.

```console
$ oras pull localhost:5000/artifact
Error: localhost:5000/artifact: invalid image reference, expecting <name:tag|name@digest>
$ oras pull localhost:5000/artifact:latest
Downloading a948904f2f0f artifact.txt
Downloaded  a948904f2f0f artifact.txt
Pulled [registry] localhost:5000/artifact:latest
Digest: sha256:9c461af426ce2c4fadba5c5a07421fe89c1f12c6c54e03347ca49059f1b6873a
$ oras manifest fetch localhost:5000/artifact:latest | jq
{
  "schemaVersion": 2,
  "mediaType": "application/vnd.oci.image.manifest.v1+json",
  "artifactType": "application/vnd.unknown.artifact.v1",
  "config": {
    "mediaType": "application/vnd.oci.empty.v1+json",
    "digest": "sha256:44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a",
    "size": 2,
    "data": "e30="
  },
  "layers": [
    {
      "mediaType": "application/vnd.oci.image.layer.v1.tar",
      "digest": "sha256:a948904f2f0f479b8f8197694b30184b0d2ed1c1cd2a1ec0fb85d299a192a447",
      "size": 12,
      "annotations": {
        "org.opencontainers.image.title": "artifact.txt"
      }
    }
  ],
  "annotations": {
    "org.opencontainers.image.created": "2026-04-21T12:30:35Z"
  }
}
```
