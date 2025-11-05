# 🔹 **1. What are Health Probes in Kubernetes?**

Health probes are used by Kubernetes to **check the health of containers** and take actions automatically:

| Probe Type          | Purpose                                                                                                                                |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **Liveness Probe**  | Checks if a container is **alive**. If it fails, Kubernetes **kills and restarts** the container.                                      |
| **Readiness Probe** | Checks if a container is **ready to serve traffic**. If it fails, the Pod is **removed from Service endpoints** but **not restarted**. |

---

# 🔹 **2. Why Liveness and Readiness are Needed**

* **Liveness** → Detects **deadlocks or crashed containers**. Prevents Pod from being stuck in a bad state.
* **Readiness** → Ensures that **only ready Pods receive traffic**. Avoids sending requests to Pods still starting up.

---

# 🔹 **3. Probe Types**

1. **HTTP Probe**

   * Sends HTTP GET request to container.
   * Example: `/healthz` endpoint.
2. **TCP Probe**

   * Checks if TCP port is open.
3. **Exec Probe**

   * Executes a command inside the container. Success = healthy, failure = unhealthy.

---

# 🔹 **4. Key Terms in Probes**

| Term                    | Meaning                                                              |
| ----------------------- | -------------------------------------------------------------------- |
| **initialDelaySeconds** | Time to wait before starting probe after container starts.           |
| **periodSeconds**       | How often probe runs (frequency).                                    |
| **timeoutSeconds**      | Time to wait for probe response before considering it failed.        |
| **successThreshold**    | Number of consecutive successes to consider Pod healthy (default 1). |
| **failureThreshold**    | Number of consecutive failures to consider Pod unhealthy.            |

---

# 🔹 **5. Example Deployment with Liveness and Readiness Probes**

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
        ports:
        - containerPort: 80
        livenessProbe:
          httpGet:
            path: /healthz
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 2
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 1
          successThreshold: 1
```

```yaml

apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx          # Matches the Deployment Pods
  ports:
    - protocol: TCP
      port: 80          # Service port
      targetPort: 80    # Pod container port
  type: ClusterIP       # Internal only (default)

```

---

# 🔹 **6. Interpretation of Example**

### **Liveness Probe**

* Checks `http://<pod-ip>:80/healthz`
* Wait **10 seconds** before first check
* Checks **every 5 seconds**
* Timeout = 2 seconds
* **3 consecutive failures** → Pod is restarted

### **Readiness Probe**

* Checks `http://<pod-ip>:80/ready`
* Wait **5 seconds** before first check
* Checks **every 5 seconds**
* Timeout = 1 second
* **1 consecutive success** → Pod is marked ready

---

# 🔹 **7. Notes / Best Practices**

1. **Separate liveness and readiness endpoints** — often `/healthz` for liveness, `/ready` for readiness.
2. **Set initialDelaySeconds** to give your app time to start.
3. **Use readiness probe for slow-starting services** so they are not added to load balancer prematurely.
4. **Use exec probe** for non-HTTP apps:

```yaml
livenessProbe:
  exec:
    command:
    - cat
    - /tmp/healthy
  initialDelaySeconds: 5
  periodSeconds: 5
```

---

# 🔹 **8. Quick Summary**

| Probe     | Action on Failure             | Typical Use                          |
| --------- | ----------------------------- | ------------------------------------ |
| Liveness  | Restart container             | Detect deadlocks, crashes            |
| Readiness | Remove from service endpoints | Ensure only ready Pods serve traffic |

---


