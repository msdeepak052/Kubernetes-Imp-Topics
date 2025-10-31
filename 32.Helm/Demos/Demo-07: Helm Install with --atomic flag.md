# **Demo-07: Helm Install with `--atomic` flag**

## 🎯 **Demo-07 Goal**

To install a Helm chart using the **`--atomic` flag**, which ensures that if the installation fails for any reason, **Helm will automatically roll back** the release to maintain a clean cluster state.

---

## 🧩 **Pre-requisites**

Make sure you have:

```bash
helm version
kubectl get nodes
kubectl create namespace demo07
```

---

## 🧠 **Concept Explanation: `--atomic` Flag**

When you use:

```bash
helm install <release> <chart> --atomic
```

👉 Helm will:

* Automatically **rollback** the release if any part of the installation fails.
* Clean up all resources created during that failed attempt.
* Set the release status to `FAILED`.

Without `--atomic`, you’d need to manually rollback or delete failed resources.

---

## 🚀 **Step-1: Add and Update Helm Repository**

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

---

## 🔍 **Step-2: Search for the Chart**

```bash
helm search repo nginx
```

---

## ⚙️ **Step-3: Install the Chart with `--atomic` Flag**

Here’s the main command of the demo 👇

```bash
helm install my-nginx bitnami/nginx --namespace demo07 --atomic
```

**Explanation:**

* `my-nginx` → release name.
* `bitnami/nginx` → chart name.
* `--atomic` → enables rollback if anything fails.
* `--namespace demo07` → deploys in a dedicated namespace.

✅ Example successful output:

```
NAME: my-nginx
LAST DEPLOYED: Fri Oct 31 15:22:48 2025
NAMESPACE: demo07
STATUS: deployed
REVISION: 1
CHART: nginx-18.2.0
APP VERSION: 1.25.3
```

---

## ⚠️ **Step-4: Simulate a Failure (Optional to See Rollback)**

To *test* the `--atomic` flag, intentionally break something — for example, provide an invalid image value:

```bash
helm install test-fail bitnami/nginx --set image.repository=invalid-image-repo --atomic -n demo07
```

🔴 Output:

```
Error: INSTALLATION FAILED: Kubernetes cluster unreachable: no such host
ROLLING BACK...
Error: INSTALLATION FAILED: unable to pull image invalid-image-repo: rollback completed
```

✅ Helm automatically cleans up the failed resources.

Check:

```bash
helm list -n demo07
```

You’ll see that `test-fail` release doesn’t exist (because rollback deleted it).

---

## 🧾 **Step-5: Verify the Successful Installation**

```bash
helm list -n demo07
```

Example output:

```
NAME     	NAMESPACE	REVISION	STATUS  	CHART       	APP VERSION
my-nginx 	demo07   	1       	deployed	nginx-18.2.0	1.25.3
```

---

## 🧱 **Step-6: Check Kubernetes Resources**

```bash
kubectl get all -n demo07
```

You should see:

```
NAME                            READY   STATUS    RESTARTS   AGE
pod/my-nginx-5ccdbf47d7-xyz12   1/1     Running   0          2m

NAME                TYPE        CLUSTER-IP     PORT(S)   AGE
service/my-nginx    ClusterIP   10.98.52.113   80/TCP    2m
```

---

## 🔧 **Step-7: Access the Application**

Use port-forwarding:

```bash
kubectl port-forward svc/my-nginx 8081:80 -n demo07
```

Open: 👉 [http://localhost:8081](http://localhost:8081)

---

## 🧹 **Step-8: Uninstall the Release**

```bash
helm uninstall my-nginx -n demo07
kubectl delete namespace demo07
```

---
