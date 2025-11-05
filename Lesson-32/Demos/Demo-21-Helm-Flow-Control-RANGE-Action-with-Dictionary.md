# **Demo-21: Helm Flow Control — `range` Action with Dictionary/Maps**,

We’ll first understand the **concept of `range` with dictionaries**, and then do a **complete practical Helm demo** with full files, commands, and step-by-step explanations.

---

## 🧠 Concept: `range` with Dictionary (Map)

In Helm templates, a **dictionary (map)** is a **key-value pair collection** — similar to a Python `dict` or Java `Map`.

The `range` action allows you to **iterate over each key-value pair** in that dictionary.

---

### 🔹 Basic Syntax

```yaml
{{- range $key, $value := .Values.mapName }}
{{ $key }}: {{ $value }}
{{- end }}
```

Here:

* `$key` → variable holding the key.
* `$value` → variable holding the value.
* `.Values.mapName` → refers to the dictionary defined in `values.yaml`.

---

### 🔹 Example 1: Inline Dictionary

```yaml
{{- $person := dict "name" "Deepak" "role" "DevOps Engineer" "location" "India" }}
{{- range $key, $value := $person }}
{{ $key }} = {{ $value }}
{{- end }}
```

**Output:**

```
name = Deepak
role = DevOps Engineer
location = India
```

---

### 🔹 Example 2: Dictionary in `values.yaml`

```yaml
userDetails:
  name: Deepak
  role: DevOps Engineer
  experience: 5 Years
```

And in your template:

```yaml
{{- range $key, $value := .Values.userDetails }}
{{ $key }}: {{ $value }}
{{- end }}
```

**Output:**

```
name: Deepak
role: DevOps Engineer
experience: 5 Years
```

---

### 🧩 DEMO-21: Helm Flow Control `range` with Dictionary (Maps)

Now let’s apply this practically.

---

### 🏗 Step 1: Create a new Helm chart

```bash
helm create demo-21-range-map
cd demo-21-range-map
```

Remove all default templates:

```bash
rm -rf templates/*
```

---

### 🧾 Step 2: Update `Chart.yaml`

```yaml
apiVersion: v2
name: demo-21-range-map
description: A Helm demo to practice range with dictionary/maps
version: 0.1.0
appVersion: "1.0"
```

---

### ⚙️ Step 3: Define dictionary in `values.yaml`

```yaml
userDetails:
  name: Deepak
  role: DevOps Engineer
  location: Bangalore
  company: XYZ
```

---

### 🧩 Step 4: Create a ConfigMap template to use `range`

**File:** `templates/configmap.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: userdetails-config
data:
  user-info: |
{{- range $key, $value := .Values.userDetails }}
    {{ $key }}: {{ $value }}
{{- end }}
```

---

### ⚙️ Step 5: Lint the chart

```bash
helm lint .
```

✅ Output should show:

```
1 chart(s) linted, no failures
```

---

### 🚀 Step 6: Install the chart

```bash
helm install my-userdetails .
```

---

### 🧾 Step 7: Check the generated manifest

```bash
helm get manifest my-userdetails
```

Output will look like:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: userdetails-config
data:
  user-info: |
    name: Deepak
    role: DevOps Engineer
    location: Bangalore
    company: XYZ
```

---

### 💡 Step 8: Add Custom Formatting (Optional)

You can modify the template to make it more readable:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: userdetails-config
data:
  user-info: |
{{- range $key, $value := .Values.userDetails }}
    - Key: {{ $key | upper }}
      Value: {{ $value }}
{{- end }}
```

This applies the `upper` function to the keys.

---

### 🧹 Step 9: Uninstall the release

```bash
helm uninstall my-userdetails
```

---

## 🧠 Summary

| Concept          | Description                                      |
| ---------------- | ------------------------------------------------ |
| Dictionary (map) | A collection of key-value pairs                  |
| `range`          | Loops through each key and value in a dictionary |
| `$key`, `$value` | Capture key and value in the loop                |
| `dict`           | Creates an inline dictionary                     |
| `.Values.<key>`  | Accesses data from `values.yaml`                 |

---

### ⚙️ Key Difference Between `range` with List vs Dictionary

| Feature        | List                         | Dictionary            |
| -------------- | ---------------------------- | --------------------- |
| Data structure | Ordered sequence             | Key-value pairs       |
| Loop variables | Only value or (index, value) | (key, value)          |
| Access example | `.Values.fruits`             | `.Values.userDetails` |
| Output example | `- Apple`                    | `name: Deepak`        |

---
