# Container Networking Lab

## Overview

A containerized application appears to start correctly but cannot be reached from the host machine.

Your task is to investigate the networking path and determine why requests are not reaching the application.

## Getting Started

Build the Docker image:

```bash
docker build -t netlab .
```

Run the container:

```bash
docker run -d -p 8080:8080 --name app netlab
```

## Verification

Check if the container is running:

```bash
docker ps
```

Attempt to reach the health endpoint:

```bash
curl localhost:8080/health
```

If the endpoint is unreachable, investigate the networking path and fix the issue.

## Root cause and fix

The broken link was **container port 8080 -> application bind address**. The
server listened only on `127.0.0.1`, so Docker's published `8080:8080` port
could not route traffic from the container network interface to the process;
this presents as a refused connection from the host. The server now listens on
`0.0.0.0:8080`, which accepts Docker's forwarded traffic while retaining the
same published host port.

After rebuilding and running the image, verify the complete path with:

```bash
docker build -t netlab .
docker rm -f app 2>/dev/null || true
docker run -d -p 8080:8080 --name app netlab
curl -i localhost:8080/health
```


## Submission evidence

The five labelled terminal-evidence pages are included in
[`evidence/container-networking-lab-report.pdf`](evidence/container-networking-lab-report.pdf).
The Docker CLI was unavailable in the execution environment, so the PDF
transparently records that limitation alongside the source-level diagnosis and
an executed post-fix local health check.
