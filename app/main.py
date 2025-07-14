from flask import Flask, jsonify, Response
import yaml
import time
import requests
from prometheus_client import Counter, Histogram, generate_latest
from threading import Thread
import os

app = Flask(__name__)

# Prometheus metrics
success_counter = Counter("uptime_check_success_total", "Number of successful URL checks", ["url"])
failure_counter = Counter("uptime_check_failure_total", "Number of failed URL checks", ["url"])
latency_histogram = Histogram("uptime_check_duration_seconds", "Duration of URL checks", ["url"])

# Load URLs from YAML - This function definition remains the same
def load_urls_from_file():
    config_path = os.path.join(os.path.dirname(__file__), "urls.yaml")
    try:
        with open(config_path, "r") as f:
            loaded_urls = yaml.safe_load(f).get("urls", [])
            print(f"Loaded URLs from {config_path}: {loaded_urls}") # Add print for confirmation
            return loaded_urls
    except FileNotFoundError:
        print(f"Error: {config_path} not found. Please ensure urls.yaml is in the 'app' directory.")
        return []
    except Exception as e:
        print(f"Error loading urls.yaml: {e}")
        return []

# --- IMPORTANT CHANGE START ---

# Load the URLs once when the application module is imported (by Gunicorn)
MONITOR_URLS = load_urls_from_file()

# Background checker - This function definition remains the same
def background_uptime_check():
    while True:
        if not MONITOR_URLS:
            print("No URLs to monitor. Sleeping...")
            time.sleep(30)
            # You might want to try reloading URLs here if you expect them to appear dynamically
            # For now, let's assume they are loaded once.
            continue

        for url_string in MONITOR_URLS:
            try:
                start = time.time()
                r = requests.get(url_string, timeout=5)
                duration = time.time() - start
                success_counter.labels(url=url_string).inc()
                latency_histogram.labels(url=url_string).observe(duration)
                print(f"Checked {url_string}: UP (status: {r.status_code}, latency: {duration:.2f}s)")
            except Exception as e:
                print(f"Error checking {url_string}: {e}")
                failure_counter.labels(url=url_string).inc()
                print(f"Checked {url_string}: DOWN (error: {e})")
        time.sleep(30)

# Start the background thread when the application module is imported (by Gunicorn)
# This thread will run alongside the Gunicorn workers
uptime_checker_thread = Thread(target=background_uptime_check, daemon=True)
uptime_checker_thread.start()

# --- IMPORTANT CHANGE END ---


# Routes (remain unchanged)
@app.route("/")
def index():
    return "Uptime Monitor Running"

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/status")
def status():
    results = []
    if not MONITOR_URLS:
        return jsonify({"message": "No URLs configured for monitoring."})

    for url_string in MONITOR_URLS:
        try:
            start = time.time()
            r = requests.get(url_string, timeout=5)
            duration = time.time() - start
            success_counter.labels(url=url_string).inc()
            latency_histogram.labels(url=url_string).observe(duration)
            results.append({"url": url_string, "status": r.status_code, "latency": round(duration, 2)})
        except Exception as e:
            print(f"Error checking {url_string} for status endpoint: {e}")
            failure_counter.labels(url=url_string).inc()
            results.append({"url": url_string, "status": "DOWN", "latency": None})
    return jsonify(results)

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype="text/plain")

# The if __name__ == "__main__": block is now only for direct script execution (e.g., python main.py)
# and is not needed for Gunicorn, but it's good practice to keep it for local development.
if __name__ == "__main__":
    # If running directly, the thread is already started above, so no need to start again
    # app.run() will be started here for local development.
    print("Running Flask app in development mode.")
    app.run(host="0.0.0.0", port=5000, debug=True) # debug=True for local development