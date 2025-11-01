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

(You already did this — it shows only user-supplied values.)

#### 2️⃣ **Full values including defaults (from the chart + overrides):**

```bash
helm get values my-nginx -n demo09 --all
```

#### 3️⃣ **Default values of the chart (not your release):**

```bash
helm show values nginx
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

## 📂 **Files for Demo-09**

```
helm-demos/
└── demo-09-override-dryrun-debug/
    ├── README.md
    ├── commands.sh
    └── custom-values.yaml
```

---

### ✅ **README.md**

````markdown
# Demo-09: Helm Override Values, --dry-run, --debug, and helm get

## 🎯 Objective
Understand how to:
1. Override chart values.
2. Validate templates using --dry-run and --debug.
3. Retrieve deployed release info using helm get commands.

## 🪜 Steps

### 1️⃣ Add repo and prepare
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
kubectl create namespace demo09
````

### 2️⃣ View default chart values

```bash
helm show values bitnami/nginx > default-values.yaml
```

### 3️⃣ Override values

**Option A – Inline:**

```bash
helm install my-nginx bitnami/nginx --namespace demo09 \
  --set service.type=NodePort --set replicaCount=2
```

**Option B – File:**
Create `custom-values.yaml`:

```yaml
replicaCount: 2
service:
  type: NodePort
```

Then run:

```bash
helm install my-nginx bitnami/nginx -f custom-values.yaml --namespace demo09
```

### 4️⃣ Validate before applying

```bash
helm install my-nginx bitnami/nginx -f custom-values.yaml --namespace demo09 --dry-run --debug
```

### 5️⃣ Deploy

```bash
helm install my-nginx bitnami/nginx -f custom-values.yaml --namespace demo09
```

### 6️⃣ Retrieve information

```bash
helm get all my-nginx -n demo09
helm get values my-nginx -n demo09
helm get manifest my-nginx -n demo09
helm get notes my-nginx -n demo09
```

### 7️⃣ Cleanup

```bash
helm uninstall my-nginx -n demo09
kubectl delete namespace demo09
```

````

---

### ✅ **commands.sh**
```bash
#!/bin/bash
# Demo-09: Helm Override Values, --dry-run, --debug, and helm get

# Setup
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
kubectl create namespace demo09

# View default values
helm show values bitnami/nginx > default-values.yaml

# Custom values
cat <<EOF > custom-values.yaml
replicaCount: 2
service:
  type: NodePort
EOF

# Dry-run and debug
helm install my-nginx bitnami/nginx -f custom-values.yaml --namespace demo09 --dry-run --debug

# Deploy for real
helm install my-nginx bitnami/nginx -f custom-values.yaml --namespace demo09

# Get information
helm get all my-nginx -n demo09
helm get values my-nginx -n demo09
helm get manifest my-nginx -n demo09
helm get notes my-nginx -n demo09

# Cleanup
helm uninstall my-nginx -n demo09
kubectl delete namespace demo09
````

---

✅ **End Result:**
You’ll know how to:

* Override Helm chart values cleanly.
* Validate & debug before deployment.
* Inspect everything Helm deployed.

---

Would you like me to continue with **Demo-10: Helm Upgrade with `--reuse-values` and `--set`** next in the same detailed format?
