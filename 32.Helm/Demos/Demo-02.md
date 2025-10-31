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

