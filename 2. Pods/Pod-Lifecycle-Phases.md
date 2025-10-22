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

## 🧠 What Is Pod Status?

When you run:

```bash
kubectl get pods
```

You see output like:

```
NAME             READY   STATUS      RESTARTS   AGE
nginx-pod        1/1     Running     0          5m
```

👉 The **`STATUS`** column is what we call the **Pod Status** — it shows the **high-level state** of the Pod (and its containers).

---

## 🧩 Pod Status Comes From:

Kubernetes determines the Pod’s status from:

* **Pod phase** (Pending, Running, Succeeded, etc.)
* **Container states** (Waiting, Running, Terminated)
* **Conditions** (like Initialized, Ready, etc.)

All of this is stored in the Pod’s **status section**:

```bash
kubectl get pod nginx-pod -o yaml
```

You’ll see:

```yaml
status:
  phase: Running
  conditions:
  - type: Initialized
    status: "True"
  - type: Ready
    status: "True"
  - type: ContainersReady
    status: "True"
  - type: PodScheduled
    status: "True"
  containerStatuses:
  - name: nginx
    state:
      running:
        startedAt: "2025-10-22T13:40:05Z"
    ready: true
    restartCount: 0
```

---

## 🚀 Main Pod Status Values

| **Status**                | **Meaning**                                                      | **What’s Happening Internally**                               |
| ------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------- |
| **Pending**               | Pod accepted by API server but not yet running                   | Scheduler may still be deciding node, or image is downloading |
| **Running**               | Pod bound to a node, containers created and at least one running | Normal operation                                              |
| **Succeeded**             | All containers exited successfully (exit code 0)                 | Typically in Jobs                                             |
| **Failed**                | All containers exited, at least one with non-zero exit code      | Script failure, crash, etc.                                   |
| **Unknown**               | API server can’t contact kubelet                                 | Node/network issue                                            |
| **CrashLoopBackOff**      | Container repeatedly crashes                                     | Application crash or config issue                             |
| **ImagePullBackOff**      | Failed to pull image                                             | Image not found / invalid credentials                         |
| **ErrImagePull**          | Image pull failed                                                | Registry or tag issue                                         |
| **ContainerCreating**     | Container image is being pulled / container being set up         | Initialization step                                           |
| **Init:CrashLoopBackOff** | Init container keeps failing                                     | Problem in init container setup                               |

---

## 🧩 Example 1 — Running Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
spec:
  containers:
    - name: nginx
      image: nginx
```

```bash
kubectl get pods
```

```
NAME         READY   STATUS    RESTARTS   AGE
nginx-pod    1/1     Running   0          2m
```

✔ Means:

* Pod phase = **Running**
* Container state = **Running**
* Conditions (Ready, Initialized) = **True**

---

## 🧩 Example 2 — Pending (image being pulled)

```yaml
image: nginx:doesnotexist
```

```bash
kubectl get pods
```

```
NAME         READY   STATUS              RESTARTS   AGE
nginx-pod    0/1     ImagePullBackOff    0          1m
```

✔ Means:

* Kubernetes tried to pull image but failed.
* Pod phase still **Pending**, container state **Waiting** with reason `ImagePullBackOff`.

---

## 🧩 Example 3 — CrashLoopBackOff

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: crash-pod
spec:
  containers:
    - name: crash
      image: busybox
      command: ["sh", "-c", "exit 1"]
```

```bash
kubectl get pods
```

```
NAME         READY   STATUS             RESTARTS   AGE
crash-pod    0/1     CrashLoopBackOff   3          2m
```

✔ Means:

* Container keeps crashing and restarting.
* kubelet uses **backoff strategy** (waits 10s, 20s, 40s...) before restarting again.

---

## 🧩 Example 4 — Succeeded

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hello-pod
spec:
  restartPolicy: Never
  containers:
    - name: hello
      image: busybox
      command: ["sh", "-c", "echo Hello Kubernetes!"]
```

```bash
kubectl get pods
```

```
NAME         READY   STATUS      RESTARTS   AGE
hello-pod    0/1     Succeeded  0          8s
```

✔ Means:

* Command executed successfully and container exited (code 0).
* Pod phase = **Succeeded**.

---

## 🧰 How To Troubleshoot Pod Status

### 🔎 1. Describe the Pod

```bash
kubectl describe pod <pod-name>
```

* Shows detailed events and container states.

### 🔎 2. Check logs

```bash
kubectl logs <pod-name>
```

* See application-level errors or crash reasons.

### 🔎 3. Check Node Events

```bash
kubectl get events --sort-by=.metadata.creationTimestamp
```

* Detect scheduling or volume mount issues.

---

## 📊 Summary Table

| STATUS           | Meaning                            | Common Cause            | Command to Debug       |
| ---------------- | ---------------------------------- | ----------------------- | ---------------------- |
| Pending          | Not yet scheduled or pulling image | No node / Image pulling | `kubectl describe pod` |
| Running          | Containers up and running          | Healthy workload        | `kubectl logs`         |
| Succeeded        | Containers exited normally         | Completed job/script    | `kubectl logs`         |
| Failed           | Containers exited with errors      | Script crash            | `kubectl logs`         |
| Unknown          | Node unreachable                   | Node down               | `kubectl get nodes`    |
| CrashLoopBackOff | Container repeatedly failing       | Misconfiguration        | `kubectl describe pod` |
| ImagePullBackOff | Image pull error                   | Wrong tag / credentials | `kubectl describe pod` |

---

## 🏁 Key Takeaway

> **Pod phase** = High-level lifecycle
> **Pod status** = Real-time operational state (includes container status + reasons + conditions)

They work **together** to tell you exactly what’s happening with your Pod.

---


