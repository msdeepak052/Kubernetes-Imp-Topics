# **Demo-08: Helm with Kubernetes Namespaces** 

This demo focuses on how **Helm interacts with Kubernetes namespaces** — how to **install, list, and manage releases** in different namespaces, and why this is important in real-world DevOps use cases.

---

## 🎯 **Goal**

To understand how **Helm works with Kubernetes namespaces**, including:

* Installing a chart into a specific namespace
* Listing releases per namespace
* Managing multiple releases across namespaces
* Observing what happens when a namespace doesn’t exist

---

## 🧠 **Concept Overview**

Namespaces in Kubernetes are **logical partitions** used to isolate workloads.

Helm uses namespaces to:

* Store release metadata (in secrets/configmaps)
* Deploy resources within that namespace
* Separate releases with the same name across environments (e.g., dev, staging, prod)

By default, Helm installs into the **“default”** namespace unless you specify one using `--namespace`.

---

## 🧩 **Pre-requisites**

Ensure the following before starting:

```bash
helm version
kubectl get nodes
```

---

## ⚙️ **Step-1: Create Multiple Namespaces**

We’ll use two namespaces: `dev` and `prod`.

```bash
kubectl create namespace dev
kubectl create namespace prod
kubectl get namespaces
```

✅ Expected:

```
NAME              STATUS   AGE
default           Active   15h
kube-system       Active   15h
dev               Active   10s
prod              Active   10s
```

---

## 🚀 **Step-2: Add & Update a Helm Repository**

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

---

## 🧱 **Step-3: Install Charts in Different Namespaces**

### a) Install in `dev` Namespace

```bash
helm install my-nginx bitnami/nginx --namespace dev
```

### b) Install the Same Chart in `prod` Namespace

```bash
helm install my-nginx bitnami/nginx --namespace prod
```

✅ Explanation:

* Both releases have the same name (`my-nginx`)
* But are isolated by their namespaces (`dev` vs `prod`)

---

## 🧾 **Step-4: Verify Installations**

### Check releases in `dev`

```bash
helm list -n dev
```

### Check releases in `prod`

```bash
helm list -n prod
```

Example:

```
NAME     	NAMESPACE	REVISION	STATUS  	CHART       	APP VERSION
my-nginx 	dev       	1       	deployed	nginx-18.2.0	1.25.3
my-nginx 	prod      	1       	deployed	nginx-18.2.0	1.25.3
```

Helm treats them as **two separate releases** because of namespace separation.

---

## 🔍 **Step-5: Check Resources in Each Namespace**

### In `dev`

```bash
kubectl get all -n dev
```

### In `prod`

```bash
kubectl get all -n prod
```

You’ll see two independent sets of pods, services, and deployments — each isolated within its namespace.

---

## ⚠️ **Step-6: Install Without Namespace (Default Behavior)**

If you don’t specify a namespace:

```bash
helm install my-nginx-default bitnami/nginx
```

This installs in the **default** namespace.
Check:

```bash
helm list -n default
kubectl get all -n default
```

---

## 🔧 **Step-7: Access the Application**

Port-forward one of them:

```bash
kubectl port-forward svc/my-nginx 8080:80 -n dev
```

Visit 👉 [http://localhost:8080](http://localhost:8080)

Each namespace’s NGINX runs independently, so `dev` and `prod` don’t interfere with each other.

---

## 🧹 **Step-8: Cleanup**

```bash
helm uninstall my-nginx -n dev
helm uninstall my-nginx -n prod
helm uninstall my-nginx-default -n default
kubectl delete namespace dev prod
```

---

## 📂 **Files for Demo-08: Helm with Namespaces**

```
helm-demos/
└── demo-08-helm-namespaces/
    ├── README.md
    ├── commands.sh
```

---

### ✅ **README.md**

````markdown
# Demo-08: Helm with Kubernetes Namespaces

## 🎯 Objective
Learn how Helm interacts with Kubernetes namespaces to manage isolated releases.

## 🧠 Key Points
- Helm installs into the "default" namespace if none is specified.
- The same release name can exist in different namespaces independently.
- Helm release metadata (ConfigMaps/Secrets) is stored per namespace.

## 🪜 Steps
1. Create namespaces:
   ```bash
   kubectl create namespace dev
   kubectl create namespace prod
````

2. Add and update repo:

   ```bash
   helm repo add bitnami https://charts.bitnami.com/bitnami
   helm repo update
   ```
3. Install charts:

   ```bash
   helm install my-nginx bitnami/nginx --namespace dev
   helm install my-nginx bitnami/nginx --namespace prod
   ```
4. Verify releases:

   ```bash
   helm list -n dev
   helm list -n prod
   ```
5. Check Kubernetes objects:

   ```bash
   kubectl get all -n dev
   kubectl get all -n prod
   ```
6. Optional default install:

   ```bash
   helm install my-nginx-default bitnami/nginx
   ```
7. Cleanup:

   ```bash
   helm uninstall my-nginx -n dev
   helm uninstall my-nginx -n prod
   helm uninstall my-nginx-default -n default
   kubectl delete namespace dev prod
   ```

````

---

