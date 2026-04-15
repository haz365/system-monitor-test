# System Monitor

A real-time system monitoring dashboard built with Python, Flask, Redis and Docker. Displays live CPU, memory and disk metrics that update every 3 seconds via a clean web dashboard.

---

## Overview

This application collects live system metrics using psutil and serves them through a Flask API. Metrics are cached in Redis for 2 seconds to reduce CPU overhead. The frontend dashboard polls the API every 3 seconds and displays the data with colour coded indicators — green for normal, amber for high, red for critical.

---

## Stack

- **Python + Flask** — web server and API
- **psutil** — system metrics collection
- **Redis** — caching layer to reduce overhead
- **Docker + Docker Compose** — containerisation and orchestration

---

## Metrics

- CPU usage and core count
- Memory usage with used/total breakdown
- Disk usage with used/total breakdown
- CPU temperature (where available)

Colour coding:
- Green — below 70%
- Amber — 70% to 90%
- Red — above 90%

---

## Running locally

Make sure Docker Desktop is running, then:

```bash
git clone https://github.com/haz365/system-monitor-test.git
cd system-monitor-test
docker-compose up --build
```

Visit `http://localhost:5000`

To stop:
```bash
docker-compose down
```

---

## Architecture
Browser → Flask App (port 5000) → Redis Cache → psutil
The Flask app receives requests from the browser. Before collecting metrics it checks Redis for a cached response. If cached data exists it returns immediately. If not it collects fresh metrics using psutil, stores them in Redis for 2 seconds, then returns the data.

---

## Project Structure

| File | Description |
|---|---|
| `app.py` | Flask app and metrics collection |
| `requirements.txt` | Python dependencies |
| `Dockerfile` | Container definition |
| `docker-compose.yml` | Orchestrates app and Redis |
| `.dockerignore` | Excludes unnecessary files |

## Docker Optimisation

The Docker image was reduced from **237MB to 112MB** using two techniques:

### 1. Alpine base image
Instead of the standard Python image which is based on Debian, the app uses `python:3.11-alpine` — a minimal Linux distribution that is only 5MB compared to Debian's 100MB+.

### 2. Multi-stage build
The build process is split into two stages:

```dockerfile
# Stage 1 — install dependencies
FROM python:3.11-alpine AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2 — final image
FROM python:3.11-alpine
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .
```

Stage 1 installs all the dependencies. Stage 2 starts completely fresh and only copies the installed packages across — not the build tools, pip cache, or anything else used during installation. This keeps the final image as lean as possible.

### Result

| Version | Image size |
|---|---|
| Before (python:3.11-slim) | 237MB |
| After (alpine + multi-stage) | 112MB |
| Compressed (Docker Hub) | 26MB |