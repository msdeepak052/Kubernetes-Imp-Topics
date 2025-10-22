# Pod Termination

When you run:

```bash
kubectl delete pod <pod-name>
```

here’s exactly what happens, step by step:

---

### 1. **API Request to Kubernetes**

* `kubectl` sends a **DELETE request** to the Kubernetes **API server** for the specified Pod.
* The request looks like:

  ```
  DELETE /api/v1/namespaces/<namespace>/pods/<pod-name>
  ```

---

### 2. **Pod Deletion Process Begins**

* Kubernetes **marks the Pod for deletion**. It sets the Pod’s `deletionTimestamp`.
* The Pod **enters `Terminating` state**.
* The Pod is **not immediately removed**; first, the system tries to gracefully shut down its containers.

---

### 3. **Graceful Termination**

* Kubernetes sends a **SIGTERM signal** to each container inside the Pod.
* Containers are given a **grace period** (default 30 seconds, configurable via `--grace-period` or Pod spec `terminationGracePeriodSeconds`) to clean up resources and exit gracefully.
* During this period, Kubernetes keeps the Pod visible in `kubectl get pods` with the status `Terminating`.

---

### 4. **Forceful Termination (if needed)**

* If containers **don’t exit within the grace period**, Kubernetes sends a **SIGKILL signal**, forcibly killing the containers.

---

### 5. **Cleanup**

* Once containers stop:

  * Kubernetes **removes the Pod from etcd** (the cluster state storage).
  * Any associated resources like **volumes** are unmounted/deallocated.
  * The Pod is **deleted from the cluster**, and `kubectl get pods` no longer lists it.

---

### 6. **Impact on ReplicaSets/Deployments**

* If the Pod is **managed by a Deployment, ReplicaSet, or StatefulSet**, Kubernetes sees that the **desired number of replicas is not met**.
* It **automatically creates a new Pod** to maintain the desired state.

---

### 🔹 Optional Flags

* `--grace-period=0 --force`: Deletes the Pod **immediately**, skipping graceful shutdown.
* `--wait=false`: Don’t wait for deletion to complete; `kubectl` returns immediately.

---

**In short:**
`kubectl delete pod` initiates a controlled shutdown and removal of the Pod. For managed Pods, it triggers a replacement to maintain the declared state.

---

<img width="1884" height="476" alt="image" src="https://github.com/user-attachments/assets/95e26c3b-73fa-48f6-bf77-b70f7fefd592" />

---

# Restart Policy

In Kubernetes, the **Restart Policy** defines **how containers in a Pod should be restarted** when they exit. This is a **Pod-level setting**, not per container. Let’s break it down clearly:

---

## 1. **Where It’s Defined**

The restart policy is specified in the Pod spec:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: example-pod
spec:
  restartPolicy: <Policy>
  containers:
    - name: nginx
      image: nginx
```

---

## 2. **Possible Values**

### a) **Always** (Default for Deployments)

* **Behavior:** The container is restarted **every time it exits**, regardless of exit status.
* **Use case:** Long-running services (e.g., web servers, databases).
* **Example:**
  If Nginx crashes, Kubernetes will immediately restart it.

---

### b) **OnFailure**

* **Behavior:** The container is restarted **only if it exits with a non-zero status** (failure).
* **Use case:** Batch jobs or tasks that might fail and need retrying.
* **Example:**
  A script that processes files; if it fails, Kubernetes restarts it.

---

### c) **Never**

* **Behavior:** The container is **never restarted**, regardless of exit status.
* **Use case:** Run-once jobs where failure should not trigger retries.
* **Example:**
  A Pod that runs a database migration script once and then exits.

---

## 3. **Important Notes**

* **Deployments / ReplicaSets** always effectively have `restartPolicy: Always`, because they manage Pods and try to keep them running.
* **Jobs / CronJobs** usually use `restartPolicy: OnFailure` or `Never`.
* **RestartPolicy only applies to containers inside a Pod**, not Pods themselves.
* Changing a Pod’s restart policy **after creation is not allowed**. You must create a new Pod spec.

---

### 4. **Visual Summary**

| Restart Policy | Container Exit | Restarted? | Typical Use Case            |
| -------------- | -------------- | ---------- | --------------------------- |
| Always         | 0 or >0        | Yes        | Long-running services       |
| OnFailure      | 0              | No         | Batch jobs (success → stop) |
| OnFailure      | >0             | Yes        | Retry on failure            |
| Never          | 0 or >0        | No         | Run-once jobs or scripts    |


<img width="1371" height="702" alt="image" src="https://github.com/user-attachments/assets/678efc67-d421-495b-80a0-78660bdc179b" />

---

