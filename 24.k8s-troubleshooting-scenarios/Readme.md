# **Kubernetes Troubleshooting Guide – Real World Scenarios**

We can classify troubleshooting into **5 major areas**:

1. **Pod & Deployment Issues**
2. **Networking & Services**
3. **Storage & PVC Issues**
4. **Performance & Resource Issues**
5. **Cluster & Control Plane Issues**

---

## **1️⃣ Pod & Deployment Issues**

### **Scenario 1: Pod is stuck in `Pending`**

**Symptoms:**

```bash
kubectl get pods
NAME         READY   STATUS    RESTARTS   AGE
webapp-1     0/1     Pending   0          5m
```

**Possible Causes:**

* No nodes with enough resources (CPU/memory)
* NodeSelector or Tolerations mismatch
* PVC not bound (volume issues)

**Troubleshooting Steps:**

```bash
kubectl describe pod webapp-1
```

* Look under `Events` → you may see messages like:

  * `0/1 nodes are available: 1 Insufficient cpu.`
  * `pod has unbound PersistentVolumeClaims`

**Fixes:**

* Check node resources:

```bash
kubectl describe node <node-name>
kubectl top node
```

* Adjust resource requests/limits in deployment
* Adjust NodeSelector/Tolerations
* Check PVC and StorageClass

---

### **Scenario 2: Pod CrashLoopBackOff**

**Symptoms:**

```bash
kubectl get pods
webapp-1   0/1   CrashLoopBackOff   5   2m
```

**Troubleshooting Steps:**

1. Check logs:

```bash
kubectl logs webapp-1
```

2. If multi-container pod, specify container:

```bash
kubectl logs webapp-1 -c <container-name>
```

3. Describe pod for events:

```bash
kubectl describe pod webapp-1
```

**Common Causes:**

* Application error (wrong image, config, missing env vars)
* Wrong command/entrypoint
* Permissions issues

**Fixes:**

* Correct image or env vars
* Ensure ConfigMap/Secrets are mounted correctly

---

### **Scenario 3: Deployment not updating**

**Symptoms:**

* You applied a new image or change but pods stay old.

**Troubleshooting Steps:**

```bash
kubectl rollout status deployment webapp
kubectl get pods -o wide
```

**Possible Causes:**

* ImagePullPolicy misconfigured
* Image tag didn’t change
* Pod anti-affinity or node constraints preventing new pods

**Fixes:**

```bash
kubectl set image deployment/webapp webapp=nginx:1.24 --record
kubectl rollout restart deployment webapp
```

---

## **2️⃣ Networking & Services**

### **Scenario 4: Pod cannot reach another pod**

**Symptoms:**

```bash
kubectl exec -it webapp-1 -- ping backend
```

Fails with `unknown host` or timeout.

**Troubleshooting Steps:**

1. Check DNS:

```bash
kubectl exec -it webapp-1 -- nslookup backend
kubectl get svc
```

2. Check NetworkPolicy (if applied)

```bash
kubectl get networkpolicy
```

3. Check CNI plugin logs (calico/weave/flannel):

```bash
kubectl logs -n kube-system <cni-pod>
```

**Fixes:**

* Correct service name / namespace
* Update NetworkPolicy rules
* Ensure CNI plugin pods are running

---

### **Scenario 5: Service not exposing pods**

**Symptoms:**

* Service `ClusterIP`/`LoadBalancer` not routing requests to pods.

**Troubleshooting:**

```bash
kubectl get endpoints <service-name>
kubectl describe svc <service-name>
```

**Possible Causes:**

* Label mismatch between service selector and pod labels
* Pods not ready (`readinessProbe` failing)

**Fixes:**

* Correct labels in deployment or service
* Check readiness probe configuration

---

### **Scenario 6: Ingress not working**

**Symptoms:**

* HTTP 404 or cannot reach the host

**Troubleshooting Steps:**

```bash
kubectl get ingress
kubectl describe ingress <ingress-name>
kubectl logs -n kube-system -l app.kubernetes.io/name=ingress-nginx
```

**Common Causes:**

* Hostnames mismatch in `/etc/hosts`
* Service not exposed correctly
* Ingress controller not running

**Fixes:**

* Correct ingress rules
* Ensure ingress controller pod is running
* Update host mappings for local testing

---

## **3️⃣ Storage & PVC Issues**

### **Scenario 7: PVC stuck in `Pending`**

```bash
kubectl get pvc
NAME         STATUS    VOLUME
webapp-pvc   Pending
```

**Troubleshooting:**

```bash
kubectl describe pvc webapp-pvc
kubectl get sc
kubectl describe sc <storageclass-name>
```

**Causes:**

* No StorageClass or PV available
* PV doesn’t match requested size or accessMode

**Fixes:**

* Create a matching PV or adjust PVC
* Ensure dynamic provisioning is enabled

---

### **Scenario 8: Pod cannot mount PVC**

**Symptoms:**

```bash
MountVolume.SetUp failed for volume
```

**Fixes:**

* Check PV is available
* Check access modes
* Check node has permission/mount options

---

## **4️⃣ Performance & Resource Issues**

### **Scenario 9: Pod using too much CPU/Memory**

**Symptoms:**

* Pod evicted or throttled

**Troubleshooting:**

```bash
kubectl top pods
kubectl top node
kubectl describe pod <pod>
```

**Fixes:**

* Update `resources.requests` and `limits` in deployment
* Scale deployment manually or with HPA
* Investigate application performance issues

---

### **Scenario 10: Node Not Ready**

**Symptoms:**

```bash
kubectl get nodes
node1   NotReady
```

**Troubleshooting:**

```bash
kubectl describe node node1
journalctl -u kubelet
```

**Possible Causes:**

* Network issue
* Kubelet not running
* Disk pressure

**Fixes:**

* Restart kubelet

```bash
systemctl restart kubelet
```

* Free disk or memory
* Check CNI plugin

---

## **5️⃣ Cluster & Control Plane Issues**

### **Scenario 11: API Server Not Reachable**

**Symptoms:**

* `kubectl get pods` fails with `Unable to connect to the server`

**Troubleshooting:**

* Check control plane components

```bash
kubectl get pods -n kube-system
kubectl get componentstatus
```

* Check API server logs:

```bash
journalctl -u kube-apiserver
```

* Network/firewall issues

---

### **Scenario 12: Unable to pull image**

**Symptoms:**

```bash
ImagePullBackOff
```

**Troubleshooting:**

```bash
kubectl describe pod <pod>
```

**Causes:**

* Wrong image name or tag
* Private registry credentials missing

**Fixes:**

* Correct image name/tag
* Create Secret for registry:

```bash
kubectl create secret docker-registry regcred --docker-server=<registry> --docker-username=<user> --docker-password=<pass> --docker-email=<email>
kubectl patch serviceaccount default -p '{"imagePullSecrets": [{"name": "regcred"}]}'
```

---

## **6️⃣ Best Practices for Troubleshooting**

1. Always start with `kubectl describe pod` → check events
2. Check logs with `kubectl logs` (for multi-container: specify `-c container`)
3. Check metrics: `kubectl top pods` / `kubectl top nodes`
4. Check resources & constraints in deployments
5. Check networking: services, endpoints, DNS, NetworkPolicies
6. Check storage: PVC, PV, access modes, mounts
7. Keep namespaces in mind — resources may exist in different namespaces

---

# **🔹 Kubernetes Troubleshooting Lab – Real Life Scenarios**

We’ll cover **12+ scenarios**:

1. Pod Pending
2. CrashLoopBackOff
3. Deployment not updating
4. Service not routing traffic
5. Ingress misconfigured
6. PVC stuck / volume mount error
7. Node NotReady
8. High CPU/Memory usage
9. HPA not scaling
10. ImagePullBackOff / private registry issue
11. DNS resolution issue inside cluster
12. NetworkPolicy blocking traffic
13. Control Plane API issues
14. Cluster resource limits & quota issues

---

## **1️⃣ Pod Pending**

**Issue:** Pod stuck in `Pending`.

**Broken deployment YAML:** `pending-pod.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pending-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: pending-app
  template:
    metadata:
      labels:
        app: pending-app
    spec:
      containers:
      - name: nginx
        image: nginx:stable
        resources:
          requests:
            cpu: 5000m
            memory: 5Gi
```

**Practice:**

```bash
kubectl apply -f pending-pod.yaml
kubectl describe pod -l app=pending-app
kubectl get events
```

**Fix:** Lower resource requests or scale cluster.

---

## **2️⃣ CrashLoopBackOff**

**Issue:** Pod keeps crashing due to wrong command.

**Broken YAML:** `crashloop-pod.yaml`

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: crash-pod
spec:
  containers:
  - name: crash-container
    image: busybox
    command: ["sleep", "wrong-arg"]
```

**Practice:**

```bash
kubectl apply -f crashloop-pod.yaml
kubectl logs crash-pod
kubectl describe pod crash-pod
```

**Fix:** Correct the command.

---

## **3️⃣ Deployment Not Updating**

**Issue:** New image not deployed.

**Broken deployment:** `stale-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: stale-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: stale-app
  template:
    metadata:
      labels:
        app: stale-app
    spec:
      containers:
      - name: nginx
        image: nginx:1.21   # old image
```

**Practice:**

```bash
kubectl apply -f stale-deployment.yaml
kubectl get pods -o wide
kubectl set image deployment/stale-app nginx=nginx:1.24
```

---

## **4️⃣ Service Not Routing Traffic**

**Issue:** Service endpoints empty.

**Broken YAML:** `service-label-mismatch.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: broken-service
spec:
  selector:
    app: wrong-label
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
```

**Practice:**

```bash
kubectl apply -f service-label-mismatch.yaml
kubectl get endpoints broken-service
```

**Fix:** Correct service selector to match pod labels.

---

## **5️⃣ Ingress Misconfigured**

**Issue:** 404 or unreachable host.

**Broken YAML:** `ingress-broken.yaml`

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: broken-ingress
spec:
  rules:
  - host: wrong.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: webapp-service
            port:
              number: 80
```

**Practice:**

* `kubectl get ingress` → check ADDRESS
* `curl http://localhost:8080` → 404

**Fix:** Correct host or use path-based routing for localhost testing.

---

## **6️⃣ PVC / Volume Mount Errors**

**Broken PVC:** `pvc-pending.yaml`

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-broken
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
```

**Practice:**

```bash
kubectl apply -f pvc-pending.yaml
kubectl get pvc
kubectl describe pvc pvc-broken
```

**Fix:** Create a matching PV or adjust storage requests.

---

## **7️⃣ Node NotReady**

**Simulation:** Stop kubelet on node (if possible) or taint node:

```bash
kubectl taint nodes <node-name> key=value:NoSchedule
kubectl get nodes
```

**Practice:**

* Check events and node description
* Check kubelet logs:

```bash
journalctl -u kubelet
```

**Fix:** Remove taint or restart kubelet.

---

## **8️⃣ High CPU/Memory Usage**

* Deploy a stress pod:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: cpu-stress
spec:
  containers:
  - name: stress
    image: polinux/stress
    args: ["--cpu", "2", "--timeout", "600s"]
```

**Practice:**

```bash
kubectl apply -f cpu-stress.yaml
kubectl top pods
kubectl top nodes
```

**Fix:** HPA or adjust resources.

---

## **9️⃣ HPA Not Scaling**

**Issue:** Metrics not available or HPA not triggering.

**Check:**

```bash
kubectl get hpa
kubectl describe hpa
kubectl top pods
```

**Fix:** Ensure metrics-server is installed and running, and CPU metrics are present.

---

## **🔹 Additional Scenarios**

10. **ImagePullBackOff / private registry:** Wrong image/tag or missing secret.
11. **DNS resolution issue:** Pod cannot resolve service names.
12. **NetworkPolicy blocking traffic:** Pod can’t reach another pod.
13. **Control Plane API unavailable:** kubectl commands fail.
14. **Resource quota exceeded:** Pod creation fails due to limits.

---

## **💡 Lab Setup Advice**

1. Create a namespace `kubectl create ns k8s-lab`
2. Apply all broken YAMLs in this namespace
3. Practice each scenario by running `kubectl describe`, `kubectl logs`, `kubectl get events`, `kubectl top`
4. Fix the issue one by one and note how each tool helps troubleshoot

---


