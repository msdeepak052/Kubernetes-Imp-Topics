# 🔹 **1. What is HPA?**

* **HPA (Horizontal Pod Autoscaler)** automatically **scales the number of Pods** in a Deployment, ReplicaSet, or StatefulSet based on observed metrics.
* Commonly used metrics:

  * **CPU utilization** (most common)
  * **Memory usage**
  * **Custom metrics**

**Goal:** Keep your application responsive while efficiently using resources.

---

# 🔹 **2. How HPA Works**

1. Monitor metrics (CPU, memory, custom metrics).
2. Compare actual usage vs desired target (e.g., 50% CPU).
3. Adjust **replica count** up or down to maintain the target.

**Example:**

* Deployment has 2 replicas, CPU target 50%.
* If Pods hit 80% CPU → HPA scales replicas to reduce load.
* If Pods are underutilized → HPA scales down.

---

# 🔹 **3. Pre-requisites to Use HPA**

1. Kubernetes cluster **version ≥ 1.18** (HPA is built-in).
2. Metrics server installed (for CPU/Memory metrics).

**Check if metrics-server is installed:**

```bash
kubectl get deployment metrics-server -n kube-system
```

**Install metrics-server if not present:**

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

**Verify metrics-server works:**

```bash
kubectl top nodes
kubectl top pods
```

---

# 🔹 **4. Sample Deployment YAML**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx
        resources:
          requests:
            cpu: 100m
          limits:
            cpu: 200m
```

* **Important:** HPA requires **CPU requests** to be set.

---

# 🔹 **5. HPA YAML Example**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nginx-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx-deployment
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

✅ **Interpretation:**

* HPA will scale `nginx-deployment` between 2 and 5 replicas.
* Target **average CPU utilization** = 50%.

---

# 🔹 **6. Create HPA in Cluster**

```bash
# Apply deployment
kubectl apply -f nginx-deployment.yaml

# Apply HPA
kubectl apply -f nginx-hpa.yaml

# Verify HPA
kubectl get hpa
kubectl describe hpa nginx-hpa
```

---

# 🔹 **7. Test HPA**

1. Generate CPU load on Pods:

```bash
kubectl run -i --tty load-generator --image=busybox --restart=Never -- /bin/sh
# Inside Pod:
while true; do wget -q -O- http://nginx-deployment; done
```

2. Monitor HPA scaling:

```bash
kubectl get hpa -w
kubectl get pods -o wide
```

* You will see **replicas increasing** when CPU usage goes above 50% and **scaling down** when load decreases.

---

# 🔹 **8. Key Notes**

* **minReplicas** → minimum number of Pods.
* **maxReplicas** → maximum number of Pods.
* **Target metric** → CPU, memory, or custom metric.
* **autoscaling/v2** API supports multiple metrics and external metrics.

---
