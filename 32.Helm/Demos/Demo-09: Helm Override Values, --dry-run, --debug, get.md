# **Demo-09: Helm Override Values, `--dry-run`, `--debug`, and `helm get` commands** 

## 🎯 **Demo-09 Goal**

Learn how to:

1. Override default chart values using `--set` and `-f values.yaml`.
2. Validate and debug deployments without applying them using `--dry-run` and `--debug`.
3. Retrieve deployed release information using `helm get` commands.

---

## 🧩 **Pre-requisites**

Make sure Helm and your cluster are ready:

```bash
helm version
kubectl get nodes
kubectl create namespace demo09
```

Add the Bitnami repo:

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

---

## ⚙️ **Step-1: Understand Default Chart Values**

Every chart comes with a `values.yaml` file that defines default configuration.

To view the defaults for NGINX:

```bash
helm show values bitnami/nginx > default-values.yaml
```

Open it (optional):

```bash
cat default-values.yaml
```

---

## 🧾 **Step-2: Override Chart Values**

There are **two main ways** to override values:

### a) Inline using `--set`

```bash
helm install my-nginx bitnami/nginx \
  --namespace demo09 \
  --set service.type=NodePort \
  --set replicaCount=2
```

### b) Using a custom `values.yaml`

Create a new file `custom-values.yaml`:

```yaml
replicaCount: 2
service:
  type: NodePort
```

Then install using:

```bash
helm install my-nginx bitnami/nginx \
  -f custom-values.yaml \
  --namespace demo09
```

✅ **Result:**
Helm merges your overrides with chart defaults.

---

## 🧪 **Step-3: Test with `--dry-run` (Preview Installation)**

Before deploying, preview everything Helm will apply to the cluster:

```bash
helm install my-nginx bitnami/nginx \
  -f custom-values.yaml \
  --namespace demo09 \
  --dry-run
```

**Output:** Helm renders all manifests (YAMLs) but does **not** deploy them.

Useful for validating syntax, templates, and parameters.

---

## 🧰 **Step-4: Debug Template Rendering with `--debug`**

Combine both:

```bash
helm install my-nginx bitnami/nginx \
  -f custom-values.yaml \
  --namespace demo09 \
  --dry-run --debug
```

**`--debug`** adds verbose output showing:

* Rendered YAML
* Chart path and revision
* Values merged from `values.yaml` + overrides

This is essential for troubleshooting misconfigured charts.

---

## 🚀 **Step-5: Actual Deployment**

Once verified:

```bash
helm install my-nginx bitnami/nginx \
  -f custom-values.yaml \
  --namespace demo09
```

Check:

```bash
helm list -n demo09
kubectl get all -n demo09
```

---

## 📥 **Step-6: Use `helm get` Commands**

Helm stores release info in the namespace as Secrets.
These commands retrieve that information easily:

| Command                                | Description                                |
| -------------------------------------- | ------------------------------------------ |
| `helm get all my-nginx -n demo09`      | Shows all stored info about the release    |
| `helm get values my-nginx -n demo09 or helm get values my-nginx -n demo09 --all`   | Shows merged values used in deployment     |
| `helm get manifest my-nginx -n demo09` | Shows final rendered Kubernetes manifests  |
| `helm get notes my-nginx -n demo09`    | Shows post-installation notes/instructions |
| `helm get hooks my-nginx -n demo09`    | Displays lifecycle hooks (if any)          |

Example:

```bash
helm get values my-nginx -n demo09
```
### ✅ Correct Usage

If you want to see:

#### 1️⃣ **Values used in your deployed release (in namespace demo09):**

```bash
helm get values my-nginx -n demo09
```

#### 2️⃣ **Full values including defaults (from the chart + overrides):**

```bash
helm get values my-nginx -n demo09 --all
```

#### 3️⃣ **Default values of the chart (not your release):**

```bash
helm show values bitnami/nginx
```

or (if you installed from Bitnami repo)

```bash
helm show values bitnami/nginx
```

---

## 🧹 **Step-7: Cleanup**

```bash
helm uninstall my-nginx -n demo09
kubectl delete namespace demo09
```

---
