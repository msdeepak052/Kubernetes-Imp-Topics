# 🔹 **What are Taints and Tolerations?**

* **Taints** are applied to **Nodes**. They **repel** pods unless those pods explicitly say they can tolerate them.
* **Tolerations** are applied to **Pods**. They let the pod be scheduled on nodes with matching taints.

👉 Think of it as:

* **Node says:** "I don’t allow pods unless they can tolerate my taint."
* **Pod says:** "I tolerate this taint, so I can run here."

This mechanism is the **opposite of `nodeSelector`/`affinity`** (which is “attraction”).

---

# 🔹 **Taint Syntax**

```bash
kubectl taint nodes <node-name> key=value:effect
```

* **key=value** → label-style identifier.
* **effect** → defines what happens if pod doesn’t tolerate.

  * `NoSchedule` → Pod will not be scheduled on this node.
  * `PreferNoSchedule` → Soft rule (try to avoid, but not guaranteed).
  * `NoExecute` → New pods won’t be scheduled, and existing pods will be **evicted** if they don’t tolerate.

---

# 🔹 **Toleration Syntax in Pod**

```yaml
tolerations:
- key: "key"
  operator: "Equal"
  value: "value"
  effect: "NoSchedule"
```

* **operator**:

  * `Equal` → key/value must match.
  * `Exists` → only key matters (value ignored).

---

# 🔹 **Examples**

## ✅ Example 1: Hard restriction (`NoSchedule`)

Taint a node:

```bash
kubectl taint nodes worker-1 dedicated=web:NoSchedule
```

Pod tolerating the taint:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-pod
spec:
  containers:
  - name: nginx
    image: nginx
  tolerations:
  - key: "dedicated"
    operator: "Equal"
    value: "web"
    effect: "NoSchedule"
```

👉 Only pods with this toleration can be scheduled on `worker-1`.

---

## ✅ Example 2: Soft restriction (`PreferNoSchedule`)

Taint a node:

```bash
kubectl taint nodes worker-2 backup=true:PreferNoSchedule
```

Pod toleration:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: soft-pod
spec:
  containers:
  - name: busybox
    image: busybox
    command: ["sleep", "3600"]
  tolerations:
  - key: "backup"
    operator: "Equal"
    value: "true"
    effect: "PreferNoSchedule"
```

👉 Scheduler will **try to avoid** putting this pod on `worker-2`, but may still schedule it if needed.

---

## ✅ Example 3: Eviction (`NoExecute`)

Taint a node:

```bash
kubectl taint nodes worker-3 critical=true:NoExecute
```

Pod toleration:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: critical-pod
spec:
  containers:
  - name: nginx
    image: nginx
  tolerations:
  - key: "critical"
    operator: "Equal"
    value: "true"
    effect: "NoExecute"
    tolerationSeconds: 60
```

👉 Behavior:

* Pods without toleration are evicted immediately.
* This pod can stay for **60s** before eviction.

---

## ✅ Example 4: Operator `Exists`

Sometimes we don’t care about value, only key.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: exists-pod
spec:
  containers:
  - name: busybox
    image: busybox
    command: ["sleep", "3600"]
  tolerations:
  - key: "dedicated"
    operator: "Exists"   # only checks key
    effect: "NoSchedule"
```

👉 Pod can tolerate **any taint with key `dedicated`**, regardless of value.

---

# 🔹 **Why use Taints & Tolerations?**

* Reserve nodes for special workloads (e.g., GPU nodes, logging, monitoring).
* Evict pods if nodes become unsuitable (maintenance, dedicated hardware).
* Ensure production workloads don’t mix with dev/test workloads.
* Enforce cluster policies (e.g., only certain apps on certain nodes).

---

# 🔹 Key Commands

```bash
# Add a taint
kubectl taint nodes worker-1 dedicated=web:NoSchedule

# Remove a taint
kubectl taint nodes worker-1 dedicated=web:NoSchedule-

# View taints on nodes
kubectl describe node worker-1 | grep Taints
```

---

✅ **Summary**

* **Taints** = repel pods from nodes.
* **Tolerations** = let pods accept those taints.
* **Effects**: `NoSchedule`, `PreferNoSchedule`, `NoExecute`.
* Great for **node isolation, workload separation, and special hardware allocation**.

---

👍 Let’s build a **real-world scenario** where we **taint GPU nodes** so only GPU workloads can run there, while normal workloads stay on regular nodes.

---

# 🔹 **Step 1: Taint the GPU Node**

Suppose your GPU node is named `gpu-node-1`.
We taint it so **only GPU workloads** can run there:

```bash
kubectl taint nodes gpu-node-1 gpu=true:NoSchedule
```

👉 This means:

* No pod can run on `gpu-node-1` **unless it tolerates the taint**.

---

# 🔹 **Step 2: Normal Pod (without toleration)**

This pod **cannot run** on `gpu-node-1`, because it doesn’t tolerate the taint:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: normal-pod
spec:
  containers:
  - name: busybox
    image: busybox
    command: ["sleep", "3600"]
```

👉 Scheduler will place it on another worker node, not `gpu-node-1`.

---

# 🔹 **Step 3: GPU Pod (with toleration)**

This pod **can run** on `gpu-node-1` because it tolerates the taint:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: gpu-pod
spec:
  containers:
  - name: gpu-container
    image: nvidia/cuda:11.0-base   # Example CUDA image
    command: ["nvidia-smi"]
  tolerations:
  - key: "gpu"
    operator: "Equal"
    value: "true"
    effect: "NoSchedule"
```

---

# 🔹 **Step 4 (Optional): Combine with `nodeSelector`**

To make sure GPU workloads **only run on GPU nodes** (not just tolerate them), we label the node and then add `nodeSelector`.

👉 Label the GPU node:

```bash
kubectl label node gpu-node-1 hardware=gpu
```

👉 Update Pod spec:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: gpu-pod-strict
spec:
  containers:
  - name: gpu-container
    image: nvidia/cuda:11.0-base
    command: ["nvidia-smi"]
  tolerations:
  - key: "gpu"
    operator: "Equal"
    value: "true"
    effect: "NoSchedule"
  nodeSelector:
    hardware: gpu
```

✅ This ensures:

* Pod runs **only on nodes labeled `hardware=gpu`**.
* Pod tolerates the taint on those nodes.

---

# 🔹 **Real-World Use Cases**

* **GPU Nodes** → ML/AI workloads only.
* **Logging Nodes** → Only logging/monitoring pods (e.g., Fluentd, Prometheus agents).
* **Critical workloads** → Run on reserved nodes with `NoExecute` taints (evict non-critical pods).
* **Maintenance mode** → Taint a node to **drain workloads gradually**.

---

# 🔹 **Key Verification Commands**

```bash
# See node taints
kubectl describe node gpu-node-1 | grep Taints

# Check where a pod is scheduled
kubectl get pod gpu-pod -o wide

# Remove taint if needed
kubectl taint nodes gpu-node-1 gpu=true:NoSchedule-
```

---

✅ **Summary**:
By combining **Taints + Tolerations + NodeSelector**, you get **strict control**:

* **Taints** = prevent unwanted pods.
* **Tolerations** = allow specific pods.
* **NodeSelector** = ensure pods run only on GPU hardware.

---

