# 👉 **Demo-22: Helm Named Templates**

We’ll first learn the **concept in detail**, and then move on to a **hands-on Helm demo** with full files, commands, and explanations.

---

## 🧠 Concept: Helm Named Templates

Helm templates can contain **reusable blocks of code**, known as **Named Templates**.

Think of them as **functions** — you define once, and reuse anywhere within your chart (and even across subcharts).

---

### 🔹 Why Named Templates?

When working on large Helm charts, you often repeat:

* labels
* resource names
* annotations
* standard formatting

Named templates help you **avoid duplication** and **enforce consistency**.

---

### 🔹 Basic Syntax

#### 1️⃣ Define a Named Template

You define them inside a **`_helpers.tpl`** file in the `templates/` folder.

```yaml
{{- define "mychart.fullname" -}}
{{ .Release.Name }}-{{ .Chart.Name }}
{{- end -}}
```

Here:

* `"mychart.fullname"` → is the **name** of your template.
* The code inside → is the **template content**.

---

#### 2️⃣ Use (Call) the Named Template

Use the `include` function to call it anywhere:

```yaml
metadata:
  name: {{ include "mychart.fullname" . }}
```

`.` passes the current context (so the helper can access `.Release.Name`, `.Chart.Name`, etc.).

---

### 🔹 Key Functions Used with Named Templates

| Function   | Description                                |
| ---------- | ------------------------------------------ |
| `define`   | Declares a named template                  |
| `include`  | Calls a named template                     |
| `template` | Similar to `include`, but outputs directly |
| `required` | Enforces mandatory values                  |
| `nindent`  | Indents the output of an included template |

---

### 🔹 Example

#### `templates/_helpers.tpl`

```yaml
{{- define "mychart.labels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/version: {{ .Chart.Version }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
```

#### `templates/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "mychart.fullname" . }}
  labels:
{{ include "mychart.labels" . | indent 4 }}
```

---

## ⚙️ DEMO-22: Helm Named Templates (Hands-on)

Let’s now build this step-by-step 👇

---

### 🏗 Step 1: Create a new chart

```bash
helm create demo-22-namedtemplates
cd demo-22-namedtemplates
```

Remove default files:

```bash
rm -rf templates/*
```

---

### 🧾 Step 2: Update `Chart.yaml`

```yaml
apiVersion: v2
name: demo-22-namedtemplates
description: Helm demo to understand Named Templates
version: 0.1.0
appVersion: "1.0"
```

---

### ⚙️ Step 3: Create `_helpers.tpl` (define named templates)

**File:** `templates/_helpers.tpl`

```yaml
{{/*
Define a reusable name
*/}}
{{- define "demo22.fullname" -}}
{{ .Release.Name }}-{{ .Chart.Name }}
{{- end -}}

{{/*
Define reusable labels
*/}}
{{- define "demo22.labels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/version: {{ .Chart.Version }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
```

---

### 🧩 Step 4: Create a Deployment that uses the named templates

**File:** `templates/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "demo22.fullname" . }}
  labels:
{{ include "demo22.labels" . | indent 4 }}
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/instance: {{ .Release.Name }}
  template:
    metadata:
      labels:
{{ include "demo22.labels" . | indent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "nginx:latest"
          ports:
            - containerPort: 80
```

---

### ⚙️ Step 5: Add a simple service (to test reusability)

**File:** `templates/service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "demo22.fullname" . }}
  labels:
{{ include "demo22.labels" . | indent 4 }}
spec:
  type: ClusterIP
  ports:
    - port: 80
      targetPort: 80
  selector:
    app.kubernetes.io/instance: {{ .Release.Name }}
```

---

### 🧾 Step 6: Validate your chart

```bash
helm lint .
```

✅ Output should be:

```
1 chart(s) linted, no failures
```

---

### 🚀 Step 7: Install the chart

```bash
helm install demo22-release .
```

---

### 🔍 Step 8: Verify the generated manifests

```bash
helm get manifest demo22-release
```

**Output (simplified):**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo22-release-demo-22-namedtemplates
  labels:
    app.kubernetes.io/name: demo-22-namedtemplates
    app.kubernetes.io/version: 0.1.0
    app.kubernetes.io/instance: demo22-release
---
apiVersion: v1
kind: Service
metadata:
  name: demo22-release-demo-22-namedtemplates
  labels:
    app.kubernetes.io/name: demo-22-namedtemplates
    app.kubernetes.io/version: 0.1.0
    app.kubernetes.io/instance: demo22-release
```

✅ Notice:

* Both Service and Deployment use the **same name and label pattern** via `_helpers.tpl`.
* This is the power of **Named Templates** — no repetition.

---

### 🧹 Step 9: Uninstall the release

```bash
helm uninstall demo22-release
```

---

## 📘 Summary: Helm Named Templates

| Concept              | Description                                         | Example                         |              |
| -------------------- | --------------------------------------------------- | ------------------------------- | ------------ |
| `define`             | Defines a named template                            | `{{ define "demo.labels" }}`    |              |
| `include`            | Includes and returns the output of a named template | `{{ include "demo.labels" . }}` |              |
| `_helpers.tpl`       | File to keep reusable templates                     | `templates/_helpers.tpl`        |              |
| `indent` / `nindent` | Indent included output properly                     | `{{ include "demo.labels" .     | indent 4 }}` |

---

### 💡 Real-World Usage

* Helm’s **official charts** use `_helpers.tpl` heavily for naming and labels.
* It ensures uniformity across all Kubernetes resources.
* Common helpers include:

  * `fullname`
  * `labels`
  * `selectorLabels`
  * `chart`

---
