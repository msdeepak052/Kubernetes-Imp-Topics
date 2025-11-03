# 🌀 **Demo-20: Helm Flow Control – `range` Action with Lists**

---

## 🎯 **Goal**

By the end of this demo, you’ll:

* Understand the `range` action in Helm templates.
* Learn how to loop over **lists** (arrays) from your `values.yaml`.
* Use variables like `$index` and `$value` to handle items dynamically.
* Build a complete working Helm chart that renders multiple entries.

---

## 🧠 **Understanding the `range` Action (Concept)**

### 🔹 What is `range`?

In Helm templates, `range` is used to **iterate (loop)** over lists or maps.
It’s equivalent to a **for loop** in programming languages.

### ✅ **Basic Syntax:**

```yaml
{{- range .Values.myList }}
  {{ . }}
{{- end }}
```

Here:

* `.Values.myList` → refers to the list from `values.yaml`
* `.` → inside the loop refers to the current item

---

### 🔸 **Example: Simple List**

**values.yaml**

```yaml
fruits:
  - apple
  - banana
  - mango
```

**template**

```yaml
{{- range .Values.fruits }}
Fruit: {{ . }}
{{- end }}
```

🟢 **Rendered Output**

```
Fruit: apple
Fruit: banana
Fruit: mango
```

---

### 🔸 **Example: Using Variables Inside Range**

You can assign variables inside the `range` loop:

```yaml
{{- range $index, $fruit := .Values.fruits }}
{{ $index }}: {{ $fruit }}
{{- end }}
```

🟢 **Output:**

```
0: apple
1: banana
2: mango
```

* `$index` — current loop index (starts from 0)
* `$fruit` — current item value

---

### 🔸 **Example: Combining with Parent Context**

If you need access to parent context (like `.Release.Name`), use a **root variable**.

```yaml
{{- $root := . }}
{{- range $fruit := .Values.fruits }}
{{ $root.Release.Name }} likes {{ $fruit }}
{{- end }}
```

🟢 **Output:**

```
demo20 likes apple
demo20 likes banana
demo20 likes mango
```

---

Now that the concept is clear — let’s apply this in a **full working Helm demo**.

---

## 🧩 **Step 1: Folder Structure**

```bash
demo-20-range-list/
├── mychart/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       └── configmap.yaml
```

---

## 📄 **Step 2: Chart.yaml**

```yaml
apiVersion: v2
name: mychart
version: 0.1.0
description: Demo-20 - Helm Flow Control RANGE Action with List
```

---

## ⚙️ **Step 3: values.yaml**

We’ll define a list of DevOps tools for looping.

```yaml
devopsTools:
  - Git
  - Docker
  - Kubernetes
  - Jenkins
  - Prometheus
  - Grafana
```

---

## 🧱 **Step 4: templates/configmap.yaml**

Here’s where we use the `range` action.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Release.Name }}-config
data:
  tools: |
    {{- $root := . }}
    {{- range $index, $tool := .Values.devopsTools }}
    {{ printf "%d. %s" (add $index 1) $tool }}
    {{- end }}
```

> 🧩 The `add` function adds 1 to the index so numbering starts from 1, not 0.

---

## 🧠 **Step 5: Explanation**

| Line                                                | Concept              | Explanation                                                       |
| --------------------------------------------------- | -------------------- | ----------------------------------------------------------------- |
| `{{- range $index, $tool := .Values.devopsTools }}` | Range loop           | Iterates through each tool name in the list.                      |
| `$index`                                            | Loop counter         | Starts from 0, so we used `add` to start from 1.                  |
| `$tool`                                             | Current list item    | Refers to a single tool (e.g., “Docker”).                         |
| `$root := .`                                        | Root context         | Lets you access `.Release` or `.Chart` if needed inside the loop. |
| `printf`                                            | Go template function | Used to format string output (`1. Docker`).                       |

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

## 🚀 **Step 7: Dry Run (Debug Rendered Output)**

```bash
helm install demo20 mychart --dry-run --debug
```

🟢 **Rendered Output:**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: demo20-config
data:
  tools: |
    1. Git
    2. Docker
    3. Kubernetes
    4. Jenkins
    5. Prometheus
    6. Grafana
```

---

## 🔍 **Step 8: Deploy and Verify**

```bash
helm install demo20 mychart
kubectl get configmap demo20-config -o yaml
```

You’ll see the ConfigMap created with your tools list as data.

---

## 🧹 **Step 9: Cleanup**

```bash
helm uninstall demo20
```

---

## 💡 **Additional Tips**

### ✅ You can also use range inside labels or env sections:

```yaml
env:
{{- range $tool := .Values.devopsTools }}
  - name: TOOL_{{ upper $tool }}
    value: "enabled"
{{- end }}
```

🟢 Output:

```yaml
env:
  - name: TOOL_GIT
    value: "enabled"
  - name: TOOL_DOCKER
    value: "enabled"
  - name: TOOL_KUBERNETES
    value: "enabled"
  ...
```

### ✅ Range over empty list check:

```yaml
{{- if .Values.devopsTools }}
  {{- range .Values.devopsTools }}
  Tool: {{ . }}
  {{- end }}
{{- else }}
  No tools found!
{{- end }}
```

---

## 🧭 **Learning Recap**

| Concept            | Description              | Example                            |
| ------------------ | ------------------------ | ---------------------------------- |
| `range`            | Loops over a list or map | `{{ range .Values.items }}`        |
| `$index`, `$value` | Loop variables           | `{{ $index }}`, `{{ $value }}`     |
| `add`              | Add numbers              | `{{ add $index 1 }}`               |
| `$root`            | Save root context        | `{{- $root := . }}`                |
| Nested `range`     | Loop inside loop         | Useful for maps/lists combinations |

---

✅ **Real-world relevance:**
`range` is heavily used in production Helm charts — e.g. for:

* Environment variables
* ConfigMap entries
* Mounts
* Services per port
* Multiple replicas or node roles

---
