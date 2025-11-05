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
> This error is very common, especially in Minikube and other development environments. The error message is very clear:

**`x509: cannot validate certificate for 192.168.49.2 because it doesn't contain any IP SANs"`**

This means the TLS certificate presented by your Minikube nodes (`192.168.49.2` and `192.168.49.3`) does not have the node's IP address in its **Subject Alternative Name (SAN)** field. The Metrics Server, by default, requires a valid TLS certificate to communicate with the kubelets on each node.

## Solution: Fix the Metrics Server Deployment

You need to add specific flags to the Metrics Server container to tell it to skip TLS verification for the kubelet's certificate. This is safe for testing and development environments.

Here are the step-by-step commands to fix this:

### Method 1: Quick Patch (Recommended)

This is the fastest way to fix the issue. It patches the deployment with the necessary arguments.

```bash
# This command adds the required insecure flags to the metrics-server deployment
kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
```

### Method 2: Edit the Deployment Manually

If you prefer to see and edit the configuration directly:

1.  **Edit the deployment:**
    ```bash
    kubectl edit deployment metrics-server -n kube-system
    ```

2.  **Find the `args` section** for the `metrics-server` container. It will look something like this:
    ```yaml
    containers:
    - args:
      - --cert-dir=/tmp
      - --secure-port=4443
      # ... possibly other args ...
      name: metrics-server
      # ...
    ```

3.  **Add the following arguments to the list:** (You can add them anywhere in the `args` list)
    ```yaml
    - --kubelet-insecure-tls
    ```
    *   `--kubelet-insecure-tls`: This is the crucial flag that skips TLS certificate verification.

4.  **Save and exit the editor.** The deployment will automatically restart the pod with the new configuration.

### Method 3: Apply a Fixed Version (Alternative)

You can also download the manifest, modify it, and then apply it. This is useful for automation.

```bash
# Download the manifest
curl -LO https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Edit the file (components.yaml) and find the metrics-server Deployment
# In the args section for the container, add the lines mentioned in Method 2.
# Then apply the modified manifest:
kubectl apply -f components.yaml
```

## Verify the Fix

After applying the fix, wait a minute for the new Metrics Server pod to start and begin collecting data.

1.  **Check that the new pod is running:**
    ```bash
    kubectl get pods -n kube-system -l k8s-app=metrics-server
    # Wait for the status to be 'Running'
    ```

2.  **Test if metrics are now available:**
    ```bash
    # This should now show CPU and memory usage instead of errors or <unknown>
    kubectl top nodes
    ```
    Example of successful output:
    ```
    NAME             CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%
    minikube         150m         7%     1254Mi          33%
    minikube-m02     120m         6%     1024Mi          27%
    ```

3.  **Check the logs of the new Metrics Server pod to confirm no more errors:**
    ```bash
    kubectl logs -n kube-system deployment/metrics-server --tail=10
    ```
    You should no longer see the `Failed to scrape node` TLS errors. Instead, you might see successful log lines.

## Why This Works in a Dev Environment

In a production cluster, the certificates would be properly configured with all the necessary SANs. However, in development environments like Minikube, the certificates are often self-signed and generated quickly without all the proper SAN entries.

The `--kubelet-insecure-tls` flag tells the Metrics Server to accept the kubelet's certificate even if it can't be validated by a trusted CA and doesn't have the correct SANs. This is an acceptable risk for a local development cluster where you trust the nodes.

Your HPA should now start working correctly once the metrics are flowing!
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
while true; do wget -q -O- http://nginx-service; done
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


