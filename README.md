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
