from flask import Flask, jsonify, render_template_string
import psutil
import redis
import json
import os

app = Flask(__name__)
cache = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=6379, decode_responses=True)

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>System Monitor</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: #0a0a0a; color: #f0f0f0; font-family: monospace; padding: 2rem; }
    h1 { font-size: 2rem; margin-bottom: 0.5rem; }
    h1 span { color: #00ff88; }
    p { color: #666; font-size: 0.85rem; margin-bottom: 2rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }
    .card { background: #111; border: 1px solid #222; border-radius: 8px; padding: 1.5rem; }
    .card.warning { border-color: #ffaa00; }
    .card.danger { border-color: #ff4444; }
    .card h2 { font-size: 0.75rem; color: #666; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 1rem; }
    .value { font-size: 2.5rem; font-weight: bold; color: #00ff88; }
    .value.warning { color: #ffaa00; }
    .value.danger { color: #ff4444; }
    .label { font-size: 0.75rem; color: #666; margin-top: 0.25rem; }
    .bar-container { background: #222; border-radius: 4px; height: 8px; margin-top: 1rem; }
    .bar { height: 100%; border-radius: 4px; background: #00ff88; transition: width 0.5s; }
    .bar.warning { background: #ffaa00; }
    .bar.danger { background: #ff4444; }
    .last-updated { font-size: 0.7rem; color: #444; text-align: right; margin-bottom: 1rem; }
    footer { border-top: 1px solid #222; padding-top: 1rem; font-size: 0.75rem; color: #444; text-align: center; margin-top: 2rem; }
  </style>
</head>
<body>
  <h1>System <span>Monitor</span></h1>
  <p>Live system metrics — updates every 3 seconds</p>
  <div class="last-updated" id="last-updated">Fetching data...</div>
  <div class="grid" id="metrics"></div>
  <footer>Built with Python · Flask · psutil · Docker</footer>
  <script>
    function getColor(value) {
      if (value >= 90) return "danger";
      if (value >= 70) return "warning";
      return "";
    }
    async function fetchMetrics() {
      try {
        const res = await fetch("/api/metrics");
        const data = await res.json();
        const grid = document.getElementById("metrics");
        grid.innerHTML = "";
        data.forEach(function(metric) {
          const color = getColor(metric.percent);
          const card = document.createElement("div");
          card.className = "card " + color;
          card.innerHTML =
            "<h2>" + metric.name + "</h2>" +
            "<div class='value " + color + "'>" + metric.value + "</div>" +
            "<div class='label'>" + metric.label + "</div>" +
            "<div class='bar-container'><div class='bar " + color + "' style='width:" + metric.percent + "%'></div></div>";
          grid.appendChild(card);
        });
        document.getElementById("last-updated").textContent = "Last updated: " + new Date().toLocaleTimeString();
      } catch(e) {
        console.error("Failed to fetch metrics");
      }
    }
    fetchMetrics();
    setInterval(fetchMetrics, 3000);
  </script>
</body>
</html>
''')

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/api/metrics')
def metrics():
    # Check cache first
    cached = cache.get('metrics')
    if cached:
        return jsonify(json.loads(cached))

    data = []

    # CPU Usage
    cpu_percent = psutil.cpu_percent(interval=1)
    data.append({
        'name': 'CPU Usage',
        'value': f'{cpu_percent}%',
        'label': f'{psutil.cpu_count()} cores',
        'percent': cpu_percent
    })

    # Memory
    mem = psutil.virtual_memory()
    data.append({
        'name': 'Memory Usage',
        'value': f'{mem.percent}%',
        'label': f'{round(mem.used / (1024**3), 1)}GB / {round(mem.total / (1024**3), 1)}GB',
        'percent': mem.percent
    })

    # Disk
    disk = psutil.disk_usage('/')
    data.append({
        'name': 'Disk Usage',
        'value': f'{disk.percent}%',
        'label': f'{round(disk.used / (1024**3), 1)}GB / {round(disk.total / (1024**3), 1)}GB',
        'percent': disk.percent
    })

    # CPU Temperature
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            for name, entries in temps.items():
                if entries:
                    temp = entries[0].current
                    data.append({
                        'name': 'CPU Temperature',
                        'value': f'{temp:.1f}°C',
                        'label': name,
                        'percent': min((temp / 100) * 100, 100)
                    })
                    break
        else:
            data.append({
                'name': 'CPU Temperature',
                'value': 'N/A',
                'label': 'Not available on Mac',
                'percent': 0
            })
    except Exception:
        data.append({
            'name': 'CPU Temperature',
            'value': 'N/A',
            'label': 'Not available on Mac',
            'percent': 0
        })

    # Cache for 2 seconds
    cache.setex('metrics', 2, json.dumps(data))

    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)