## 🎯 **Demo-06: Helm Install with --generate-name flag**

To install a Helm chart **without explicitly specifying a release name**, using Helm’s `--generate-name` flag — Helm will auto-generate a unique release name.

---

## 🧩 **Pre-requisites**

Before you begin:

```bash
# 1. Verify Helm is installed
helm version

# 2. Verify Kubernetes cluster access
kubectl get nodes

# 3. Check that a namespace (optional) exists or create one
kubectl create namespace demo06
```

---

## 🚀 **Step-1: Add Helm Repository**

Add a chart repository (Bitnami’s NGINX in this example):

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
```

---

## 🚀 **Step-2: Update Helm Repository**

Always update before searching/installing:

```bash
helm repo update
```

---

## 🔍 **Step-3: Search for the Chart**

Check available versions of NGINX chart:

```bash
helm search repo nginx
```

---

## ⚙️ **Step-4: Install the Chart Using `--generate-name`**

Here’s the key part of this demo 👇

```bash
helm install bitnami/nginx --generate-name --namespace demo06
```

**Explanation:**

* `helm install` → installs a Helm chart.
* `bitnami/nginx` → chart name (repo/chart).
* `--generate-name` → auto-generates a random release name.
* `--namespace demo06` → optional, specifies the namespace.

✅ Example output:

```
NAME: nginx-1728935467
LAST DEPLOYED: Fri Oct 31 14:45:56 2025
NAMESPACE: demo06
STATUS: deployed
REVISION: 1
CHART: nginx-18.2.0
APP VERSION: 1.25.3
```

---

## 🧾 **Step-5: Verify the Installation**

Check Helm releases:

```bash
helm list -n demo06
```

✅ Example output:

```
NAME            	NAMESPACE	REVISION	UPDATED                             	STATUS  	CHART        	APP VERSION
nginx-1728935467	demo06   	1       	2025-10-31 14:45:56.123456 +0530 IST	deployed	nginx-18.2.0 	1.25.3
```

---

## 🧱 **Step-6: Check Kubernetes Resources**

Confirm the pod, service, and deployment created by Helm:

```bash
kubectl get all -n demo06
```

Expected:

```
NAME                                      READY   STATUS    RESTARTS   AGE
pod/nginx-1728935467-abc123               1/1     Running   0          1m

NAME                         TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
service/nginx-1728935467     ClusterIP   10.99.12.113    <none>        80/TCP    1m

NAME                                      READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/nginx-1728935467          1/1     1            1           1m
```

---

## 🔧 **Step-7: Access the Application**

Since this chart creates a **ClusterIP** service by default, you can use port-forwarding:

```bash
kubectl port-forward svc/nginx-1728935467 8080:80 -n demo06
```

Now open in browser:
👉 [http://localhost:8080](http://localhost:8080)

---

## 🔁 **Step-8: Uninstall the Release**

Get the auto-generated release name first:

```bash
helm list -n demo06
```

Then uninstall using that name:

```bash
helm uninstall nginx-1728935467 -n demo06
```

---

## 🧹 **Step-9: Cleanup (Optional)**

```bash
kubectl delete namespace demo06
```

---

## 📂 **Files Involved in This Demo**

No custom files are needed because this demo uses an **existing Helm chart**.
However, for your practice structure, you can create a folder:

```
helm-demos/
└── demo-06-generate-name/
    ├── README.md
    ├── commands.sh
```

### ✅ **README.md**

```markdown
# Demo-06: Helm Install with --generate-name

## Objective
Install a Helm chart without specifying a release name using the --generate-name flag.

## Steps
1. Add repo: `helm repo add bitnami https://charts.bitnami.com/bitnami`
2. Update repo: `helm repo update`
3. Search chart: `helm search repo nginx`
4. Install: `helm install bitnami/nginx --generate-name --namespace demo06`
5. Verify: `helm list -n demo06`
6. Check resources: `kubectl get all -n demo06`
7. Access app: `kubectl port-forward svc/<generated-release> 8080:80 -n demo06`
8. Uninstall: `helm uninstall <generated-release> -n demo06`
```

### ✅ **commands.sh**

```bash
#!/bin/bash
# Demo-06: Helm Install with --generate-name

helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm search repo nginx
kubectl create namespace demo06
helm install bitnami/nginx --generate-name --namespace demo06
helm list -n demo06
kubectl get all -n demo06
# Replace <release-name> with the generated one
# helm uninstall <release-name> -n demo06
```

---
