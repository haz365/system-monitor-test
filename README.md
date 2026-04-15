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
Browser
│
▼
Flask App (port 5000)
│
├── GET /          → serves dashboard
├── GET /health    → health check
└── GET /api/metrics
│
├── check Redis cache
│     └── if cached → return immediately
└── if not cached
├── collect metrics with psutil
├── store in Redis for 2 seconds
└── return metrics

---

## Project Structure
system-monitor/
├── app.py              # Flask app and metrics collection
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container definition
├── docker-compose.yml  # Orchestrates app and Redis
└── .dockerignore       # Excludes unnecessary files
