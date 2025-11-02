# **Demo-13: Helm If, Else with EQ Function** — 

We’ll build a fully working chart (`demo13-ifelse`) from scratch, run it, and understand **step-by-step** how logic flow works in templates.

---

## 🎯 **Goal**

Understand and practice:

* Conditional statements (`if`, `else if`, `else`, `end`)
* Comparison functions like `eq`, `ne`, `lt`, `gt`
* Controlling manifest rendering based on `.Values`
* Writing clear, maintainable conditional logic in Helm templates

---

## 🧰 **Chart Overview**

We’ll create a chart that:

* Deploys either **Nginx** or **Apache HTTPD** depending on `.Values.serverType`
* Includes a Service conditionally (only if `.Values.exposeService` is true)
* Adds annotations based on environment type (`dev`, `stage`, `prod`)

---

## 📁 Folder Structure

```
demo-13-ifelse/
└── webchart/
    ├── Chart.yaml
    ├── values.yaml
    ├── templates/
    │   ├── deployment.yaml
    │   ├── service.yaml
    │   ├── configmap.yaml
    │   └── _helpers.tpl
    ├── .helmignore
    ├── README.md
    └── commands.sh
```

---

## 🪜 Step-by-Step Setup

### Step 1 — Create the chart skeleton

```bash
mkdir demo-13-ifelse
cd demo-13-ifelse
helm create webchart
```

Now clean up default files (we’ll rewrite them with our custom logic).

---

## Step 2 — Replace chart files

### **Chart.yaml**

```yaml
apiVersion: v2
name: webchart
description: Helm demo to learn If, Else, and EQ function
type: application
version: 0.1.0
appVersion: "1.0.0"
maintainers:
  - name: Deepak Yadav
    email: deepak@example.com
```

---

### **values.yaml**

```yaml
replicaCount: 1

# Choose which server to deploy: nginx or apache
serverType: "nginx"

# Toggle to control Service creation
exposeService: true

# Environment tag (used for annotations)
env: "dev"

image:
  nginx: "nginx:1.25.3"
  apache: "httpd:2.4.62"

service:
  type: ClusterIP
  port: 80
```

---

### **templates/_helpers.tpl**

```gotemplate
{{- define "webchart.fullname" -}}
{{ printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end -}}
```

---

### **templates/deployment.yaml**

This file demonstrates the **`if`, `else if`, and `eq` functions**.

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
      annotations:
        {{- if eq .Values.env "dev" }}
        environment: "Development"
        log-level: "debug"
        {{- else if eq .Values.env "stage" }}
        environment: "Staging"
        log-level: "info"
        {{- else if eq .Values.env "prod" }}
        environment: "Production"
        log-level: "error"
        {{- else }}
        environment: "Unknown"
        {{- end }}
    spec:
      containers:
        - name: {{ .Values.serverType }}
          {{- if eq .Values.serverType "nginx" }}
          image: "{{ .Values.image.nginx }}"
          {{- else if eq .Values.serverType "apache" }}
          image: "{{ .Values.image.apache }}"
          {{- else }}
          image: "busybox"
          command: ["sh","-c","echo Invalid serverType; sleep 3600"]
          {{- end }}
          ports:
            - containerPort: 80
          env:
            - name: SERVER_TYPE
              value: {{ .Values.serverType | quote }}
```

### 🔍 Explanation:

* **`eq .Values.env "dev"`** → checks if environment equals `dev`
* **`if` / `else if` / `else`** → control which block of YAML is rendered
* **`{{- ... -}}`** → removes extra newlines/whitespace for clean YAML

---

### **templates/service.yaml**

Conditional Service rendering using `if .Values.exposeService`.

```gotemplate
{{- if .Values.exposeService }}
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
# Service is disabled for this environment
{{- end }}
```

### 🔍 Explanation:

If `.Values.exposeService` = `false`, Helm **skips** creating a Service manifest.

---

### **templates/configmap.yaml**

We’ll also show inline `if` inside data fields.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "webchart.fullname" . }}-config
data:
  message: |
    {{- if eq .Values.serverType "nginx" }}
    Running NGINX web server
    {{- else if eq .Values.serverType "apache" }}
    Running APACHE web server
    {{- else }}
    Running default BusyBox server
    {{- end }}
  envType: "{{ .Values.env }}"

```

---

### **.helmignore**

```
*.tgz
.git/
README.md
```

---

### **README.md**

````markdown
# Demo-13: Helm If, Else, and EQ Function

This chart demonstrates:
- Conditional templating using `if`, `else if`, `else`, and `end`
- Comparison functions (`eq`, `ne`, `lt`, `gt`)
- Conditional resource creation
- Environment-based annotations

## Example usage

Render chart:
```bash
helm template demo ./webchart
````

Deploy:

```bash
helm install demo ./webchart -n demo13 --create-namespace
```

Try different values:

```bash
helm upgrade demo ./webchart -n demo13 --set serverType=apache
helm upgrade demo ./webchart -n demo13 --set exposeService=false
helm upgrade demo ./webchart -n demo13 --set env=prod
```

````

---

### **commands.sh**
```bash
#!/usr/bin/env bash
set -euo pipefail

RELEASE="ifelse-demo"
NAMESPACE="demo13"

echo "Linting..."
helm lint webchart

echo "Rendering manifests..."
helm template $RELEASE ./webchart -n $NAMESPACE > rendered.yaml

echo "Installing chart..."
kubectl create namespace $NAMESPACE || true
helm install $RELEASE ./webchart -n $NAMESPACE --wait

echo "View Deployment..."
kubectl get deploy -n $NAMESPACE
kubectl get svc -n $NAMESPACE

echo "Change to apache server..."
helm upgrade $RELEASE ./webchart -n $NAMESPACE --set serverType=apache

echo "Disable service and redeploy..."
helm upgrade $RELEASE ./webchart -n $NAMESPACE --set exposeService=false

echo "Change env to prod..."
helm upgrade $RELEASE ./webchart -n $NAMESPACE --set env=prod

echo "Cleanup..."
helm uninstall $RELEASE -n $NAMESPACE
kubectl delete namespace $NAMESPACE
````

---

## 🧩 Step 3 — Run and Observe Behavior

### 🧪 Case 1 — Default (Nginx, `dev` env)

```bash
helm install demo ./webchart -n demo13 --create-namespace
```

✅ Deployment uses Nginx
✅ Service created
✅ Annotations show environment: Development

---

### 🧪 Case 2 — Apache (`serverType=apache`)

```bash
helm upgrade demo ./webchart -n demo13 --set serverType=apache
```

✅ Deployment switches to Apache HTTPD
✅ Message in ConfigMap changes accordingly

---

### 🧪 Case 3 — Disable Service

```bash
helm upgrade demo ./webchart -n demo13 --set exposeService=false
```

✅ Service manifest disappears
✅ `helm get manifest` confirms no Service resource rendered

---

### 🧪 Case 4 — Change Environment

```bash
helm upgrade demo ./webchart -n demo13 --set env=prod
```

✅ Deployment annotation changes to:

```
environment: "Production"
log-level: "error"
```

---

## 🧠 Summary of Key Learnings

| Function   | Description                       | Example                                  |
| ---------- | --------------------------------- | ---------------------------------------- |
| `if`       | Starts a conditional block        | `{{ if eq .Values.env "dev" }}`          |
| `else if`  | Another condition                 | `{{ else if eq .Values.env "prod" }}`    |
| `else`     | Fallback                          | `{{ else }}`                             |
| `end`      | Closes conditional                | `{{ end }}`                              |
| `eq`       | Equal comparison                  | `{{ if eq .Values.serverType "nginx" }}` |
| `ne`       | Not equal                         | `{{ if ne .Values.env "prod" }}`         |
| `lt`, `gt` | Less / greater than (for numbers) | `{{ if gt .Values.replicas 2 }}`         |

---

## 🧹 Cleanup

```bash
helm uninstall demo -n demo13
kubectl delete namespace demo13
```

---

