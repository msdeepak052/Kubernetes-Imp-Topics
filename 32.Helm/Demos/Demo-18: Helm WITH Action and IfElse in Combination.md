# **Demo-18: Helm `with` Action and `if-else` Combination** 

---

## 🎯 **Objective**

In this demo, you’ll learn how to:

* Use the `with` action to scope into a specific value.
* Combine it with an `if-else` block for conditional rendering.
* Understand how Helm’s template engine processes nested contexts.

---

## 🧩 **Step 1: Folder Structure**

```bash
demo-18-with-ifelse/
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
description: Demo-18 - WITH Action with IfElse Combination
```

---

## ⚙️ **Step 3: values.yaml**

Here we define an app section that might be empty or filled.

```yaml
app:
  name: "HelmFlowApp"
  environment: "production"
  enabled: true
```

> Try changing these values later (like `enabled: false` or removing `environment`) to see how the template behaves.

---

## 🧱 **Step 4: templates/configmap.yaml**

This is where we combine `with` and `if-else` logic.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Release.Name }}-config
data:
  {{- with .Values.app }}
  {{- if .enabled }}
  app_name: "{{ .name }}"
  environment: "{{ .environment }}"
  message: "Application is enabled and running fine!"
  {{- else }}
  message: "Application is disabled!"
  {{- end }}
  {{- else }}
  message: "No app configuration found!"
  {{- end }}
```
### 🧠 Structure breakdown (indentation helps visualize logic)
with .Values.app          ← starts the outer block
│
├── if .enabled           ← starts the inner conditional
│   ├── message when enabled
│   └── else → message when disabled
│   end                   ← closes inner if
│
└── else                  ← outer else (if no .Values.app at all)
end                       ← closes outer with


---

## 🧠 **Step 5: Explanation**

| Line                                 | Concept                      | Explanation                                                                                  |
| ------------------------------------ | ---------------------------- | -------------------------------------------------------------------------------------------- |
| `{{- with .Values.app }}`            | **with action**              | Temporarily moves into `.Values.app` — all inner references use `.` to refer to this object. |
| `{{- if .enabled }}`                 | **if condition inside with** | Checks the boolean value of `.enabled` within `.Values.app`.                                 |
| `app_name`, `environment`, `message` | **conditional fields**       | Rendered only if the app is enabled.                                                         |
| `else` inside `with`                 | **nested else**              | Used if `.enabled` is false.                                                                 |
| Outer `else` (after `with`)          | **fallback**                 | Used if `.Values.app` is completely missing.                                                 |

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

## 🚀 **Step 7: Dry Run to See Rendered Output**

```bash
helm install demo18 mychart --dry-run --debug
```

### 🟢 **If app.enabled = true**

Output:

```yaml
data:
  app_name: "HelmFlowApp"
  environment: "production"
  message: "Application is enabled and running fine!"
```

### 🔴 **If app.enabled = false**

Output:

```yaml
data:
  message: "Application is disabled!"
```

### ⚫ **If app section removed**

Output:

```yaml
data:
  message: "No app configuration found!"
```

---

## 🔍 **Step 8: Deploy for Real**

```bash
helm install demo18 mychart
kubectl get configmap
kubectl get configmap demo18-config -o yaml
```

You’ll see the final data section rendered based on your condition.

---

## 🧹 **Step 9: Cleanup**

```bash
helm uninstall demo18
```

---

## 💡 **Learning Recap**

| Concept                    | Description                                                 |
| -------------------------- | ----------------------------------------------------------- |
| `with`                     | Creates a local context for a sub-value.                    |
| `if`, `else` inside `with` | Add conditions within that context.                         |
| Nested `else`              | Works in both `if` and `with` scopes.                       |
| Output control             | Helps produce clean manifests with clear conditional logic. |

---
