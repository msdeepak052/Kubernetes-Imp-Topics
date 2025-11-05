# 🎯 **Topic: Helm Named Templates — Template in Template**

---

## 🔹 1. What does “Template in Template” mean?

In Helm, a **template in template** simply means:

> Calling one named template **inside another** named template.

You do this to **reuse**, **combine**, and **compose** small logic blocks (partials) into larger reusable functions.

It’s similar to **functions calling other functions** in programming.

---

### 🧩 Think of it like this

| Template               | Role                                  | Analogy                         |
| ---------------------- | ------------------------------------- | ------------------------------- |
| `define`               | Define a named block                  | Function definition             |
| `include`              | Call a named block                    | Function call                   |
| “Template in Template” | One `define` calling another `define` | Function calls another function |

---

## 🔹 2. Syntax Review

You can define a named template in `_helpers.tpl`:

```yaml
{{- define "demo24.app.name" -}}
{{ .Values.appName }}
{{- end -}}
```

Then you can call this inside another named template:

```yaml
{{- define "demo24.fullname" -}}
{{ printf "%s-%s" (include "demo24.app.name" .) .Release.Name }}
{{- end -}}
```

Here:

* `"demo24.fullname"` calls `"demo24.app.name"`.
* That’s why it’s called **Template in Template**.

---

## 🔹 3. Why use Template-in-Template?

✅ Reusability → avoid repeating logic
✅ Consistency → single change updates multiple locations
✅ Cleaner and modular charts

---

## 🔹 4. Key Functions Used

| Function  | Description                                     | Example                                                 |               |
| --------- | ----------------------------------------------- | ------------------------------------------------------- | ------------- |
| `define`  | Define a named template                         | `{{ define "mychart.labels" }}...{{ end }}`             |               |
| `include` | Call another template and **return** its output | `{{ include "mychart.labels" . }}`                      |               |
| `nindent` | Indent the output                               | `{{ include "mychart.labels" .                          | nindent 4 }}` |
| `printf`  | Format combined output                          | `{{ printf "%s-%s" (include "name" .) .Release.Name }}` |               |

---

# 🚀 **Demo-24: Helm Named Templates — Template in Template**

We’ll build a Helm chart called **demo24-template-in-template**
that shows how one template calls another inside `_helpers.tpl`.

---

## 🧱 Step 1 — Create Chart

```bash
helm create demo24-template-in-template
cd demo24-template-in-template
```

Clean default templates:

```bash
rm -rf templates/*
```

---

## 🧾 Step 2 — values.yaml

```yaml
appName: deepakbank
stage: prod

image:
  repository: nginx
  tag: "1.29.3"
```

---

## ⚙️ Step 3 — Define Nested Templates in `_helpers.tpl`

📁 File: `templates/_helpers.tpl`

```yaml
{{/*
This template returns the app name
*/}}
{{- define "demo24.app.name" -}}
{{ .Values.appName }}
{{- end -}}

{{/*
This template builds the full name by calling another template inside it
*/}}
{{- define "demo24.fullname" -}}
{{ printf "%s-%s" (include "demo24.app.name" .) .Release.Name | lower }}
{{- end -}}

{{/*
This template defines app labels — it calls the fullname template
*/}}
{{- define "demo24.labels" -}}
app.kubernetes.io/name: {{ include "demo24.app.name" . | quote }}
app.kubernetes.io/instance: {{ include "demo24.fullname" . | quote }}
stage: {{ .Values.stage | quote }}
{{- end -}}
```

### 🔍 Breakdown

1. `demo24.app.name` → returns base app name
2. `demo24.fullname` → calls `demo24.app.name` inside it
3. `demo24.labels` → calls both `demo24.app.name` and `demo24.fullname`

So this is a **template chain**:

```
labels → fullname → app.name
```

That’s **template in template** in action ✅

---

## 🧾 Step 4 — Create Deployment Template

📁 File: `templates/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "demo24.fullname" . }}
  labels:
    {{ include "demo24.labels" . | nindent 4 }}
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ include "demo24.app.name" . | quote }}
  template:
    metadata:
      labels:
        {{ include "demo24.labels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ include "demo24.app.name" . }}
          image: {{ .Values.image.repository }}:{{ .Values.image.tag }}
```

---

## ✅ Step 5 — Lint and Dry Run

```bash
helm lint .
```

✅ Should pass

Then:

```bash
helm install demo24 . --dry-run --debug
```

---

## 🧾 Step 6 — Expected Output

Here’s what Helm will render (simplified):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: deepakbank-demo24
  labels:
    app.kubernetes.io/name: "deepakbank"
    app.kubernetes.io/instance: "deepakbank-demo24"
    stage: "prod"
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: "deepakbank"
  template:
    metadata:
      labels:
        app.kubernetes.io/name: "deepakbank"
        app.kubernetes.io/instance: "deepakbank-demo24"
        stage: "prod"
    spec:
      containers:
        - name: deepakbank
          image: nginx:1.29.3
```

---

## 🧩 Step 7 — Template Chain Visualization

```
demo24.labels
   ↳ demo24.fullname
         ↳ demo24.app.name
```

✔ `demo24.labels` includes `demo24.fullname`
✔ `demo24.fullname` includes `demo24.app.name`
→ That’s **Template inside Template inside Template** 💡

---

# ✅ Summary Table

| Template Name     | Called Inside                   | Purpose                      |
| ----------------- | ------------------------------- | ---------------------------- |
| `demo24.app.name` | Base                            | Defines base app name        |
| `demo24.fullname` | Calls `app.name`                | Builds full name dynamically |
| `demo24.labels`   | Calls `fullname` and `app.name` | Creates consistent labels    |
| `include`         | Used for calling                | Enables nesting              |
| `nindent`         | Used for spacing                | Maintains YAML indentation   |

---

## 💡 Practical Use Case

In real-world Helm charts:

* Templates are **nested deeply** for naming, labels, selectors, annotations, etc.
* This approach keeps charts **modular, DRY (Don’t Repeat Yourself)**, and scalable.

---

