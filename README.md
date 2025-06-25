# Uptime Monitor Web App (Mini StatusPage)

Este proyecto implementa una solución de monitoreo de disponibilidad (Uptime Monitoring) construida con tecnologías modernas como Prometheus, Grafana y Kubernetes. Su objetivo es exponer visualmente el estado de una serie de URLs y generar alertas en caso de fallos.

---

## Tabla de Contenidos

- [Arquitectura](#arquitectura)
- [Requisitos](#requisitos)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Despliegue Local con Minikube](#despliegue-local-con-minikube)
- [Observabilidad](#observabilidad)
- [Alertas](#alertas)
- [Automatización y SRE](#automatización-y-sre)
- [Extensiones y Opciones Avanzadas](#extensiones-y-opciones-avanzadas)

---

## Arquitectura

El sistema consta de los siguientes componentes:

- **Aplicación Python (Flask)**: Realiza pruebas HTTP periódicas a URLs definidas y expone métricas en `/metrics`.
- **Prometheus**: Scrapea las métricas de la app cada 10 segundos.
- **Grafana**: Muestra un dashboard de estado con visualización de tiempos de respuesta y errores.
- **Alertmanager**: Dispara alertas cuando una URL falla, con opción de integración a Slack.
- **Kubernetes**: Orquesta el despliegue usando manifiestos y monitoreo personalizado.

---

## Requisitos

- Docker o Podman
- Minikube (o un cluster Kubernetes)
- kubectl
- Helm
- Python 3.9+
- Prometheus & Grafana

---

## Estructura del Proyecto

```bash
.
├── .github/workflows/deploy.yaml          # Pipeline CI/CD con GitHub Actions
├── app/                                   # Aplicación Flask que expone /status y /metrics
│   ├── main.py
│   ├── requirements.txt
│   └── urls.yaml
├── Dockerfile                             # Imagen para la aplicación Flask
├── k8s/                                   # Manifiestos Kubernetes
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── service-monitor.yaml
│   └── uptime-alert-rules.yaml
├── monitoring/grafana-dashboards/         # Dashboard JSON personalizado
│   └── uptime-dashboard.json
├── scripts/send_slack_alert.py            # Script para integración manual con Slack
└── uptime-monitor.tar                     # Imagen empaquetada para importar en Minikube
````

---

## Despliegue Local con Minikube

1. Iniciar Minikube:

   ```bash
   minikube start
   ```

2. Importar imagen:

   ```bash
   minikube cp uptime-monitor.tar /tmp/images/
   minikube ssh
   docker load -i /tmp/images/uptime-monitor.tar
   docker tag localhost/uptime-monitor:local uptime-monitor:local
   exit
   ```

3. Aplicar manifiestos:

   ```bash
   kubectl apply -f k8s/
   ```

4. Exponer el servicio:

   ```bash
   kubectl port-forward svc/uptime-service 8088:80
   ```

5. Acceder:

   * Aplicación: [http://localhost:8088/status](http://localhost:8088/status)
   * Métricas Prometheus: [http://localhost:8088/metrics](http://localhost:8088/metrics)

---

## Observabilidad

* Dashboard Grafana: importá `monitoring/grafana-dashboards/uptime-dashboard.json`.
* Datos visualizados:

  * Latencia por URL
  * Estado actual (UP/DOWN)
  * Historial de errores

---

## Alertas

* Reglas Prometheus:

  * Alertas si `uptime_check_failure_total` aumenta.
  * Archivo: `k8s/uptime-alert-rules.yaml`

* Alertmanager:

  * Integración vía webhook o Slack.
  * Ejemplo en `scripts/send_slack_alert.py`.

---

## Automatización y SRE

* GitHub Actions:

  * Pipeline de despliegue definido en `.github/workflows/deploy.yaml`.

* Terraform:

  * Opcional para desplegar en AWS con `terraform/`.

---

## Extensiones y Opciones Avanzadas

Este proyecto permite total libertad tecnológica. Algunas ideas:

* **Infraestructura**:

  * Usar Minikube, Kind, K3s o un cluster cloud (EKS, AKS, GKE).
* **CI/CD**:

  * GitHub Actions, Jenkins, GitLab CI, ArgoCD.
* **Monitoreo**:

  * Alternativas: Zabbix, Datadog, Uptime Kuma.
* **Alertas**:

  * Slack, Microsoft Teams, PagerDuty.

---

## Créditos

Desarrollado para fines educativos dentro de un entorno formativo de SRE.

---
