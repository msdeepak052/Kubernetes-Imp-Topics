# Comprehensive JSONPath tutorial

---

# **🔹 JSONPath in Kubernetes**

**JSONPath** is a query language for extracting specific fields from JSON-formatted data.

* Kubernetes API outputs resources in **JSON** or **YAML**.
* `kubectl` has a `-o jsonpath=<expression>` flag to extract specific fields.
* Very useful for scripting, filtering resources, or getting custom output.

---

## **1️⃣ Basic JSONPath Syntax**

| Syntax              | Description       | Example                                              |
| ------------------- | ----------------- | ---------------------------------------------------- |
| `$`                 | Root element      | `$`                                                  |
| `.`                 | Child element     | `.metadata.name`                                     |
| `..`                | Recursive descent | `..name`                                             |
| `*`                 | Wildcard          | `.items[*].metadata.name`                            |
| `[n]`               | Array index       | `.items[0].metadata.name`                            |
| `[start:end]`       | Array slice       | `.items[0:2].metadata.name`                          |
| `[?(<expression>)]` | Filter            | `.items[?(@.status.phase=="Running")].metadata.name` |

---

## **2️⃣ Using JSONPath with `kubectl`**

**Basic Example: Get pod names**

```bash
kubectl get pods -o jsonpath='{.items[*].metadata.name}'
```

**Explanation:**

* `.items` → list of pods in the namespace.
* `[*]` → iterate all pods.
* `.metadata.name` → extract the name field.
* Output: space-separated pod names.

---

**Example: Get pod names line by line**

```bash
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}'
```

---

**Example: Get container images in all pods**

```bash
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}: {.spec.containers[*].image}{"\n"}{end}'
```

---

**Example: Filter pods by status Running**

```bash
kubectl get pods -o jsonpath='{.items[?(@.status.phase=="Running")].metadata.name}'
```

---

## **3️⃣ Advanced JSONPath Features**

### **3.1 Nested Fields**

* Extract multiple nested fields:

```bash
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[*].name}'
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[*].resources.limits.cpu}'
```

---

### **3.2 Filters with Expressions**

* Example: Get pods with label `app=nginx` and Running:

```bash
kubectl get pods -o jsonpath='{.items[?(@.metadata.labels.app=="nginx" && @.status.phase=="Running")].metadata.name}'
```

---

### **3.3 Array Slicing**

* Get first 3 pods:

```bash
kubectl get pods -o jsonpath='{.items[0:3].metadata.name}'
```

* Get last pod in the list:

```bash
kubectl get pods -o jsonpath='{.items[-1:].metadata.name}'
```

---

### **3.4 Combining Text with JSONPath**

* Example: Show pod name and its node:

```bash
kubectl get pods -o jsonpath='{range .items[*]}Pod: {.metadata.name}, Node: {.spec.nodeName}{"\n"}{end}'
```

---

### **3.5 Using with Services**

* Get service ClusterIP:

```bash
kubectl get svc <service-name> -o jsonpath='{.spec.clusterIP}'
```

* Get all service ports:

```bash
kubectl get svc <service-name> -o jsonpath='{.spec.ports[*].port}'
```

---

### **3.6 Using JSONPath in Scripts**

* Example: Delete all pods with label `app=nginx`:

```bash
kubectl delete pod $(kubectl get pods -l app=nginx -o jsonpath='{.items[*].metadata.name}')
```

---

## **4️⃣ Real-life Scenarios Where JSONPath Helps**

1. **Quickly Get Pod Names / IPs / Nodes**

```bash
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{" -> "}{.status.podIP}{"\n"}{end}'
```

2. **Check Container Images for All Pods**

* Useful before updating or patching images:

```bash
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}: {.spec.containers[*].image}{"\n"}{end}'
```

3. **Filter Running Pods Only**

```bash
kubectl get pods -o jsonpath='{.items[?(@.status.phase=="Running")].metadata.name}'
```

4. **Automation / Scripting**

* Delete pods automatically, get IPs for monitoring, etc.

5. **Inspect Resources Quickly Without Full YAML**

```bash
kubectl get pod <pod> -o jsonpath='{.spec.containers[*].resources.limits.cpu}'
```

6. **Debugging Networking / Service Connectivity**

```bash
kubectl get endpoints <service> -o jsonpath='{.subsets[*].addresses[*].ip}'
```

---

## **5️⃣ Tips & Gotchas**

* JSONPath **does not support all JSONPath features**; use `jq` for complex queries.
* Always wrap expressions in `{}` and quote them to avoid shell expansion.
* Use `range` and `end` to iterate lists.
* Use filters `[?()]` carefully with `@` to reference current object.

---

## **6️⃣ Summary Table of Useful JSONPath Queries**

| Task              | Command                                                                                             |
| ----------------- | --------------------------------------------------------------------------------------------------- |
| List pod names    | `kubectl get pods -o jsonpath='{.items[*].metadata.name}'`                                          |
| Pod name + Node   | `kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"->"}{.spec.nodeName}{"\n"}{end}'` |
| Container images  | `kubectl get pods -o jsonpath='{.items[*].spec.containers[*].image}'`                               |
| Running pods      | `kubectl get pods -o jsonpath='{.items[?(@.status.phase=="Running")].metadata.name}'`               |
| Service ClusterIP | `kubectl get svc <svc> -o jsonpath='{.spec.clusterIP}'`                                             |
| Service ports     | `kubectl get svc <svc> -o jsonpath='{.spec.ports[*].port}'`                                         |

---
