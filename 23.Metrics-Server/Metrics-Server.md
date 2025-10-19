# Metrics-Server --  HPA

## **1️⃣ What is Metrics Server?**

* **Metrics Server** is a **cluster-wide aggregator of resource metrics** in Kubernetes.
* It collects **CPU and memory usage** from **kubelets** on all nodes and exposes them via the **Kubernetes API**.
* Other components use it:

  * **kubectl top** (pods and nodes resource usage)
  * **Horizontal Pod Autoscaler (HPA)**

---

### **Why do we need it?**

1. **Monitor resource usage:**

   * Example: See which pod is using the most CPU or memory:

     ```bash
     kubectl top pod
     kubectl top node
     ```
2. **Enable HPA (Horizontal Pod Autoscaler):**

   * Example: Automatically scale pods based on CPU utilization:

     ```yaml
     apiVersion: autoscaling/v2
     kind: HorizontalPodAutoscaler
     metadata:
       name: webapp-hpa
     spec:
       scaleTargetRef:
         apiVersion: apps/v1
         kind: Deployment
         name: webapp
       minReplicas: 2
       maxReplicas: 5
       metrics:
       - type: Resource
         resource:
           name: cpu
           target:
             type: Utilization
             averageUtilization: 50
     ```

Without metrics-server, **kubectl top** and HPA won’t work.

---

## **2️⃣ Metrics Server Architecture & Flow**

1. Metrics Server scrapes **metrics from kubelets** on each node.
2. Kubelets expose `/metrics/resource` endpoint via **HTTPS**.
3. Metrics Server aggregates this data and exposes it through the **Kubernetes API**.
4. Other components (kubectl top, HPA) query Metrics Server API.

---

## **3️⃣ Install Metrics Server on kubeadm cluster**

**Step 1 — Clone Metrics Server manifests**

```bash
git clone https://github.com/kubernetes-sigs/metrics-server
cd metrics-server
```

**Step 2 — Apply the manifests**

```bash
kubectl apply -f manifests/base
```

✅ This deploys Metrics Server in the `kube-system` namespace.

---

### **Step 3 — Tweak for insecure TLS (common in kubeadm clusters)**

* In kubeadm clusters, kubelets often use **self-signed certificates**, so Metrics Server may fail with TLS errors.
* Solution: Add the flag `--kubelet-insecure-tls`.

**Edit the deployment:**

```bash
kubectl -n kube-system edit deployment metrics-server
```

* Under `containers` → `args`, add:

```yaml
- --kubelet-insecure-tls
```

Example:

```yaml
spec:
  containers:
  - name: metrics-server
    image: k8s.gcr.io/metrics-server/metrics-server:v0.8.7
    args:
    - --cert-dir=/tmp
    - --secure-port=4443
    - --kubelet-preferred-address-types=InternalIP
    - --kubelet-insecure-tls   # <-- added this
```

Save and exit.

---

**Step 4 — Verify installation**

```bash
kubectl get pods -n kube-system
```

* You should see `metrics-server` pod running.

Test with:

```bash
kubectl top nodes
kubectl top pods -A
```

✅ You should see CPU and memory usage metrics.

---

### **4️⃣ Common Errors & Fixes**

| Error                                           | Cause                           | Fix                               |
| ----------------------------------------------- | ------------------------------- | --------------------------------- |
| `x509: certificate signed by unknown authority` | Kubelet TLS cert is self-signed | Add `--kubelet-insecure-tls` flag |
| `metrics API not available`                     | Metrics server not running      | Check pod logs and events         |

---

### **5️⃣ Example Scenario**

**Scenario:** Auto-scaling a web application based on CPU

1. Deploy your app:

```bash
kubectl create deployment webapp --image=nginx
kubectl expose deployment webapp --port=80
```

2. Create HPA (requires metrics-server):

```bash
kubectl autoscale deployment webapp --cpu-percent=50 --min=2 --max=5
```

3. Generate load to test auto-scaling:

```bash
kubectl run -i --tty load-generator --image=busybox /bin/sh
# inside pod
while true; do wget -q -O- http://webapp; done
```

4. Watch scaling:

```bash
kubectl get hpa -w
```

✅ Pods scale automatically based on CPU because metrics-server is feeding metrics.

---

If you want, I can create a **ready-to-run manifest specifically for kubeadm clusters** with `--kubelet-insecure-tls` already included, so you just apply it.

Do you want me to do that?
