# Pod lifecycle phases

## 🧠 What Is the Pod Lifecycle?

Every **Pod** in Kubernetes goes through a **series of well-defined phases** — from creation to deletion.

Kubernetes tracks these phases in the Pod’s **status** field (visible via `kubectl get pods` or `kubectl describe pod`).

---

## 🚀 The 6 Main Pod Phases

| Phase                                                              | Description                                                                                                                                                   |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1. Pending**                                                     | The Pod has been accepted by the API server, but **not all containers are created yet**. (Images may still be pulling or the Pod is waiting to be scheduled.) |
| **2. Running**                                                     | The Pod has been scheduled to a node, and **all containers are created and at least one is running**.                                                         |
| **3. Succeeded**                                                   | All containers in the Pod have **terminated successfully (exit code 0)** and won’t restart.                                                                   |
| **4. Failed**                                                      | All containers have **terminated**, and at least one container **failed (non-zero exit code)** and will not restart.                                          |
| **5. Unknown**                                                     | The **state of the Pod cannot be determined**, often due to communication errors between the API server and node.                                             |
| **6. Terminating** *(not an official phase but a transient state)* | The Pod is being deleted — it’s cleaning up and shutting down gracefully.                                                                                     |

---

## 🔄 1. **Pending Phase**

**What happens:**

* Pod is created and validated by the API Server.
* Scheduler tries to assign it to a suitable Node.
* Pod waits for image pulling and volume mounting.

**Example reason:**

```bash
kubectl describe pod nginx-pod
```

```
Status: Pending
Reason: ImagePullBackOff
```

**Common causes:**

* No available nodes
* Image still downloading
* Missing imagePullSecret for private registries

---

## 🟢 2. **Running Phase**

**What happens:**

* The Pod is bound to a Node.
* All init containers have completed.
* Main containers are started and at least one is running.

**Example:**

```bash
Status: Running
Containers:
  nginx:
    State: Running
    Started: 10s ago
```

**Typical for:** web servers, databases, long-running workloads.

---

## ✅ 3. **Succeeded Phase**

**What happens:**

* All containers terminated successfully (exit code `0`).
* Kubernetes won’t restart the Pod (unless managed by a Job).

**Example:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: batch-job
spec:
  restartPolicy: Never
  containers:
    - name: job
      image: busybox
      command: ["sh", "-c", "echo Done"]
```

Output:

```bash
kubectl get pod batch-job
# STATUS = Succeeded
```

---

## ❌ 4. **Failed Phase**

**What happens:**

* All containers have terminated.
* At least one container **failed** (non-zero exit code).

**Example:**

```yaml
command: ["sh", "-c", "exit 1"]
```

```bash
kubectl get pod fail-job
# STATUS = Failed
```

**Describe output:**

```
State: Terminated
Reason: Error
Exit Code: 1
```

---

## ⚠️ 5. **Unknown Phase**

**What happens:**

* The kubelet on the node **can’t be reached**.
* The API server can’t determine the Pod’s actual state.

**Example causes:**

* Network issues between control plane and node
* Node is down or unresponsive

---

## 🧹 6. **Terminating (Transitional)**

**What happens:**

* Appears when you run:

  ```bash
  kubectl delete pod <pod-name>
  ```
* Kubernetes sends a **SIGTERM** to containers.
* Pod stays in `Terminating` until:

  * Containers exit, or
  * `terminationGracePeriodSeconds` expires (then SIGKILL is sent)

**Example:**

```bash
kubectl get pods
# nginx-pod   1/1   Terminating
```

---

## 🔁 Summary Flow Diagram

```
PENDING ──> RUNNING ──> SUCCEEDED
     │           │
     │           └──> FAILED
     │
     └──> UNKNOWN (if node unreachable)
```

During deletion:

```
RUNNING ──> TERMINATING ──> (Deleted)
```

---

## 🧩 Real Example

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-lifecycle-demo
spec:
  containers:
    - name: demo
      image: busybox
      command: ["sh", "-c", "echo Hello && sleep 10 && echo Done"]
      imagePullPolicy: IfNotPresent
```

### When you run:

```bash
kubectl apply -f pod-lifecycle-demo.yaml
```

You’ll see:

| Time                          | Status                             |
| ----------------------------- | ---------------------------------- |
| Immediately after creation    | `Pending` (waiting for scheduling) |
| After scheduling              | `Running`                          |
| After 10 seconds (sleep ends) | `Succeeded`                        |
| After deletion command        | `Terminating` → removed            |

---

## 🏁 Key Takeaways

| Phase       | Description                                 | Common in             |
| ----------- | ------------------------------------------- | --------------------- |
| Pending     | Pod waiting to be scheduled or image pulled | Startup issues        |
| Running     | Containers active                           | Normal workloads      |
| Succeeded   | All containers finished                     | Jobs                  |
| Failed      | Containers exited abnormally                | Failed jobs/scripts   |
| Unknown     | Node communication issue                    | Node/network failures |
| Terminating | Pod shutting down                           | Graceful deletions    |

---
