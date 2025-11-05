## 🎯 What Are Helm Variables?

Helm variables are **temporary placeholders** used inside templates to store data (like a value, object, or result of a function).

They make your templates **cleaner, reusable, and more readable**, especially when you refer to the same value multiple times.

---

## 🧩 **1️⃣ Declaring a Variable**

Helm variables **start with `$`** and are created using `:=`.

### ✅ Syntax

```yaml
{{- $variableName := VALUE }}
```

### Example

```yaml
{{- $app := .Values.app }}
```

This creates a variable named `$app` which holds everything inside `.Values.app`.

So instead of repeatedly writing:

```yaml
{{ .Values.app.name }}
{{ .Values.app.version }}
```

You can simply write:

```yaml
{{ $app.name }}
{{ $app.version }}
```

---

## 🧠 **2️⃣ Why Use Variables?**

| Without Variables                                                            | With Variables                                          |
| ---------------------------------------------------------------------------- | ------------------------------------------------------- |
| `.Values.app.name` <br> `.Values.app.version` <br> `.Values.app.environment` | `$app.name` <br> `$app.version` <br> `$app.environment` |

👉 Cleaner, shorter, and easier to maintain!

---

## ⚙️ **3️⃣ Where Can You Use Variables?**

You can use variables in:

* Any template file (Deployment, ConfigMap, Service, etc.)
* Inside `if`, `range`, or `with` blocks
* Inside helper templates (`_helpers.tpl`)
* Inside loops to hold temporary values

---

## 💡 **4️⃣ Examples**

Let’s look at practical examples.

---

### 🧱 Example 1: Basic Variable in a ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Release.Name }}-config
data:
  {{- $app := .Values.app }}
  app_name: "{{ $app.name }}"
  app_version: "{{ $app.version }}"
  message: "Running {{ $app.name }} version {{ $app.version }}"
```

**values.yaml**

```yaml
app:
  name: "HelmApp"
  version: "v1.0"
```

✅ Rendered output:

```yaml
data:
  app_name: "HelmApp"
  app_version: "v1.0"
  message: "Running HelmApp version v1.0"
```

---

### 🧱 Example 2: Using Variable Inside `range` (Loop)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Release.Name }}-config
data:
  {{- $envs := .Values.environments }}
  {{- range $key, $value := $envs }}
  {{ $key }}: "{{ $value }}"
  {{- end }}
```

**values.yaml**

```yaml
environments:
  dev: "Development"
  qa: "Testing"
  prod: "Production"
```

✅ Rendered output:

```yaml
data:
  dev: "Development"
  qa: "Testing"
  prod: "Production"
```

Here, `$envs` stores `.Values.environments`, and inside the `range` loop we use `$key` and `$value`.

---

### 🧱 Example 3: Variable with Conditional Logic

```yaml
{{- $app := .Values.app }}
{{- if $app.enabled }}
App "{{ $app.name }}" is enabled in "{{ $app.environment }}" environment.
{{- else }}
App "{{ $app.name }}" is disabled.
{{- end }}
```

**values.yaml**

```yaml
app:
  name: "HelmVarApp"
  environment: "staging"
  enabled: true
```

✅ Rendered output:

```
App "HelmVarApp" is enabled in "staging" environment.
```

---

## 🧩 **5️⃣ Common Built-in Variables**

| Variable        | Description                                                     |
| --------------- | --------------------------------------------------------------- |
| `.Values`       | Contains user-defined values from `values.yaml` or CLI `--set`. |
| `.Chart`        | Metadata about the chart (`Chart.yaml`).                        |
| `.Release`      | Info about Helm release (name, namespace, revision).            |
| `.Files`        | Access files inside your chart (used with `Files.Get`).         |
| `.Capabilities` | Info about the Kubernetes cluster (API versions supported).     |

---

### Example with Built-ins

```yaml
data:
  release_name: "{{ .Release.Name }}"
  chart_name: "{{ .Chart.Name }}"
  chart_version: "{{ .Chart.Version }}"
```

---

## ⚙️ **6️⃣ Scope of Variables**

* Variables are **scoped** to the block they’re defined in.
* Inside loops or `with` blocks, the **`.` (dot)** changes meaning — so `$variable` helps you access **outer context** safely.

---

### Example of Scope

```yaml
{{- $root := . }}
{{- range .Values.apps }}
app: {{ .name }}
release: {{ $root.Release.Name }}
{{- end }}
```

Here:

* Inside the `range`, `.` refers to an app item.
* `$root` stores the global context, so you can still access `.Release.Name`.

---

## 🔍 **7️⃣ Debugging Variables**

You can print variables to inspect their values using `toYaml` and `nindent`.

```yaml
{{- $app := .Values.app }}
{{- toYaml $app | nindent 2 }}
```

---

## 🧪 **8️⃣ Run and Test**

```bash
helm lint mychart
helm install demo19 mychart --dry-run --debug
```

You’ll see how all variables resolve into their final values in the rendered manifest.

---

## 🧹 **9️⃣ Cleanup**

```bash
helm uninstall demo19
```

---

## 💬 **Summary Table**

| Feature                | Description                 | Example                             |               |
| ---------------------- | --------------------------- | ----------------------------------- | ------------- |
| Variable declaration   | Create variable             | `{{- $app := .Values.app }}`        |               |
| Access subkeys         | Use variable field          | `{{ $app.name }}`                   |               |
| Inside range/with      | Use `$root` to keep context | `{{ $root.Release.Name }}`          |               |
| Combine with condition | If logic on variable        | `{{ if $app.enabled }}...{{ end }}` |               |
| Debug                  | Print YAML value            | `{{ toYaml $app                     | nindent 2 }}` |

---

✅ **In Real Charts**
You’ll often see:

```yaml
{{- $fullname := include "mychart.fullname" . }}
metadata:
  name: {{ $fullname }}
```

👉 `$fullname` is a variable that stores a helper function’s output — used multiple times in the same file.

---


## 🎯 ** Demo Objective**

In this demo, you’ll learn:

* How to define **variables** inside Helm templates.
* How to **reference** those variables.
* How they make templates **cleaner, reusable, and easier to maintain**.

---

## 🧩 **Step 1: Folder Structure**

```bash
demo-19-variables/
├── mychart/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       └── configmap.yaml
```

---

## 🗂 **Step 2: Chart.yaml**

```yaml
apiVersion: v2
name: mychart
version: 0.1.0
description: Demo-19 - Helm Variables
```

---

## ⚙️ **Step 3: values.yaml**

```yaml
app:
  name: "HelmVariableApp"
  version: "v1.5"
  environment: "staging"
  region: "ap-south-1"
```

---

## 🧱 **Step 4: templates/configmap.yaml**

Here’s where we use **Helm variables**.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Release.Name }}-config
data:
  {{- $app := .Values.app }}
  app_name: "{{ $app.name }}"
  app_version: "{{ $app.version }}"
  environment: "{{ $app.environment }}"
  region: "{{ $app.region }}"
  release_name: "{{ .Release.Name }}"
  chart_name: "{{ .Chart.Name }}"
  chart_version: "{{ .Chart.Version }}"
  message: "Deployed {{ $app.name }} version {{ $app.version }} in {{ $app.environment }} region {{ $app.region }}"
```

---

## 🧠 **Step 5: Explanation**

| Concept                      | Explanation                                                                          |
| ---------------------------- | ------------------------------------------------------------------------------------ |
| `{{- $app := .Values.app }}` | Creates a **local variable** `$app` and assigns it the value of `.Values.app`.       |
| `$app.name`, `$app.version`  | Access values using the variable instead of long references like `.Values.app.name`. |
| `.Release.*`, `.Chart.*`     | Helm built-in objects — used to print release name and chart metadata.               |
| The `message` line           | Combines multiple variables into a single string (real-world usage).                 |

---

## 🧪 **Step 6: Lint the Chart**

```bash
helm lint mychart
```

✅ Expected output:

```
1 chart(s) linted, no failures
```

---

## 🚀 **Step 7: Dry Run and Debug**

```bash
helm install demo19 mychart --dry-run --debug
```

**Rendered output example:**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: demo19-config
data:
  app_name: "HelmVariableApp"
  app_version: "v1.5"
  environment: "staging"
  region: "ap-south-1"
  release_name: "demo19"
  chart_name: "mychart"
  chart_version: "0.1.0"
  message: "Deployed HelmVariableApp version v1.5 in staging region ap-south-1"
```

---

## 🔍 **Step 8: Deploy and Verify**

```bash
helm install demo19 mychart
kubectl get configmap
kubectl get configmap demo19-config -o yaml
```

You’ll see the ConfigMap with all variables replaced properly.

---

## 🧹 **Step 9: Cleanup**

```bash
helm uninstall demo19
```

---

## 💡 **Learning Recap**

| Concept       | Description                                                                       |
| ------------- | --------------------------------------------------------------------------------- |
| `$variable`   | Declares a variable in Helm templates.                                            |
| `:=`          | Used for assignment (create a variable).                                          |
| Scope         | Variables are limited to the file or block they’re declared in.                   |
| Benefit       | Reduces repetition like `.Values.app.name` multiple times.                        |
| Best practice | Use for subobjects (e.g., `$app := .Values.app`), loops, or repeated expressions. |

---

✅ **Real-World Tip:**
You’ll often see `$values := .Values` or `$fullName := include "chart.fullname" .` in production Helm charts — this improves readability and performance during template rendering.

---
