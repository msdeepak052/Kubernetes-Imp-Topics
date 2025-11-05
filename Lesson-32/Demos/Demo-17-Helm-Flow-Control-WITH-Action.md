# 🎯 **Demo-17: Helm Flow Control — `with` Action**

---

## 🧩 **Objective**

In this demo, you’ll learn:

* What the **`with`** action does
* How to use `.` (the dot) context inside `with`
* How to reference values cleanly within nested objects
* When to use `with` vs direct access (`.Values.something`)

---

## 🧱 **Concept Overview**

Normally, you reference values like this:

```gotemplate
{{ .Values.image.repository }}
```

If you are using the same nested object repeatedly (like `.Values.image.repository`, `.Values.image.tag`, `.Values.image.pullPolicy`),
you can use **`with`** to *simplify* it:

```gotemplate
{{- with .Values.image }}
image: "{{ .repository }}:{{ .tag }}"
imagePullPolicy: {{ .pullPolicy }}
{{- end }}
```

Inside a `with` block, the `.` (dot) context changes — it now refers to **the value of `.Values.image`**.

---

## 📁 **Project Structure**

```
demo-17-with-action/
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

## 🪜 Step 1 — Create the Chart

```bash
mkdir demo-17-with-action
cd demo-17-with-action
helm create webchart
rm -rf webchart/templates/*
```

---

## 📘 Step 2 — Chart.yaml

```yaml
apiVersion: v2
name: webchart
description: Helm demo for Flow Control WITH Action
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

image:
  repository: nginx
  tag: "1.25.3"
  pullPolicy: IfNotPresent

service:
  type: NodePort
  port: 80

config:
  appName: "Deepak WebApp"
  maintainer: "Deepak Yadav"
  features:
    - Login
    - Dashboard
    - Reports
```

---

## 🧠 Step 4 — _helpers.tpl

```gotemplate
{{- define "webchart.fullname" -}}
{{ printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end -}}
```

---

## 🧾 Step 5 — templates/deployment.yaml

```gotemplate
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
          {{- with .Values.image }}
          image: "{{ .repository }}:{{ .tag }}"
          imagePullPolicy: {{ .pullPolicy }}
          {{- end }}
          ports:
            - containerPort: 80
          env:
            - name: APP_NAME
              value: {{ .Values.config.appName | quote }}
```

---

### 🧠 Explanation

| Keyword       | Purpose                                 | Description                                          |
| ------------- | --------------------------------------- | ---------------------------------------------------- |
| `with`        | Changes context `.` to the nested value | Inside this block, `.` now refers to `.Values.image` |
| `.repository` | Means `.Values.image.repository`        | Easier and cleaner                                   |
| `{{- end }}`  | Closes the block                        | Always required                                      |

✅ Using `with`, you don’t have to repeat `.Values.image.repository` again and again.

---

## ⚙️ Step 6 — templates/service.yaml

```gotemplate
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
```

---

## 📘 Step 7 — templates/configmap.yaml

```gotemplate
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "webchart.fullname" . }}-config
data:
  appName: {{ .Values.config.appName | quote }}
  maintainer: {{ .Values.config.maintainer | quote }}
  {{- with .Values.config.features }}
  features: |
    {{- range . }}
    - {{ . }}
    {{- end }}
  {{- end }}
```

### 🧠 Explanation

* `with .Values.config.features` changes `.` to the list of features.
* Then `range .` iterates through each feature.
* This results in a YAML array-like list under `features:`.

---

## 📘 Step 8 — README.md

````markdown
# Demo-17: Helm Flow Control WITH Action

This demo shows how to use the `with` action in Helm to simplify access to nested objects.

## What `with` Does
- It **scopes** the context (`.`) to a specific value.
- Makes templates shorter and easier to read.

### Example
Instead of writing:
```gotemplate
image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
````

You can write:

```gotemplate
{{- with .Values.image }}
image: "{{ .repository }}:{{ .tag }}"
{{- end }}
```

## Commands

Render templates:

```bash
helm template demo ./webchart
```

Install:

```bash
helm install demo ./webchart -n demo17 --create-namespace
```

Upgrade with different values:

```bash
helm upgrade demo ./webchart -n demo17 --set image.repository=httpd --set image.tag=2.4
```

````

---

## 💻 Step 9 — commands.sh

```bash
#!/usr/bin/env bash
set -euo pipefail

RELEASE="with-demo"
NAMESPACE="demo17"

echo "Linting chart..."
helm lint webchart

echo "Rendering templates..."
helm template $RELEASE ./webchart -n $NAMESPACE > rendered.yaml

echo "Installing chart..."
helm install $RELEASE ./webchart -n $NAMESPACE --create-namespace

echo "Checking resources..."
kubectl get all -n $NAMESPACE

echo "View ConfigMap data..."
kubectl get configmap -n $NAMESPACE -o yaml

echo "Upgrade with new image..."
helm upgrade $RELEASE ./webchart -n $NAMESPACE --set image.repository=httpd --set image.tag=2.4

echo "Cleanup..."
helm uninstall $RELEASE -n $NAMESPACE
kubectl delete namespace $NAMESPACE
````

---

## 🧠 Test Scenarios

| Scenario     | Values                                          | Expected Result     |
| ------------ | ----------------------------------------------- | ------------------- |
| Default      | image=nginx                                     | Deploys Nginx pods  |
| Updated      | image=httpd                                     | Deploys Apache pods |
| ConfigMap    | Shows appName, maintainer, and list of features |                     |
| `with` usage | Simplifies `.Values.image.*` access             | Cleaner templates   |

---

## 🧩 Key Takeaways

| Concept       | Description                             | Example                                    |
| ------------- | --------------------------------------- | ------------------------------------------ |
| `with`        | Temporarily changes scope of `.`        | `{{ with .Values.image }}`                 |
| `end`         | Closes `with` block                     | `{{ end }}`                                |
| Dot (`.`)     | Inside block refers to new context      | `.repository` = `.Values.image.repository` |
| Nesting       | You can nest `with` inside `range`      | For deeper objects                         |
| Best Practice | Use `with` for repeating nested objects | Makes templates shorter and cleaner        |

---

## 🧹 Cleanup

```bash
helm uninstall demo -n demo17
kubectl delete namespace demo17
```

---

✅ **Result:**
After this demo, you’ll clearly understand:

* How `with` changes the value of the dot (`.`)
* How to simplify nested access in Helm templates
* How to mix `with` with `range` for compact templates

---
