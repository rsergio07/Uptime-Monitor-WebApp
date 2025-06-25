# Uptime Monitor Web App (Mini Status Page)

This project provides an uptime‑monitoring solution built with Flask, Prometheus, Grafana, and Kubernetes. It periodically checks configured URLs, exposes Prometheus‑style metrics, visualizes status in Grafana, and triggers alerts when failures occur.

## Table of Contents

- [Architecture](#architecture)  
- [Requirements](#requirements)  
- [Project Structure](#project-structure)  
- [Local Deployment (Minikube)](#local-deployment-minikube)  
- [Observability](#observability)  
- [Alerts](#alerts)  
- [Automation & SRE](#automation--sre)  
- [Advanced Options](#advanced-options)  

---

## Architecture

- **Flask App**: periodically checks a list of URLs defined in `urls.yaml`, exposes `/status` and `/metrics`.
- **Prometheus**: scrapes `/metrics` every 10 s via a ServiceMonitor.
- **Grafana**: visualizes metrics and latency.
- **Alertmanager**: alerts on failed URL checks; e.g. integration with Slack.
- **Kubernetes**: orchestrates deployment via `deployment.yaml`, `service.yaml`, etc.

---

## Requirements

- Podman or Docker  
- Minikube (or any Kubernetes cluster)  
- kubectl  
- Helm  
- Python 3.9+  
- Prometheus + Grafana via Helm chart  

---

## Project Structure

```

.
├── .github/workflows/deploy.yaml
├── app/
│   ├── main.py
│   ├── requirements.txt
│   └── urls.yaml
├── Dockerfile
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── service-monitor.yaml
│   └── uptime-alert-rules.yaml
├── monitoring/
│   └── grafana-dashboards/
│       └── uptime-dashboard.json
├── scripts/
│   └── send\_slack\_alert.py
├── README.md
├── CONTRIBUTING.md
└── LICENSE

````

---

## Local Deployment (Minikube)

1. Start Minikube:
   ```bash
   minikube start
````

2. Load container image:

   ```bash
   minikube cp uptime-monitor.tar /tmp/images/
   minikube ssh
     docker load -i /tmp/images/uptime-monitor.tar
     docker tag localhost/uptime-monitor:local uptime-monitor:local
     exit
   ```
3. Apply Kubernetes manifests:

   ```bash
   kubectl apply -f k8s/
   ```
4. Port‑forward the service:

   ```bash
   kubectl port-forward svc/uptime-service 8088:80
   ```
5. Access:

   * App JSON: `http://localhost:8088/status`
   * Prometheus metrics: `http://localhost:8088/metrics`

---

## Observability

* Import `monitoring/grafana-dashboards/uptime-dashboard.json` into Grafana.
* Visualizes:

  * URL latencies
  * Failure counters
  * Success rates

---

## Alerts

* Defined in `k8s/uptime-alert-rules.yaml`:

  * Trigger: `increase(uptime_check_failure_total[1m]) > 0`.
* Alertmanager configuration (e.g. Slack webhook) can be added via Kubernetes Secret.

---

## Automation & SRE

* GitHub Actions workflow defined in `.github/workflows/deploy.yaml`.
* Optional Terraform under `terraform/` to provision AWS/EKS cluster.

---

## Advanced Options

You’re free to swap components as you wish:

* **Kubernetes environment**: Minikube, Kind, GKE, EKS, AKS, IBM Cloud.
* **App tech**: Flask, FastAPI, Node.js, Go, Ruby.
* **IaC**: Terraform, Pulumi, Ansible.
* **Alert endpoints**: Slack, Email, Discord, PagerDuty.
* **CI/CD**: GitHub Actions, Jenkins, GitLab CI, ArgoCD.

---
