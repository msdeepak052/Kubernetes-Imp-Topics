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


If you want, I can also **draw a simple diagram showing the Pod deletion lifecycle**, which makes it very easy to visualize. Do you want me to do that?
