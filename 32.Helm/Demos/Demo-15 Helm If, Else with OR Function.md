# 🎯 **Demo-15: Helm If, Else with OR Function**

In this demo, you’ll learn how to use the **`or`** function to handle *either/or* conditions —
useful when you want to deploy a resource if **any one** of several conditions is true.

---

## 🧩 **Objective**

You’ll learn how to:

* Use the `or` function in Helm templates
* Combine it with `if` and `else`
* Create flexible deployment logic for multiple environments
* Print conditional messages for debugging

---

## 📁 **Project Structure**

```
demo-15-or-function/
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

## 🪜 Step 1 — Create Chart

```bash
mkdir demo-15-or-function
cd demo-15-or-function
helm create webchart
rm -rf webchart/templates/*
```

---

## 🧾 Step 2 — Chart.yaml

```yaml
apiVersion: v2
name: webchart
description: Helm demo for If/Else with OR Function
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
replicaCount: 1

# Environment
env: "dev"

# Feature flags
enableDeployment: false
enableService: true
enableDevMode: true
enableLogging: false

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

## 🧱 Step 5 — Deployment Template (with OR logic)

### **templates/deployment.yaml**

```gotemplate
{{- if or .Values.enableDeployment (eq .Values.env "dev") }}
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
          {{- if or .Values.enableDevMode .Values.enableLogging }}
            - name: MODE
              value: "DEBUG"
          {{- else }}
            - name: MODE
              value: "NORMAL"
          {{- end }}
{{- else }}
# Deployment not created because both conditions are false.
{{- end }}
```

---

### 🧠 **Explanation:**

| Condition                                                             | Meaning                                                                              |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `or .Values.enableDeployment (eq .Values.env "dev")`                  | Deployment is created if *either* deployment is enabled **OR** environment is `dev`. |
| Nested condition: `if or .Values.enableDevMode .Values.enableLogging` | Enables DEBUG mode if **either** flag is true.                                       |

---

## ⚙️ Step 6 — Service Template

### **templates/service.yaml**

```gotemplate
{{- if or .Values.enableService (eq .Values.env "prod") }}
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
# Service creation skipped
{{- end }}
```

---

## 🧾 Step 7 — ConfigMap Template (to print logic result)

### **templates/configmap.yaml**

```gotemplate
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "webchart.fullname" . }}-config
data:
  message: |
    {{- if or .Values.enableDeployment (eq .Values.env "dev") -}}
    Deployment is enabled (because enableDeployment=true or env=dev)
    {{- else -}}
    Deployment disabled (neither flag true)
    {{- end }}
  mode: |
    {{- if or .Values.enableDevMode .Values.enableLogging -}}
    Debug Mode Active
    {{- else -}}
    Normal Mode
    {{- end }}
```

---

## 📘 Step 8 — README.md

````markdown
# Demo-15: Helm If, Else with OR Function

This demo shows how Helm's `or` function works:
- If **any one** condition is true, the block executes.
- It’s useful when you want fallback logic like:
  “Deploy in dev OR when feature flag is enabled.”

## Commands

Render templates:
```bash
helm template demo ./webchart
````

Install:

```bash
helm install demo ./webchart -n demo15 --create-namespace
```

Test other cases:

```bash
helm upgrade demo ./webchart -n demo15 --set enableDeployment=true
helm upgrade demo ./webchart -n demo15 --set env=prod
helm upgrade demo ./webchart -n demo15 --set enableDevMode=false --set enableLogging=true
```

````

---

## 💻 Step 9 — commands.sh

```bash
#!/usr/bin/env bash
set -euo pipefail

RELEASE="or-demo"
NAMESPACE="demo15"

echo "Linting chart..."
helm lint webchart

echo "Rendering templates..."
helm template $RELEASE ./webchart -n $NAMESPACE > rendered.yaml

echo "Installing chart..."
helm install $RELEASE ./webchart -n $NAMESPACE --create-namespace

echo "Checking resources..."
kubectl get all -n $NAMESPACE

echo "Updating values to test OR conditions..."
helm upgrade $RELEASE ./webchart -n $NAMESPACE --set enableDeployment=true
helm upgrade $RELEASE ./webchart -n $NAMESPACE --set env=prod
helm upgrade $RELEASE ./webchart -n $NAMESPACE --set enableDevMode=false --set enableLogging=true

echo "Cleanup..."
helm uninstall $RELEASE -n $NAMESPACE
kubectl delete namespace $NAMESPACE
````

---

## 🧠 **Test Scenarios**

| Scenario                            | Values                           | Expected Result                      |
| ----------------------------------- | -------------------------------- | ------------------------------------ |
| Default                             | enableDeployment=false, env=dev  | Deployment created (because env=dev) |
| Both False                          | enableDeployment=false, env=prod | Deployment skipped                   |
| One True                            | enableDeployment=true            | Deployment created                   |
| enableDevMode OR enableLogging true | MODE=DEBUG                       |                                      |
| Both False                          | MODE=NORMAL                      |                                      |

---

## 🧩 Key Takeaways

| Function             | Description                       | Example                                         |
| -------------------- | --------------------------------- | ----------------------------------------------- |
| `or`                 | True if **any** condition is true | `{{ if or A B }}`                               |
| Combine `and` + `or` | For complex logic                 | `{{ if and (or A B) C }}`                       |
| Typical use          | Enable fallback configs           | e.g. enable feature in `dev` OR `staging`       |
| Readability          | Use parentheses for clarity       | `{{ if or (eq env "dev") (eq env "staging") }}` |

---

## 🧹 Cleanup

```bash
helm uninstall demo -n demo15
kubectl delete namespace demo15
```

---

