# 🧩 **Demo-10: Helm Chart Folder Structure (Full Practical Guide)**

---

## 🎯 Objective

Understand the **internal structure of a Helm chart**, what each file does, and how Helm converts it into Kubernetes manifests.

---

## ⚙️ Step-1: Create a New Helm Chart

```bash
helm create mychart
```

🧠 **Explanation:**

* This command creates a full Helm chart skeleton called `mychart/`.
* It includes predefined templates and configuration files.

---

## 📁 Step-2: View Folder Structure

```bash
tree mychart
```

**Output:**

```
mychart/
├── Chart.yaml
├── values.yaml
├── charts/
├── templates/
│   ├── deployment.yaml
│   ├── _helpers.tpl
│   ├── hpa.yaml
│   ├── ingress.yaml
│   ├── NOTES.txt
│   ├── service.yaml
│   └── serviceaccount.yaml
└── .helmignore
```

---

## 📘 Step-3: Understand Each File

| File / Folder                     | Description                                       |
| --------------------------------- | ------------------------------------------------- |
| **Chart.yaml**                    | Chart metadata (name, version, app version, etc.) |
| **values.yaml**                   | Default configuration values used in templates    |
| **charts/**                       | Holds dependent/sub-charts                        |
| **templates/**                    | Contains Kubernetes manifest templates            |
| **templates/_helpers.tpl**        | Helper functions for naming conventions           |
| **templates/deployment.yaml**     | Template for a Deployment resource                |
| **templates/service.yaml**        | Template for a Service resource                   |
| **templates/ingress.yaml**        | Template for Ingress configuration                |
| **templates/hpa.yaml**            | Template for Horizontal Pod Autoscaler            |
| **templates/serviceaccount.yaml** | Template for ServiceAccount                       |
| **templates/NOTES.txt**           | Instructions shown after install                  |
| **.helmignore**                   | Files to ignore when packaging chart              |

---

## 🧾 Step-4: Open and Explain Each File

---

### 🔹 **1. Chart.yaml**

```yaml
apiVersion: v2
name: mychart
description: A Helm chart for Kubernetes
type: application
version: 0.1.0
appVersion: "1.16.0"
```

🧠 **Explanation:**

* `apiVersion`: Helm chart API version (v2 for Helm 3).
* `name`: Chart name.
* `version`: Chart version (used during packaging).
* `appVersion`: Application version (for example, the image tag).

---

### 🔹 **2. values.yaml**

```yaml
replicaCount: 1

image:
  repository: nginx
  pullPolicy: IfNotPresent
  tag: ""

service:
  type: ClusterIP
  port: 80

resources: {}

autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 100
  targetCPUUtilizationPercentage: 80

nodeSelector: {}
tolerations: []
affinity: {}
```

🧠 **Explanation:**

* All chart configuration values live here.
* These can be overridden using:

  ```bash
  helm install mychart ./mychart --set image.repository=bitnami/nginx
  ```

---

### 🔹 **3. templates/_helpers.tpl**

```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "mychart.name" -}}
{{ .Chart.Name }}
{{- end -}}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "mychart.fullname" -}}
{{ .Release.Name }}-{{ .Chart.Name }}
{{- end -}}
```

🧠 **Explanation:**

* This file defines reusable template helpers.
* For example, `{{ include "mychart.fullname" . }}` in other templates will automatically generate a standard name.

---

### 🔹 **4. templates/deployment.yaml**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "mychart.fullname" . }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ include "mychart.name" . }}
  template:
    metadata:
      labels:
        app.kubernetes.io/name: {{ include "mychart.name" . }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default "latest" }}"
          ports:
            - containerPort: 80
```

🧠 **Explanation:**

* Uses **Go templating syntax** (`{{ }}`) to dynamically inject values.
* `.Values` accesses keys from `values.yaml`.
* `.Chart` and `.Release` provide metadata about the chart and release.

---

### 🔹 **5. templates/service.yaml**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "mychart.fullname" . }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: 80
  selector:
    app.kubernetes.io/name: {{ include "mychart.name" . }}
```

🧠 **Explanation:**

* Creates a Service to expose the Deployment.
* Service type (ClusterIP, NodePort, LoadBalancer) comes from `values.yaml`.

---

### 🔹 **6. templates/NOTES.txt**

```
1. Get the application URL by running these commands:
  export POD_NAME=$(kubectl get pods --namespace {{ .Release.Namespace }} -l "app.kubernetes.io/name={{ include "mychart.name" . }}" -o jsonpath="{.items[0].metadata.name}")
  kubectl port-forward $POD_NAME 8080:80
  echo "Visit http://127.0.0.1:8080 to access your app"
```

🧠 **Explanation:**

* These instructions are displayed after you install the chart.
* They help you verify or test your deployed application.

---

## ⚙️ Step-5: Validate the Chart

```bash
helm lint mychart
```

**Output:**

```
==> Linting mychart
1 chart(s) linted, 0 chart(s) failed
```

🧠 **Explanation:**

* Ensures there are no syntax or logical errors in chart structure.

---

## 🔍 Step-6: Render the Templates (Dry Run)

```bash
helm template mychart ./mychart
```

**Output:**

```
# Source: mychart/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: release-mychart
spec:
  replicas: 1
  ...
```

🧠 **Explanation:**

* This command renders all templates into final YAML without installing them into the cluster.

---

## 🚀 Step-7: Install the Chart

```bash
helm install mychart ./mychart
```

**Output:**

```
NAME: mychart
LAST DEPLOYED: Fri Oct 31 10:00:00 2025
NAMESPACE: default
STATUS: deployed
REVISION: 1
NOTES:
1. Get the application URL by running these commands:
...
```

🧠 **Explanation:**

* Installs the chart into the cluster.
* Creates Deployment, Service, and other resources as per templates.

---

## 🧩 Step-8: Verify the Deployment

```bash
kubectl get all
```

**Output:**

```
NAME                                      READY   STATUS    RESTARTS   AGE
pod/mychart-6c9db7b789-2z5jg              1/1     Running   0          1m
service/mychart                           ClusterIP   10.0.34.12   <none>   80/TCP   1m
deployment.apps/mychart                   1/1     1            1           1m
```

---

## 📦 Step-9: Package the Chart

```bash
helm package mychart
```

**Output:**

```
Successfully packaged chart and saved it to: ./mychart-0.1.0.tgz
```

🧠 **Explanation:**

* Packages the chart into a `.tgz` file for distribution or Helm repository upload.

---

## 🧾 Step-10: Cleanup

```bash
helm uninstall mychart
```

**Output:**

```
release "mychart" uninstalled
```

---

## 🧭 Final Summary

| Command                          | Description            |
| -------------------------------- | ---------------------- |
| `helm create mychart`            | Create chart structure |
| `helm lint mychart`              | Validate chart         |
| `helm template mychart`          | Render templates       |
| `helm install mychart ./mychart` | Deploy chart           |
| `kubectl get all`                | Verify resources       |
| `helm package mychart`           | Create `.tgz` package  |
| `helm uninstall mychart`         | Remove release         |

---

## ✅ Key Takeaways

* Every Helm chart follows this folder structure.
* `Chart.yaml` = metadata, `values.yaml` = configuration, `templates/` = manifest templates.
* You can override any value at runtime using:

  ```bash
  helm install mychart ./mychart --set image.repository=bitnami/nginx
  ```
* Helm charts are reusable and parameterized for multiple environments.

---
