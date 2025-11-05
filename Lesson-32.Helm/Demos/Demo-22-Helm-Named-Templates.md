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


> These three Helm functions — `template`, `required`, and `nindent` — are often used inside templates or helper files and make your Helm charts more **robust**, **reusable**, and **readable**.

Let’s go one by one with **clear explanations and examples** 👇

---

## 🔹 1️⃣ `template` — (Similar to `include`, but outputs directly)

### 🧠 Concept

Both `include` and `template` call another named template.
However:

| Function   | Behavior                                                                  |            |            |
| ---------- | ------------------------------------------------------------------------- | ---------- | ---------- |
| `include`  | Returns the output **as a string** (you can pipe or format it).           |            |            |
| `template` | Outputs the template content **directly into the file** (no need to use ` | indent`or` | nindent`). |

---

### 🧩 Example 1 — `include`

**_helpers.tpl**

```yaml
{{- define "mychart.labels" -}}
app: {{ .Chart.Name }}
env: {{ .Values.env }}
{{- end -}}
```

**deployment.yaml**

```yaml
metadata:
  labels:
{{ include "mychart.labels" . | indent 4 }}
```

👉 Here, `include` returns the helper content **as a string**,
then `| indent 4` adds 4 spaces to format YAML properly.

---

### 🧩 Example 2 — `template`

**deployment.yaml**

```yaml
metadata:
  labels:
  {{- template "mychart.labels" . }}
```

👉 `template` **directly inserts** the content of `"mychart.labels"` into the output.
No `indent` or `nindent` needed.

---

### ⚙️ Key takeaway

✅ `include` = flexible (can use pipes like `| indent`, `| upper`, etc.)
✅ `template` = direct output (no formatting control)

Use `include` when you need indentation or want to manipulate the text.
Use `template` when you just want to insert it “as-is.”

---

## 🔹 2️⃣ `required` — (Enforces mandatory values)

### 🧠 Concept

The `required` function ensures that a specific Helm value **must be provided** — otherwise, Helm installation fails with an error.

**Syntax:**

```yaml
{{ required "Error message if missing" .Values.someKey }}
```

---

### 🧩 Example — `required` in use

**values.yaml**

```yaml
replicaCount: 2
# image:
#   repository: nginx
```

**deployment.yaml**

```yaml
spec:
  replicas: {{ .Values.replicaCount }}
  template:
    spec:
      containers:
        - name: nginx
          image: {{ required "image.repository is required!" .Values.image.repository }}
```

If `.Values.image.repository` is missing, Helm will throw an error:

```
Error: template: deployment.yaml:11:16: executing "deployment.yaml" 
at <required "image.repository is required!" .Values.image.repository>: 
error calling required: image.repository is required!
```

✅ This ensures critical values aren’t forgotten in CI/CD or by other developers.

---

## 🔹 3️⃣ `nindent` — (Newline + Indent)

### 🧠 Concept

`nindent` works like `indent`, **but also adds a newline before indenting**.

| Function    | Description                   |
| ----------- | ----------------------------- |
| `indent 4`  | Adds 4 spaces of indentation  |
| `nindent 4` | Adds a **newline + 4 spaces** |

This helps when embedding text inside YAML blocks.

---

### 🧩 Example — difference between `indent` and `nindent`

**_helpers.tpl**

```yaml
{{- define "mychart.labels" -}}
app: {{ .Chart.Name }}
env: {{ .Values.env }}
{{- end -}}
```

**deployment.yaml**

```yaml
metadata:
  labels: {{ include "mychart.labels" . | indent 4 }}
```

Output 👇

```yaml
metadata:
  labels: app: myapp
    env: dev
```

😖 Not properly formatted YAML.

---

✅ Correct way using `nindent`

```yaml
metadata:
  labels:
{{ include "mychart.labels" . | nindent 4 }}
```

Output 👇

```yaml
metadata:
  labels:
    app: myapp
    env: dev
```

Perfectly valid YAML 🎯

---

## 🧾 Quick Reference Summary

| Function   | Purpose                                          | Example                             | Output Type            |                    |
| ---------- | ------------------------------------------------ | ----------------------------------- | ---------------------- | ------------------ |
| `template` | Inserts another named template’s output directly | `{{ template "mychart.labels" . }}` | Directly rendered YAML |                    |
| `include`  | Returns output as string (can pipe it)           | `{{ include "mychart.labels" .      | indent 4 }}`           | String             |
| `required` | Enforces that a value must be provided           | `{{ required "msg" .Values.key }}`  | Validation             |                    |
| `nindent`  | Newline + indent text for proper YAML format     | `{{ include "helper" .              | nindent 4 }}`          | String (formatted) |

---

## 🧩 Mini Demo to Try

### 1️⃣ `values.yaml`

```yaml
env: dev
image:
  repository: nginx
```

### 2️⃣ `templates/_helpers.tpl`

```yaml
{{- define "demo.labels" -}}
app: demo
env: {{ .Values.env }}
{{- end -}}
```

### 3️⃣ `templates/configmap.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: demo-config
  labels:
{{ include "demo.labels" . | nindent 4 }}
data:
  image: {{ required "image.repository must be set!" .Values.image.repository }}
```

Run:

```bash
helm install demo22 .
```

✅ Works fine if `image.repository` exists
❌ Fails if you comment it out (validating `required` usage)
✅ Produces perfectly formatted YAML because of `nindent`

---



