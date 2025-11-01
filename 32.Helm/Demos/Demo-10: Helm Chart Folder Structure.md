# **Demo-10: Helm Chart Folder Structure** 

## 🧩 **Demo-10: Helm Chart Folder Structure**

### 🎯 **Objective**

Understand the structure of a Helm chart — what each file and directory means, and how they work together to form a Helm chart.

---

## ⚙️ **Step 1: Create a New Chart**

```bash
helm create mychart
```

This command generates a complete Helm chart directory named `mychart` with all default files and templates.

---

## 📁 **Step 2: Explore the Folder Structure**

```bash
tree mychart
```

Output:

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

## 📘 **Step 3: Understand Each Component**

| File / Folder                     | Purpose                                                                              |
| --------------------------------- | ------------------------------------------------------------------------------------ |
| **Chart.yaml**                    | Defines the chart’s metadata (name, version, description, etc.)                      |
| **values.yaml**                   | Default configuration values for the chart (can be overridden using `--set` or `-f`) |
| **charts/**                       | Holds dependent charts (for example, sub-charts or external dependencies)            |
| **templates/**                    | Contains Kubernetes manifest templates that will be rendered by Helm                 |
| **templates/_helpers.tpl**        | Holds helper template definitions (like reusable labels or names)                    |
| **templates/deployment.yaml**     | Template for the Kubernetes Deployment object                                        |
| **templates/service.yaml**        | Template for the Service object                                                      |
| **templates/ingress.yaml**        | Template for the Ingress object                                                      |
| **templates/hpa.yaml**            | Template for the HorizontalPodAutoscaler                                             |
| **templates/serviceaccount.yaml** | Template for the ServiceAccount object                                               |
| **templates/NOTES.txt**           | Post-installation notes (displayed when `helm install` finishes)                     |
| **.helmignore**                   | Similar to `.gitignore`; lists files to exclude when packaging the chart             |

---

## 🧠 **Step 4: View the Chart Metadata**

`Chart.yaml`:

```yaml
apiVersion: v2
name: mychart
description: A Helm chart for Kubernetes
type: application
version: 0.1.0
appVersion: "1.16.0"
```

> The `version` field refers to the **chart** version, while `appVersion` is the **application** version (for example, your app image version).

---

## 🧾 **Step 5: View and Modify `values.yaml`**

`values.yaml` (default snippet):

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
```

You can modify these values or override them during installation:

```bash
helm install mychart ./mychart --set image.repository=bitnami/nginx
```

---

## 🧩 **Step 6: Templates in Action**

Each file in `templates/` uses Go templating.
Example: `templates/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "mychart.fullname" . }}
spec:
  replicas: {{ .Values.replicaCount }}
  template:
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
```

Helm replaces the templating expressions (`{{ ... }}`) with actual values at render time.

---

## 🧱 **Step 7: Render the Chart without Installing**

You can test how the templates render:

```bash
helm template mychart ./mychart
```

This will output the full Kubernetes manifests as Helm would install them — without touching the cluster.

---

## 📦 **Step 8: Package and Verify**

To package your chart:

```bash
helm package mychart
```

Output:

```
mychart-0.1.0.tgz
```

To verify the contents:

```bash
tar -tzf mychart-0.1.0.tgz
```

---

## 🧾 **Step 9: Key Commands Recap**

| Command                           | Description                               |
| --------------------------------- | ----------------------------------------- |
| `helm create mychart`             | Create a new chart with default structure |
| `helm template mychart ./mychart` | Render templates locally                  |
| `helm lint mychart`               | Validate chart syntax and best practices  |
| `helm package mychart`            | Package chart into a `.tgz` archive       |
| `helm install mychart ./mychart`  | Install chart to a Kubernetes cluster     |

---

## ✅ **Final Notes**

* **`values.yaml`** → controls configuration.
* **`templates/`** → contains K8s manifest blueprints.
* **`Chart.yaml`** → defines chart metadata.
* **`helm create`** → is the best way to learn by inspecting the auto-generated structure.

---
