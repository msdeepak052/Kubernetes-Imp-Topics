# **Demo-02: Helm Repo, Search, List, Install and Uninstall**


## 🧭 Objective

Learn how to:

* Add and manage Helm repositories
* Search for charts
* Install and uninstall Helm charts
* List installed charts

---

## 🧱 Prerequisites

Ensure the following are ready before you begin:

| Tool               | Description                                         | Command to Check    |
| ------------------ | --------------------------------------------------- | ------------------- |
| Docker             | Running Kubernetes (via Docker Desktop or Minikube) | `docker --version`  |
| Kubernetes Cluster | Local cluster (Docker Desktop or Minikube)          | `kubectl get nodes` |
| Helm CLI           | Installed and configured                            | `helm version`      |

If Helm isn’t installed:

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

---

## 🪜 Step-by-Step Implementation

### **Step 1: Add a Helm Repository**

Helm uses repositories (repos) as sources for charts. Let’s add the **Bitnami** repo — a popular source for production-grade charts.

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
```

✅ **Expected Output:**

```
"bitnami" has been added to your repositories
```

---

### **Step 2: List the Repositories**

Check which repos are configured in your Helm setup:

```bash
helm repo list
```

✅ **Expected Output:**

```
NAME    URL
bitnami https://charts.bitnami.com/bitnami
```

---

### **Step 3: Search for a Chart in a Repo**

Example: Search for the **nginx** chart in Bitnami repo.

```bash
helm search repo bitnami/nginx
```

✅ **Expected Output:**

```
NAME            	CHART VERSION	APP VERSION	DESCRIPTION
bitnami/nginx   	15.9.2       	1.25.3     	NGINX Open Source is a web server...
```

---

### **Step 4: Install a Helm Chart**

Let’s install **nginx** from the Bitnami repo.

```bash
helm install my-nginx bitnami/nginx
```

✅ **Expected Output:**

```
NAME: my-nginx
LAST DEPLOYED: Fri Oct 31 19:20:43 2025
NAMESPACE: default
STATUS: deployed
REVISION: 1
NOTES:
1. Get the application URL by running these commands:
   export SERVICE_IP=$(kubectl get svc --namespace default my-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
   echo "http://$SERVICE_IP/"
```

## 🧩 **Standard Helm Install Syntax**

```bash
helm install <release-name> <chart> [flags]
```

---

## 📘 **Syntax Explanation**

| Component        | Description                                                                                                                            | Example                                                                 |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| `helm`           | The Helm CLI command itself                                                                                                            | —                                                                       |
| `install`        | Subcommand used to deploy (install) a Helm chart                                                                                       | —                                                                       |
| `<release-name>` | A name you assign to this deployment. It uniquely identifies this release within the namespace.                                        | `my-nginx`                                                              |
| `<chart>`        | The chart to install — can be a chart reference (`repo/chart-name`), a local chart directory (`./mychart`), or a `.tgz` chart package. | `bitnami/nginx`                                                         |
| `[flags]`        | Optional parameters to customize the installation.                                                                                     | `--namespace`, `--set`, `--values`, `--atomic`, `--generate-name`, etc. |

---

## 💡 **Example (Your Command)**

```bash
helm install my-nginx bitnami/nginx
```

### Breakdown:

| Part              | Meaning                                                         |
| ----------------- | --------------------------------------------------------------- |
| `helm`            | Invokes Helm CLI                                                |
| `install`         | Tells Helm to install a chart                                   |
| `my-nginx`        | Your chosen **release name**                                    |
| `bitnami/nginx`   | The **chart reference** from the Bitnami repository             |
| *(no flags used)* | Means it uses **default values** from the chart’s `values.yaml` |

---

## ⚙️ **More Examples with Flags**

| Command                                                               | Description                                        |
| --------------------------------------------------------------------- | -------------------------------------------------- |
| `helm install my-nginx bitnami/nginx --namespace web`                 | Installs in a specific namespace (`web`)           |
| `helm install my-nginx bitnami/nginx --set service.type=LoadBalancer` | Overrides default chart values inline              |
| `helm install my-nginx bitnami/nginx -f custom-values.yaml`           | Installs using your custom `values.yaml`           |
| `helm install --generate-name bitnami/nginx`                          | Automatically generates a random release name      |
| `helm install my-nginx bitnami/nginx --atomic`                        | Rolls back automatically if the installation fails |

---

## 📋 **Quick Syntax Reference Summary**

| Element            | Required | Description                             | Example                  |
| ------------------ | -------- | --------------------------------------- | ------------------------ |
| `<release-name>`   | ✅        | Custom name for your release            | `my-nginx`               |
| `<chart>`          | ✅        | Chart source (repo/chart, dir, or .tgz) | `bitnami/nginx`          |
| `--namespace`      | ❌        | Kubernetes namespace to deploy into     | `--namespace web`        |
| `--set`            | ❌        | Inline variable override                | `--set image.tag=latest` |
| `-f` or `--values` | ❌        | Specify custom values file              | `-f myvalues.yaml`       |
| `--version`        | ❌        | Specify chart version                   | `--version 15.9.2`       |
| `--atomic`         | ❌        | Rollback if install fails               | `--atomic`               |
| `--generate-name`  | ❌        | Auto-generate release name              | `--generate-name`        |


---

### **Step 5: Verify Installation**

Check the running releases:

```bash
helm list
```

✅ **Expected Output:**

```
NAME      	NAMESPACE	REVISION	UPDATED                                	STATUS  	CHART       	APP VERSION
my-nginx  	default  	1       	2025-10-31 19:20:43.342717 +0530 IST	deployed	nginx-15.9.2	1.25.3
```

Also verify via Kubernetes:

```bash
kubectl get pods
kubectl get svc
```

---

### **Step 6: Uninstall the Helm Release**

When done, uninstall the nginx release:

```bash
helm uninstall my-nginx
```

✅ **Expected Output:**

```
release "my-nginx" uninstalled
```

---

### **Step 7: Verify Removal**

Confirm it’s gone:

```bash
helm list
```

✅ Should show **no releases**.

Also check Kubernetes:

```bash
kubectl get all
```

---

## 📂 Files Involved

This demo doesn’t require you to manually create any files — Helm pulls everything from the **Bitnami repo** automatically.
However, here’s what happens behind the scenes:

| File / Folder                      | Description                                | Location                               |
| ---------------------------------- | ------------------------------------------ | -------------------------------------- |
| `~/.config/helm/repositories.yaml` | Stores repo info (like Bitnami URL)        | Created after `helm repo add`          |
| `/tmp/helm` or `$HOME/.cache/helm` | Cached chart files                         | Auto-managed by Helm                   |
| Kubernetes manifests               | Generated temporarily from chart templates | Stored in cluster (via `helm install`) |

---

## 🧹 Cleanup Commands

If you want to reset your environment:

```bash
helm uninstall my-nginx
helm repo remove bitnami
```

---

## 🧠 Summary

| Command                               | Purpose                           |
| ------------------------------------- | --------------------------------- |
| `helm repo add <name> <url>`          | Add a Helm chart repository       |
| `helm repo list`                      | View available repositories       |
| `helm search repo <chart>`            | Search for charts in repositories |
| `helm install <release> <repo/chart>` | Install a Helm chart              |
| `helm list`                           | List installed Helm releases      |
| `helm uninstall <release>`            | Uninstall a Helm release          |

---

