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

### Full hands-on HPA demo
---

## **1️⃣ Prerequisites**

* Kubernetes cluster (kubeadm or Minikube)
* Metrics Server installed and working (`kubectl top nodes` shows metrics)
* `kubectl` configured

---

## **2️⃣ Step 1 — Create Deployment**

We’ll deploy a simple **Nginx app** that HPA can scale.

**File: `webapp-deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
  labels:
    app: webapp
spec:
  replicas: 1
  selector:
    matchLabels:
      app: webapp
  template:
    metadata:
      labels:
        app: webapp
    spec:
      containers:
      - name: nginx
        image: nginx:stable
        resources:
          requests:
            cpu: 100m
          limits:
            cpu: 500m
        ports:
        - containerPort: 80
```

**Deploy it:**

```bash
kubectl apply -f webapp-deployment.yaml
```

---

## **3️⃣ Step 2 — Expose Deployment via Service**

**File: `webapp-service.yaml`**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: webapp-service
spec:
  selector:
    app: webapp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: ClusterIP
```

**Apply:**

```bash
kubectl apply -f webapp-service.yaml
```

---

## **4️⃣ Step 3 — Create Horizontal Pod Autoscaler**

We’ll autoscale based on CPU usage.

**File: `webapp-hpa.yaml`**

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
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
```

**Apply HPA:**

```bash
kubectl apply -f webapp-hpa.yaml
```

---

## **5️⃣ Step 4 — Verify HPA and Metrics**

Check HPA:

```bash
kubectl get hpa
```

Expected output (initially, replicas = 1):

```
NAME         REFERENCE       TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
webapp-hpa   Deployment/webapp  0%/50%    1         5         1          1m
```

Check pod CPU usage:

```bash
kubectl top pods
kubectl top nodes
```

---

## **6️⃣ Step 5 — Generate Load**

Create a temporary pod to stress Nginx:

```bash
kubectl run load-generator --rm -i --tty --image=busybox /bin/sh
```

Inside the pod, run:

```bash
while true; do wget -q -O- http://webapp-service.default.svc.cluster.local; done
```

✅ This generates CPU usage for your Nginx pods.

---

## **7️⃣ Step 6 — Watch HPA Scale Up**

In another terminal:

```bash
kubectl get hpa -w
```

* You will see `CURRENT CPU%` increase
* HPA will **increase replicas** automatically (up to maxReplicas = 5)

You can also watch pods:

```bash
kubectl get pods -w
```

---

## **8️⃣ Step 7 — Clean Up**

After demo:

```bash
kubectl delete -f webapp-hpa.yaml
kubectl delete -f webapp-service.yaml
kubectl delete -f webapp-deployment.yaml
kubectl delete pod load-generator
```

---

### **✅ Key Learning Points**

1. **Metrics Server is required** for HPA.
2. HPA scales **deployment pods** automatically based on **metrics**.
3. CPU utilization triggers scaling — you can also use **memory or custom metrics**.
4. `kubectl top pods` is essential for verifying metrics.

---



