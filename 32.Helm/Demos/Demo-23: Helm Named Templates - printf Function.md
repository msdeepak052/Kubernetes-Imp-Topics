# 🎯 **Topic: Helm Named Templates — `printf` Function**

---

## 🔹 1. What is `printf` in Helm?

Helm uses the **Go templating language**, and `printf` comes from Go.

> 🧩 `printf` is used to **format and combine strings** dynamically inside templates.

It works almost the same way as `printf` in C, Python, or Java.

---

## 🔹 2. Syntax

```yaml
{{ printf "format-string" value1 value2 ... }}
```

* The first argument (`"format-string"`) defines how the rest of the values will be inserted.
* You can insert placeholders like:

  * `%s` → string
  * `%d` → integer
  * `%t` → boolean
  * `%v` → auto type (useful for any)

---

## 🔹 3. Simple Examples

### 🧠 Example 1 — Concatenating Strings

```yaml
{{ printf "%s-%s" "frontend" "prod" }}
```

🧾 Output:

```
frontend-prod
```

---

### 🧠 Example 2 — Formatting Numbers

```yaml
{{ printf "Pods: %d, Replicas: %d" 5 3 }}
```

🧾 Output:

```
Pods: 5, Replicas: 3
```

---

### 🧠 Example 3 — Using Chart and Release Objects

```yaml
{{ printf "%s-%s" .Chart.Name .Release.Name }}
```

🧾 Output (assuming chart name = `mychart`, release = `demo`):

```
mychart-demo
```

---

### 🧠 Example 4 — Storing `printf` Output in a Variable

```yaml
{{- $fullname := printf "%s-%s" .Chart.Name .Release.Name -}}
metadata:
  name: {{ $fullname }}
```

🧾 Output:

```yaml
metadata:
  name: mychart-demo
```

---

### 🧠 Example 5 — Using `printf` inside Named Templates

You can use `printf` within a named template (`define`) to **build consistent naming patterns**:

```yaml
{{- define "mychart.fullname" -}}
{{ printf "%s-%s" .Chart.Name .Release.Name }}
{{- end -}}
```

This allows you to call it later using `include`.

---

## 💡 Why use `printf`?

| Feature                 | Explanation                                         |
| ----------------------- | --------------------------------------------------- |
| 🧩 String concatenation | Combine chart name, release name, environment, etc. |
| 🧱 Reusability          | Used in named templates for consistent naming       |
| 🔧 Flexibility          | Can embed dynamic variables easily                  |
| ⚙️ Integration          | Works with `include`, `nindent`, and `required`     |

---

# 🚀 **Demo-23: Helm Named Templates — `printf` Function**

Now that we understand the theory, let’s create a **hands-on demo**.

---

## 🧱 Step 1 — Create Chart

```bash
helm create demo23-printf
cd demo23-printf
```

Clean up unnecessary files:

```bash
rm -rf templates/*
```

---

## 🧾 Step 2 — Create `values.yaml`

```yaml
appName: deepakbank
environment: dev
image:
  repository: nginx
  tag: "1.29.3"
```

---

## ⚙️ Step 3 — Create `_helpers.tpl`

📁 **File: `templates/_helpers.tpl`**

```yaml
{{/*
Return application name
*/}}
{{- define "demo23.app.name" -}}
{{ .Values.appName }}
{{- end -}}

{{/*
Return formatted full name using printf
*/}}
{{- define "demo23.fullname" -}}
{{ printf "%s-%s-%s" (include "demo23.app.name" .) .Release.Name .Values.environment | lower }}
{{- end -}}

{{/*
Return labels using printf
*/}}
{{- define "demo23.labels" -}}
app.kubernetes.io/name: {{ include "demo23.app.name" . | quote }}
app.kubernetes.io/instance: {{ include "demo23.fullname" . | quote }}
environment: {{ .Values.environment | quote }}
{{- end -}}
```

---

### 🧩 Explanation

1. **`demo23.app.name`** → returns `deepakbank`
2. **`demo23.fullname`** → uses `printf` to combine:

   ```
   appname-release-environment
   ```

   Example output: `deepakbank-demo23-dev`
3. **`demo23.labels`** → adds standardized labels using the templates

---

## 🧾 Step 4 — Create Deployment Template

📁 **File: `templates/deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "demo23.fullname" . }}
  labels:
    {{ include "demo23.labels" . | nindent 4 }}
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ include "demo23.app.name" . | quote }}
  template:
    metadata:
      labels:
        {{ include "demo23.labels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ include "demo23.app.name" . }}
          image: {{ .Values.image.repository }}:{{ .Values.image.tag }}
```

---

## ✅ Step 5 — Lint and Dry Run

```bash
helm lint .
```

✅ Output:

```
1 chart(s) linted, 0 chart(s) failed
```

Then run:

```bash
helm install demo23 . --dry-run --debug
```

---

## 🧾 Step 6 — Rendered Output

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: deepakbank-demo23-dev
  labels:
    app.kubernetes.io/name: "deepakbank"
    app.kubernetes.io/instance: "deepakbank-demo23-dev"
    environment: "dev"
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: "deepakbank"
  template:
    metadata:
      labels:
        app.kubernetes.io/name: "deepakbank"
        app.kubernetes.io/instance: "deepakbank-demo23-dev"
        environment: "dev"
    spec:
      containers:
        - name: deepakbank
          image: nginx:1.29.3
```

---

## 🧩 Step 7 — Visualize Template Relationships

```
demo23.labels
   ↳ demo23.fullname
         ↳ demo23.app.name
              ↳ printf used for dynamic naming
```

This structure demonstrates **printf inside named templates** to dynamically format and return values.

---

## ✅ Summary Table

| Concept   | Description                        | Example                            |
| ---------- | ---------------------------------- | ---------------------------------- |
| `printf`  | Formats and joins multiple strings | `printf "%s-%s" "frontend" "prod"` |
| `include` | Calls another template             | `include "demo23.app.name" .`      |
| `nindent` | Maintains indentation              | `{{ .Value \| nindent 4 }}`        |
| `define`  | Creates reusable template          | `{{- define "demo23.fullname" -}}` |
| `quote`   | Wraps values in quotes             | `{{ .Value \| quote }}`            |

---

## 🧠 Real-World Example

`printf` is widely used in official Helm charts for:

* Building unique **resource names**
* Combining **namespace + environment + release**
* Formatting annotations or labels
* Dynamically generating URLs

Example (from a production-like chart):

```yaml
{{ printf "https://%s.%s.svc.cluster.local" .Release.Name .Release.Namespace }}
```

🧾 Output:

```
https://demo23.default.svc.cluster.local
```

---
