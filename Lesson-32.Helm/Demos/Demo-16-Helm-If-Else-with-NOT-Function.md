# 🎯 **Demo-16: Helm If, Else with NOT Function**

The `not` function is used when you want to execute something **only if a condition is false**.
This helps make your Helm charts smarter and prevents deploying unwanted resources.

---

## 🧩 **Objective**

You’ll learn:

* How to use the `not` function in Helm
* Combine `not` with `if`, `else`, and `eq`
* Write conditions that deploy resources *only when disabled flags are false*
* Use it in templates like Deployment and ConfigMap

---

## 📁 **Project Structure**

```
demo-16-not-function/
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

## 🪜 Step 1 — Create Helm Chart

```bash
mkdir demo-16-not-function
cd demo-16-not-function
helm create webchart
rm -rf webchart/templates/*
```

---

## 📘 Step 2 — Chart.yaml

```yaml
apiVersion: v2
name: webchart
description: Helm demo for If/Else with NOT Function
type: application
version: 0.1.0
appVersion: "1.0.0"
maintainers:
  - name: Deepak Yadav
    email: deepak@example.com
```

---

## ⚙️ Step 3 — values.yaml

```yaml
replicaCount: 2

# Environment
env: "prod"

# Feature flags
enableDeployment: true
enableMonitoring: false
maintenanceMode: false

image:
  repository: nginx
  tag: "1.25.3"
  pullPolicy: IfNotPresent

service:
  type: NodePort
  port: 80
```

---

## 🧠 Step 4 — _helpers.tpl

```gotemplate
{{- define "webchart.fullname" -}}
{{ printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end -}}
```

---

## 🧱 Step 5 — templates/deployment.yaml

This template demonstrates the **`not`** and **`eq`** functions in action.

```gotemplate
{{- if and (not .Values.maintenanceMode) .Values.enableDeployment }}
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
          env:
            - name: ENVIRONMENT
              value: {{ .Values.env | quote }}
            - name: STATUS
              value: "Running Normally"
{{- else }}
# Deployment skipped because maintenanceMode=true or enableDeployment=false
{{- end }}
```

---

### 🧠 Explanation:

| Function | Description                  | Example                                                                              |
| -------- | ---------------------------- | ------------------------------------------------------------------------------------ |
| `not`    | Inverts a condition          | `not .Values.maintenanceMode` returns `true` if maintenanceMode=false                |
| `and`    | Combines multiple conditions | `and (not .Values.maintenanceMode) .Values.enableDeployment` means both must be true |
| `eq`     | Compares values              | `eq .Values.env "prod"` returns true if env=prod                                     |

✅ Deployment will be created only when:

* `maintenanceMode` is **false**
* `enableDeployment` is **true**

---

## ⚙️ Step 6 — templates/service.yaml

```gotemplate
{{- if not .Values.maintenanceMode }}
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
# Service disabled due to maintenance mode
{{- end }}
```

🧠 **Logic:**
If maintenance mode is ON → Service won’t be deployed.

---

## 🧾 Step 7 — templates/configmap.yaml

```gotemplate
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "webchart.fullname" . }}-config
data:
  environment: {{ .Values.env | quote }}
  maintenanceStatus: |
    {{- if .Values.maintenanceMode }}
    The application is currently in maintenance mode.
    {{- else }}
    Application is fully operational.
    {{- end }}
  monitoring: |
    {{- if not .Values.enableMonitoring }}
    Monitoring is disabled.
    {{- else }}
    Monitoring is enabled.
    {{- end }}
```

🧠 **Logic Used:**

* `if .Values.maintenanceMode` — checks if maintenance is ON.
* `if not .Values.enableMonitoring` — prints opposite message if monitoring is false.

---

## 📘 Step 8 — README.md

````markdown
# Demo-16: Helm If, Else with NOT Function

This demo shows how to use Helm’s `not` function for inverse logic.

## Concepts
- `not` reverses any Boolean or comparison result.
- Combine with `if`, `and`, or `or` for complex logic.
- Useful for “disable features” or “maintenance mode” conditions.

## Commands

Render templates:
```bash
helm template demo ./webchart
````

Install:

```bash
helm install demo ./webchart -n demo16 --create-namespace
```

Change values to see effect:

```bash
helm upgrade demo ./webchart -n demo16 --set maintenanceMode=true
helm upgrade demo ./webchart -n demo16 --set enableMonitoring=true
helm upgrade demo ./webchart -n demo16 --set enableDeployment=false
```

````

---

## 💻 Step 9 — commands.sh

```bash
#!/usr/bin/env bash
set -euo pipefail

RELEASE="not-demo"
NAMESPACE="demo16"

echo "Linting chart..."
helm lint webchart

echo "Rendering templates..."
helm template $RELEASE ./webchart -n $NAMESPACE > rendered.yaml

echo "Installing chart..."
helm install $RELEASE ./webchart -n $NAMESPACE --create-namespace

echo "Check deployment..."
kubectl get all -n $NAMESPACE

echo "Simulate maintenance mode..."
helm upgrade $RELEASE ./webchart -n $NAMESPACE --set maintenanceMode=true

echo "Enable monitoring..."
helm upgrade $RELEASE ./webchart -n $NAMESPACE --set enableMonitoring=true

echo "Disable deployment..."
helm upgrade $RELEASE ./webchart -n $NAMESPACE --set enableDeployment=false

echo "Cleanup..."
helm uninstall $RELEASE -n $NAMESPACE
kubectl delete namespace $NAMESPACE
````

---

## 🧠 Test Scenarios

| Scenario               | Values                                       | Expected Result              |
| ---------------------- | -------------------------------------------- | ---------------------------- |
| Default                | maintenanceMode=false, enableDeployment=true | Deployment + Service created |
| maintenanceMode=true   | Service + Deployment skipped                 |                              |
| enableDeployment=false | Deployment skipped                           |                              |
| enableMonitoring=false | ConfigMap prints "Monitoring disabled"       |                              |
| enableMonitoring=true  | ConfigMap prints "Monitoring enabled"        |                              |

---

## 🧩 Key Takeaways

| Function         | Description                                                          | Example               |
| ---------------- | -------------------------------------------------------------------- | --------------------- |
| `not`            | Inverts the value of a condition                                     | `not .Values.enabled` |
| `and`            | All conditions must be true                                          | `and A B`             |
| `or`             | Any one condition true                                               | `or A B`              |
| `eq`             | Check equality                                                       | `eq A "value"`        |
| Combined example | `{{ if and (not .Values.maintenanceMode) (eq .Values.env "prod") }}` |                       |

---

## 🧹 Cleanup

```bash
helm uninstall demo -n demo16
kubectl delete namespace demo16
```

---

✅ **Result:**
After completing this demo, you’ll understand how to:

* Use `not` for negation logic
* Build smarter conditional flows
* Prevent unwanted deployments during maintenance or testing

---
