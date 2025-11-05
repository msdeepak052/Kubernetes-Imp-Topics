# **Demo-14: Helm If/Else with Boolean Check and AND Function**


This demo builds directly on Demo-13 — we’ll make a new chart that decides how and when to deploy resources based on *multiple boolean values*.

---

## 🎯 **Objective**

You’ll learn to:

* Use boolean values (`true` / `false`) in Helm
* Combine multiple conditions with `and`, `or`, and `not`
* Create complex logic for environment-specific deployments
* Cleanly structure conditions for readability

---

## 📁 **Project Structure**

```
demo-14-boolean-and/
└── webchart/
    ├── Chart.yaml
    ├── values.yaml
    ├── templates/
    │   ├── deployment.yaml
    │   ├── service.yaml
    │   ├── configmap.yaml
    │   └── _helpers.tpl
    ├── README.md
    └── commands.sh
```

---

## 🪜 **Step-by-Step Implementation**

### Step 1 — Create the chart

```bash
mkdir demo-14-boolean-and
cd demo-14-boolean-and
helm create webchart
```

Then delete the default templates (`rm -rf webchart/templates/*`) — we’ll recreate them.

---

## Step 2 — Define the Chart Metadata

### **Chart.yaml**

```yaml
apiVersion: v2
name: webchart
description: Helm demo for If/Else with Boolean and AND function
type: application
version: 0.1.0
appVersion: "1.0.0"
maintainers:
  - name: Deepak Yadav
    email: deepak@example.com
```

---

## Step 3 — Define Variables

### **values.yaml**

```yaml
replicaCount: 1

# Toggle to enable/disable deployment
enableDeployment: true

# Toggle to enable/disable service
enableService: true

# Additional feature flag for logging
enableLogging: true

# Combine with environment for AND/OR conditions
env: "prod"

image:
  repository: "nginx"
  tag: "1.25.3"
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80
```

---

## Step 4 — Helpers File

### **templates/_helpers.tpl**

```yaml
{{- define "webchart.fullname" -}}
{{ printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end -}}
```

---

## Step 5 — Deployment Template

### **templates/deployment.yaml**

```yaml
{{- if and .Values.enableDeployment (eq .Values.env "prod") }}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "webchart.fullname" . }}
  labels:
    app: {{ include "webchart.fullname" . }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ include "webchart.fullname" . }}
  template:
    metadata:
      labels:
        app: {{ include "webchart.fullname" . }}
    spec:
      containers:
        - name: nginx
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - containerPort: 80
          {{- if .Values.enableLogging }}
          env:
            - name: LOG_LEVEL
              value: "debug"
          {{- else }}
          env:
            - name: LOG_LEVEL
              value: "error"
          {{- end }}
{{- else }}
# Deployment disabled — either enableDeployment=false or env != prod
{{- end }}
```

### 🔍 Explanation:

| Logic                                                  | Meaning                                            |
| ------------------------------------------------------ | -------------------------------------------------- |
| `and .Values.enableDeployment (eq .Values.env "prod")` | Render Deployment only if both are true            |
| `if .Values.enableLogging`                             | Add different env variable based on logging flag   |
| `{{- else }}`                                          | Acts as a fallback comment when conditions not met |

---

## Step 6 — Service Template

### **templates/service.yaml**

```yaml
{{- if and .Values.enableService .Values.enableDeployment }}
apiVersion: v1
kind: Service
metadata:
  name: {{ include "webchart.fullname" . }}-svc
spec:
  type: {{ .Values.service.type }}
  selector:
    app: {{ include "webchart.fullname" . }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: 80
{{- else }}
# Service creation skipped (either enableService=false or enableDeployment=false)
{{- end }}
```

---

## Step 7 — ConfigMap Template

### **templates/configmap.yaml**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "webchart.fullname" . }}-config
data:
  environment: {{ .Values.env | quote }}
  deployment_status: |
    {{- if and .Values.enableDeployment (eq .Values.env "prod") -}}
    Deployment enabled in Production
    {{- else -}}
    Deployment disabled or not Production
    {{- end }}
  service_status: |
    {{- if .Values.enableService -}}
    Service is enabled
    {{- else -}}
    Service is disabled
    {{- end }}
```

---

## Step 8 — README.md

````markdown
# Demo-14: Helm If, Else with Boolean Check and AND Function

This chart shows how to:
- Use boolean values (`true` / `false`)
- Combine conditions using `and`, `or`, and `not`
- Render or skip Kubernetes resources dynamically

## Commands

Render templates:
```bash
helm template demo ./webchart
````

Install:

```bash
helm install demo ./webchart -n demo14 --create-namespace
```

Change values:

```bash
helm upgrade demo ./webchart -n demo14 --set enableDeployment=false
helm upgrade demo ./webchart -n demo14 --set env=dev
helm upgrade demo ./webchart -n demo14 --set enableLogging=false
```

````

---

## Step 9 — commands.sh

```bash
#!/usr/bin/env bash
set -euo pipefail

RELEASE="boolean-demo"
NAMESPACE="demo14"

echo "Linting chart..."
helm lint webchart

echo "Rendering manifests..."
helm template $RELEASE ./webchart -n $NAMESPACE > rendered.yaml

kubectl create namespace $NAMESPACE || true

echo "Installing chart..."
helm install $RELEASE ./webchart -n $NAMESPACE --wait

echo "Check Deployment and Service..."
kubectl get all -n $NAMESPACE

echo "Disable deployment and upgrade..."
helm upgrade $RELEASE ./webchart -n $NAMESPACE --set enableDeployment=false

echo "Set environment to dev..."
helm upgrade $RELEASE ./webchart -n $NAMESPACE --set env=dev

echo "Disable logging..."
helm upgrade $RELEASE ./webchart -n $NAMESPACE --set enableLogging=false

echo "Cleanup..."
helm uninstall $RELEASE -n $NAMESPACE
kubectl delete namespace $NAMESPACE
````

---

## 🧩 Step 10 — Try Out Scenarios

| Scenario           | Values                          | Expected                                    |
| ------------------ | ------------------------------- | ------------------------------------------- |
| Default            | enableDeployment=true, env=prod | Deployment + Service created                |
| Disable Deployment | enableDeployment=false          | Deployment skipped, only ConfigMap rendered |
| Dev Env            | env=dev                         | Deployment skipped (since env != prod)      |
| Logging Off        | enableLogging=false             | LOG_LEVEL=error in container                |
| Disable Service    | enableService=false             | Service YAML not rendered                   |

---

## 🧠 Key Learnings

| Function | Description                       | Example                              |
| -------- | --------------------------------- | ------------------------------------ |
| `if`     | Conditional start                 | `{{ if .Values.enableService }}`     |
| `and`    | True only if both conditions true | `{{ if and A B }}`                   |
| `or`     | True if either condition true     | `{{ if or A B }}`                    |
| `not`    | Negates boolean                   | `{{ if not .Values.enableLogging }}` |
| `eq`     | Compares equality                 | `{{ if eq .Values.env "prod" }}`     |

---

## 🧹 Cleanup

```bash
helm uninstall demo -n demo14
kubectl delete namespace demo14
```

---
