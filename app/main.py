from flask import Flask, jsonify, Response
import yaml
import time
import requests

from prometheus_client import Counter, Histogram, generate_latest

app = Flask(__name__)

# Prometheus metrics
success_counter = Counter("uptime_check_success_total", "Number of successful URL checks", ["url"])
failure_counter = Counter("uptime_check_failure_total", "Number of failed URL checks", ["url"])
latency_histogram = Histogram("uptime_check_duration_seconds", "Duration of URL checks", ["url"])

def load_urls():
    with open("app/urls.yaml", "r") as f:
        return yaml.safe_load(f)["urls"]

@app.route("/")
def index():
    return "Uptime Monitor Running"

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/status")
def status():
    urls = load_urls()
    results = []
    for url in urls:
        try:
            start = time.time()
            r = requests.get(url, timeout=5)
            duration = time.time() - start
            success_counter.labels(url=url).inc()
            latency_histogram.labels(url=url).observe(duration)
            results.append({"url": url, "status": r.status_code, "latency": round(duration, 2)})
        except:
            failure_counter.labels(url=url).inc()
            results.append({"url": url, "status": "DOWN", "latency": None})
    return jsonify(results)

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
