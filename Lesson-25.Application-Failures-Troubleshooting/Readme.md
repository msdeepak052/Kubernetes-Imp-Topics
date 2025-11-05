# **🔹 Kubernetes Application Failure Troubleshooting**

We’ll categorize failures into **common real-world scenarios**:

---

## **1️⃣ Pod Crash / CrashLoopBackOff**

**Symptoms:**

* Pod status shows `CrashLoopBackOff` or `Error`.
* Logs show repeated start and crash.

**Common Causes:**

* Wrong container command or args.
* Missing environment variables.
* Application dependency not available.

**Troubleshooting Steps:**

1. Check pod status:

```bash
kubectl get pods -n <namespace>
kubectl describe pod <pod-name>
```

2. Check container logs:

```bash
kubectl logs <pod-name> -c <container-name>
```

3. Check events:

```bash
kubectl get events -n <namespace> --sort-by='.lastTimestamp'
```

**Example Fix:**

* Update container command or fix environment variables in Deployment YAML.

---

## **2️⃣ Pending Pod**

**Symptoms:**

* Pod stuck in `Pending`.

**Common Causes:**

* Resource requests too high.
* Node not ready or tainted.
* Unschedulable due to affinity rules.

**Troubleshooting Steps:**

1. Describe pod:

```bash
kubectl describe pod <pod-name>
```

Check `Events` for `Insufficient CPU/Memory` or `node(s) didn't match`.

2. Check node status:

```bash
kubectl get nodes
kubectl describe node <node-name>
```

**Fix:**

* Lower resource requests.
* Tolerate node taints if necessary.
* Add more nodes to cluster.

---

## **3️⃣ ImagePullBackOff / ErrImagePull**

**Symptoms:**

* Pod stuck with `ImagePullBackOff`.
* Event shows `Failed to pull image`.

**Troubleshooting Steps:**

1. Describe pod to see error:

```bash
kubectl describe pod <pod-name>
```

2. Verify image name and tag:

```bash
docker pull <image>
```

3. If private registry, check secret:

```bash
kubectl get secret
kubectl describe secret <secret-name>
```

**Fix:**

* Correct image name or tag.
* Attach proper imagePullSecrets in deployment.

---

## **4️⃣ Application Not Serving Traffic**

**Symptoms:**

* Service accessible but returns 404 or 503.
* Ingress returns 404.

**Common Causes:**

* Service selector mismatch with pod labels.
* Ingress misconfiguration.
* Path mismatch in Ingress rules.

**Troubleshooting Steps:**

1. Check pods:

```bash
kubectl get pods -l app=<app-name>
```

2. Check service endpoints:

```bash
kubectl get endpoints <service-name>
```

3. Check ingress rules:

```bash
kubectl describe ingress <ingress-name>
```

4. Curl pod directly:

```bash
kubectl exec -it <pod-name> -- curl http://localhost:80
```

**Fix:**

* Correct service selectors or ingress paths.
* Ensure backend pods are running.

---

## **5️⃣ Environment / Config Issues**

**Symptoms:**

* Application fails due to missing config or secrets.
* Pod logs show `missing environment variable` or `config file not found`.

**Troubleshooting Steps:**

1. Check pod spec for env vars:

```bash
kubectl describe pod <pod-name>
```

2. Check ConfigMaps and Secrets:

```bash
kubectl get configmap
kubectl get secret
kubectl describe configmap <name>
kubectl describe secret <name>
```

3. Verify mount paths if using volumes.

**Fix:**

* Correct ConfigMap/Secret references.
* Ensure proper volume mounts.

---

## **6️⃣ Networking / DNS Issues**

**Symptoms:**

* Pod cannot reach other services.
* Curl fails inside pod (`host not found`).

**Troubleshooting Steps:**

1. Check pod DNS resolution:

```bash
kubectl exec -it <pod-name> -- nslookup <service-name>
```

2. Check CNI plugin status:

```bash
kubectl get pods -n kube-system
kubectl describe daemonset <cni-plugin>
```

3. Ping other pods or service IPs:

```bash
kubectl exec -it <pod-name> -- ping <service-ip>
```

**Fix:**

* Fix CNI plugin.
* Check NetworkPolicies for blocked traffic.

---

## **7️⃣ Resource / Performance Issues**

**Symptoms:**

* Application slow, high latency.
* Pod killed due to `OOMKilled`.

**Troubleshooting Steps:**

1. Check pod resource usage:

```bash
kubectl top pod <pod-name>
kubectl top node
```

2. Check HPA or limits:

```bash
kubectl get hpa
kubectl describe hpa <hpa-name>
```

3. Check events:

```bash
kubectl describe pod <pod-name>
```

**Fix:**

* Increase resources or limits.
* Configure HPA for scaling.
* Investigate memory leaks in application.

---

## **8️⃣ Logging / Observability Issues**

* Use centralized logging (ELK, Loki, etc.) to check application logs.
* Use Prometheus/Grafana to monitor CPU, memory, and request metrics.

**Example:**

```bash
kubectl logs -f <pod-name> -c <container-name>
```

---

## **9️⃣ HPA Not Working**

**Symptoms:**

* Application CPU load high, but HPA not scaling.

**Troubleshooting Steps:**

1. Check metrics-server:

```bash
kubectl get deployment metrics-server -n kube-system
kubectl logs -n kube-system <metrics-server-pod>
```

2. Check HPA:

```bash
kubectl get hpa
kubectl describe hpa <hpa-name>
```

**Fix:**

* Ensure metrics-server is running.
* Check resource requests in pod spec.

---

## **10️⃣ Stateful / Database Issues**

**Symptoms:**

* Application cannot connect to database.
* PVC not bound or `Pending`.

**Troubleshooting Steps:**

1. Check PVC status:

```bash
kubectl get pvc
kubectl describe pvc <pvc-name>
```

2. Check PVs:

```bash
kubectl get pv
kubectl describe pv <pv-name>
```

3. Check pod logs for DB connection errors.

**Fix:**

* Correct storage class or PV.
* Ensure database service is accessible.

---

## **💡 General Troubleshooting Commands**

```bash
kubectl get pods -n <namespace>
kubectl describe pod <pod-name>
kubectl logs <pod-name> [-c container]
kubectl exec -it <pod-name> -- /bin/sh
kubectl get events -n <namespace> --sort-by='.lastTimestamp'
kubectl top pod <pod-name>
kubectl top node
```

**Tips:**

* Always check **Events first**.
* Use **describe** to see configuration mismatches.
* Logs are your first clue to runtime issues.
* Resource issues are often overlooked — check CPU/memory limits.

---

