# Uptime Monitor Web App (Mini Status Page)

This project provides an uptime‑monitoring solution built with Flask, Prometheus, Grafana, and Kubernetes. It periodically checks configured URLs, exposes Prometheus‑style metrics, visualizes status in Grafana, and triggers alerts when failures occur.

## Table of Contents

- [Architecture](#architecture)  
- [Requirements](#requirements)  
- [Project Structure](#project-structure)  
- [Local Deployment (Minikube)](#local-deployment-minikube)  
- [Observability](#observability)  
- [Alerts](#alerts)  
- [Advanced Options](#advanced-options)  
- [License](LICENSE.md)  
- [Contributing](CONTRIBUTING.md)

---

## Architecture

-   **Flask App**: periodically checks a list of URLs defined in `urls.yaml`, exposes `/status` and `/metrics`.
-   **Prometheus**: scrapes `/metrics` every 10 s via a ServiceMonitor.
-   **Grafana**: visualizes metrics and latency.
-   **Alertmanager**: alerts on failed URL checks; e.g. integration with Slack.
-   **Kubernetes**: orchestrates deployment via `deployment.yaml`, `service.yaml`, etc.

---

## Requirements

-   Podman or Docker  
-   Minikube (or any Kubernetes cluster) - *Consider using the `--driver=qemu` for broad OS/CPU compatibility.*
-   kubectl  
-   Helm  
-   Python 3.9+  
-   Prometheus + Grafana via Helm chart  

---

## Project Structure

```

.
├── app
│   ├── main.py
│   ├── requirements.txt
│   └── urls.yaml
├── CONTRIBUTING.md
├── Dockerfile
├── k8s
│   ├── deployment.yaml
│   ├── service-monitor.yaml
│   ├── service.yaml
│   └── uptime-alert-rules.yaml
├── kubectl
├── LICENSE.md
├── monitoring
│   └── grafana-dashboards
│       └── uptime-dashboard.json
└── README.md

````

---

## Local Deployment (Minikube)

1.  **Start Minikube**:
    ```bash
    minikube start --driver=qemu # Recommended for broad OS/CPU compatibility
    ```
    *Note: Ensure virtualization (Intel VT-x/AMD-V) is enabled in your system's BIOS/UEFI settings.*

2.  **Set Docker environment to Minikube**:
    This command points your local `docker` CLI to Minikube's internal Docker daemon, allowing you to build images directly into the Minikube VM.
    ```bash
    eval $(minikube -p minikube docker-env)
    ```

3.  **Build your application container image**:
    After making changes to `app/main.py` or `Dockerfile`, rebuild the image. The `kubectl rollout restart` command in the next step will ensure the new image is used.
    ```bash
    docker build -t uptime-monitor:latest -f Dockerfile .
    ```

4.  **Deploy the monitoring stack (Prometheus, Grafana, Alertmanager) and your application's Kubernetes resources**:

    First, install the `kube-prometheus-stack` using Helm. This sets up Prometheus, Grafana, and Alertmanager. You'll need to specify a version that is compatible with your cluster.
    ```bash
    helm upgrade --install prometheus-stack prometheus-community/kube-prometheus-stack \
      --namespace monitoring --create-namespace \
      --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesPods=false \
      --version <LATEST_STABLE_VERSION_HERE> # e.g., 58.1.0 from Artifact Hub
    ```
    *Wait for the monitoring components to be ready before proceeding to ensure smooth operation.*

    Then, apply your application's specific Kubernetes manifests (Deployment, Service, ServiceMonitor, AlertRules).
    ```bash
    kubectl apply -f k8s/
    ```

    *If you update your application's image (e.g., after `docker build`):*
    ```bash
    kubectl rollout restart deployment/uptime-monitor
    ```

5.  **Port-forward services for local access**:
    Run these commands in **separate terminal windows** or in the background (`&`) to access the UIs. Remember to get the correct pod name for the application.

    * **Uptime Monitor App (Metrics & Status):**
        ```bash
        # Get the current pod name (it changes on redeployment)
        POD_NAME=$(kubectl get pods -l app=uptime-monitor -o jsonpath='{.items[0].metadata.name}')
        kubectl port-forward $POD_NAME 8000:5000 & # Forward local 8000 to container's 5000
        ```
    * **Prometheus UI:**
        ```bash
        kubectl --namespace monitoring port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090 &
        ```
    * **Grafana UI:**
        ```bash
        kubectl --namespace monitoring port-forward svc/prometheus-grafana 3000:80 &
        ```
    * **Alertmanager UI:**
        ```bash
        kubectl --namespace monitoring port-forward svc/prometheus-kube-prometheus-alertmanager 9093:9093 &
        ```

6.  **Access (URLs once port-forwarded):**

    * **Uptime Monitor App:**
        * App Status (JSON): `http://localhost:8000/status`
        * Prometheus Metrics: `http://localhost:8000/metrics`
    * **Prometheus UI:** `http://localhost:9090`
    * **Grafana UI:** `http://localhost:3000` (Default login usually `admin`/`prom-operator` or `admin`/`admin`. Check `kubectl get secret prometheus-stack-grafana -n monitoring -o jsonpath='{.data.admin-password}' | base64 --decode` if default password is unknown.)
    * **Alertmanager UI:** `http://localhost:9093`

---

## Observability

* Import `monitoring/grafana-dashboards/uptime-dashboard.json` into Grafana.
    * Navigate to your Grafana UI (`http://localhost:3000`).
    * Go to **Dashboards** > **New Dashboard** > **Import**.
    * Click **"Upload JSON file"** and select `monitoring/grafana-dashboards/uptime-dashboard.json` from your project directory.
    * Ensure you select `Prometheus` as the data source when prompted.
    * *Crucially, set the dashboard's time range (top right) to "Last 5 minutes" or "Last 15 minutes" to see recent data, as your application might have just started collecting metrics.*
* Visualizes:
    * URL latencies
    * Failure counters
    * Success rates

---

## Alerts

* Defined in `k8s/uptime-alert-rules.yaml`:
    * Trigger: `increase(uptime_check_failure_total[1m]) > 0`
* Alertmanager configuration (e.g., Slack webhook) can be added via Kubernetes Secret.
* **To test alerts manually:**
    * Ensure Alertmanager is port-forwarded (`http://localhost:9093`).
    * Run the following `curl` command (all on one line) to send a test alert. This alert will automatically expire after 5 minutes due to `endsAt`.
        ```bash
        curl -X POST -H "Content-Type: application/json" --data '[ { "labels": { "alertname": "ManualTestAlert", "severity": "critical", "instance": "manual-alert-source", "job": "test-job" }, "annotations": { "summary": "This is a manually generated test alert.", "description": "This alert was generated to test Alertmanager\'s functionality." }, "generatorURL": "[http://example.com/manual-alert](http://example.com/manual-alert)", "startsAt": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")", "endsAt": "$(date -u -d "+5 minutes" +"%Y-%m-%dT%H:%M:%SZ")" } ]' http://localhost:9093/api/v2/alerts
        ```
    * Verify the alert appears in the Alertmanager UI at `http://localhost:9093`.

---

## Advanced Options

You’re free to swap components as you wish:

* **Kubernetes environment**: Minikube, Kind, GKE, EKS, AKS, IBM Cloud.
* **App tech**: Flask, FastAPI, Node.js, Go, Ruby.
* **IaC**: Terraform, Pulumi, Ansible.
* **Alert endpoints**: Slack, Email, Discord, PagerDuty.
* **CI/CD**: GitHub Actions, Jenkins, GitLab CI, ArgoCD.

---

## Notes

-   This repository is part of a practical training series developed for the SRE Academy.
-   It is optimized for environments like Minikube but can be adapted to other Kubernetes setups.
-   Contributions and improvements are welcome. If you encounter issues or have suggestions, please open a pull request or GitHub issue.

Happy learning and implementing SRE best practices!

![Observability](https://img.shields.io/badge/Observability-Grafana%20%7C%20Prometheus-orange)
![Kubernetes](https://img.shields.io/badge/Platform-Kubernetes-informational)

---