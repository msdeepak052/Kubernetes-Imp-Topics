# 🔹 **What is NodeSelector?**

* A **simple scheduling constraint** for Pods.
* It makes sure a Pod is scheduled **only on nodes that have specific labels**.
* Works like:

  * **Node** → must have label(s).
  * **Pod** → requests those label(s) in `nodeSelector`.
* It’s the **simplest form of node affinity** (no advanced logic).

---

# 🔹 **How it Works**

1. Label the node:

   ```bash
   kubectl label node worker-node-1 disktype=ssd
   ```
2. Pod uses `nodeSelector`:

   ```yaml
   spec:
     nodeSelector:
       disktype: ssd
   ```

👉 Pod runs **only on nodes with `disktype=ssd`**.

---

# 🔹 **YAML Examples**

## ✅ Example 1: Basic `nodeSelector`

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-ssd
spec:
  containers:
  - name: nginx
    image: nginx
  nodeSelector:
    disktype: ssd
```

👉 Pod will only run on nodes labeled `disktype=ssd`.

---

## ✅ Example 2: Deployment with NodeSelector

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: nginx
        image: nginx
      nodeSelector:
        region: us-east
```

👉 All Pods in this Deployment will be scheduled on nodes with label `region=us-east`.

---

## ✅ Example 3: Multiple Node Labels

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: multi-label-pod
spec:
  containers:
  - name: busybox
    image: busybox
    command: ["sleep", "3600"]
  nodeSelector:
    disktype: ssd
    region: ap-south-1
```

👉 Node must have **both labels** (`disktype=ssd` AND `region=ap-south-1`).

---

## ✅ Example 4: NodeSelector + Tolerations

(Sometimes you combine both to strictly control scheduling.)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: gpu-pod
spec:
  containers:
  - name: cuda
    image: nvidia/cuda:11.0-base
    command: ["nvidia-smi"]
  nodeSelector:
    hardware: gpu
  tolerations:
  - key: "gpu"
    operator: "Equal"
    value: "true"
    effect: "NoSchedule"
```

👉 Pod can **only run on GPU nodes** that:

* Have label `hardware=gpu`.
* Are tainted with `gpu=true:NoSchedule` (but tolerated).

---

# 🔹 **Limitations of NodeSelector**

* Only supports **exact matches** (`key=value`).
* No advanced rules like ranges, OR conditions, etc.
* For complex scheduling → use **Node Affinity**.

---

# 🔹 **When to Use NodeSelector**

* Simple use cases like:

  * Run pods on SSD-backed nodes.
  * Run workloads in specific regions/zones.
  * Ensure app pods only run on GPU nodes.
  * Separate dev vs. prod workloads.

---

# 🔹 Key Commands

```bash
# Label a node
kubectl label node worker-node-1 disktype=ssd

# View node labels
kubectl get nodes --show-labels

# Remove a label
kubectl label node worker-node-1 disktype-
```

---

✅ **Summary**

* `nodeSelector` = simplest way to **pin Pods to Nodes** with labels.
* Good for **basic constraints** (one or multiple labels).
* For advanced logic (e.g., OR, NOT, ranges) → use **Node Affinity**.

---

👍 — Let’s go step by step. Node Affinity and Pod Affinity are **advanced scheduling rules** in Kubernetes, more flexible than `nodeSelector`.

---

# 🔹 **1. Node Affinity**

* **Definition**: A set of rules that constrain which **nodes a Pod can be scheduled on** based on node labels.
* **More advanced than NodeSelector**:

  * Can use **soft vs hard rules** (preferred vs required).
  * Supports **operators** (`In`, `NotIn`, `Exists`, `Gt`, `Lt`).

---

## ✅ Node Affinity Types

1. **requiredDuringSchedulingIgnoredDuringExecution** (hard requirement)

   * Pod **must** be scheduled on nodes matching the rule.
2. **preferredDuringSchedulingIgnoredDuringExecution** (soft preference)

   * Scheduler **tries** to place Pod on matching nodes, but it’s not mandatory.

---

## 🔹 Node Affinity YAML Examples

### Example 1: Hard Node Affinity

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hard-affinity-pod
spec:
  containers:
  - name: nginx
    image: nginx
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: disktype
            operator: In
            values:
            - ssd
```

✅ Pod **must** run on a node with label `disktype=ssd`.

---

### Example 2: Soft Node Affinity

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: soft-affinity-pod
spec:
  containers:
  - name: nginx
    image: nginx
  affinity:
    nodeAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 1
        preference:
          matchExpressions:
          - key: region
            operator: In
            values:
            - us-east
```

✅ Scheduler **prefers nodes** with `region=us-east` but can schedule elsewhere if needed.

---

# 🔹 **2. Pod Affinity & Anti-Affinity**

* **Pod Affinity** → Schedule Pod **close to other pods** with matching labels (same node, same topology).
* **Pod Anti-Affinity** → Schedule Pod **away from other pods** with matching labels.
* Useful for **co-locating apps** or **spreading workloads**.

---

## ✅ Pod Affinity Types

1. **requiredDuringSchedulingIgnoredDuringExecution** → hard rule
2. **preferredDuringSchedulingIgnoredDuringExecution** → soft rule

---

## 🔹 Pod Affinity YAML Example

### Example 1: Pod Affinity (co-locate)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-affinity-example
  labels:
    app: frontend
spec:
  containers:
  - name: nginx
    image: nginx
  affinity:
    podAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values:
            - frontend
        topologyKey: "kubernetes.io/hostname"
```

✅ Pod will be scheduled **on the same node** as other pods with `app=frontend`.

---

### Example 2: Pod Anti-Affinity (spread)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-anti-affinity-example
  labels:
    app: backend
spec:
  containers:
  - name: nginx
    image: nginx
  affinity:
    podAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 1
        podAffinityTerm:
          labelSelector:
            matchExpressions:
            - key: app
              operator: In
              values:
              - backend
          topologyKey: "kubernetes.io/hostname"
```

✅ Scheduler prefers **not to schedule on nodes** with other `app=backend` pods (spreading workloads).

---

# 🔹 **Key Notes**

| Feature          | Node Affinity                        | Pod Affinity / Anti-Affinity                        |
| ---------------- | ------------------------------------ | --------------------------------------------------- |
| Scope            | Nodes                                | Pods (same node or topology domain)                 |
| Hard vs Soft     | Yes                                  | Yes                                                 |
| Operator support | In, NotIn, Exists, Gt, Lt            | In, NotIn, Exists                                   |
| Common Use       | Hardware constraints, zones, regions | Co-locating apps or spreading workloads             |
| YAML Key         | `affinity.nodeAffinity`              | `affinity.podAffinity` / `affinity.podAntiAffinity` |

---

# 🔹 **Summary**

* **Node Affinity** → controls **which nodes** pods land on.
* **Pod Affinity** → schedule pods **with other pods** (co-locate).
* **Pod Anti-Affinity** → schedule pods **away from other pods** (spread workloads).
* Preferred vs Required allows **soft vs hard rules**.

---
👍 — Let’s go step by step. Node Affinity and Pod Affinity are **advanced scheduling rules** in Kubernetes, more flexible than `nodeSelector`.

---

# 🔹 **1. Node Affinity**

* **Definition**: A set of rules that constrain which **nodes a Pod can be scheduled on** based on node labels.
* **More advanced than NodeSelector**:

  * Can use **soft vs hard rules** (preferred vs required).
  * Supports **operators** (`In`, `NotIn`, `Exists`, `Gt`, `Lt`).

---

## ✅ Node Affinity Types

1. **requiredDuringSchedulingIgnoredDuringExecution** (hard requirement)

   * Pod **must** be scheduled on nodes matching the rule.
2. **preferredDuringSchedulingIgnoredDuringExecution** (soft preference)

   * Scheduler **tries** to place Pod on matching nodes, but it’s not mandatory.

---

## 🔹 Node Affinity YAML Examples

### Example 1: Hard Node Affinity

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hard-affinity-pod
spec:
  containers:
  - name: nginx
    image: nginx
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: disktype
            operator: In
            values:
            - ssd
```

✅ Pod **must** run on a node with label `disktype=ssd`.

---

### Example 2: Soft Node Affinity

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: soft-affinity-pod
spec:
  containers:
  - name: nginx
    image: nginx
  affinity:
    nodeAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 1
        preference:
          matchExpressions:
          - key: region
            operator: In
            values:
            - us-east
```

✅ Scheduler **prefers nodes** with `region=us-east` but can schedule elsewhere if needed.

---

# 🔹 **2. Pod Affinity & Anti-Affinity**

* **Pod Affinity** → Schedule Pod **close to other pods** with matching labels (same node, same topology).
* **Pod Anti-Affinity** → Schedule Pod **away from other pods** with matching labels.
* Useful for **co-locating apps** or **spreading workloads**.

---

## ✅ Pod Affinity Types

1. **requiredDuringSchedulingIgnoredDuringExecution** → hard rule
2. **preferredDuringSchedulingIgnoredDuringExecution** → soft rule

---

## 🔹 Pod Affinity YAML Example

### Example 1: Pod Affinity (co-locate)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-affinity-example
  labels:
    app: frontend
spec:
  containers:
  - name: nginx
    image: nginx
  affinity:
    podAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values:
            - frontend
        topologyKey: "kubernetes.io/hostname"
```

✅ Pod will be scheduled **on the same node** as other pods with `app=frontend`.

---

### Example 2: Pod Anti-Affinity (spread)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-anti-affinity-example
  labels:
    app: backend
spec:
  containers:
  - name: nginx
    image: nginx
  affinity:
    podAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 1
        podAffinityTerm:
          labelSelector:
            matchExpressions:
            - key: app
              operator: In
              values:
              - backend
          topologyKey: "kubernetes.io/hostname"
```

✅ Scheduler prefers **not to schedule on nodes** with other `app=backend` pods (spreading workloads).

---

# 🔹 **Key Notes**

| Feature          | Node Affinity                        | Pod Affinity / Anti-Affinity                        |
| ---------------- | ------------------------------------ | --------------------------------------------------- |
| Scope            | Nodes                                | Pods (same node or topology domain)                 |
| Hard vs Soft     | Yes                                  | Yes                                                 |
| Operator support | In, NotIn, Exists, Gt, Lt            | In, NotIn, Exists                                   |
| Common Use       | Hardware constraints, zones, regions | Co-locating apps or spreading workloads             |
| YAML Key         | `affinity.nodeAffinity`              | `affinity.podAffinity` / `affinity.podAntiAffinity` |

---

# 🔹 **Summary**

* **Node Affinity** → controls **which nodes** pods land on.
* **Pod Affinity** → schedule pods **with other pods** (co-locate).
* **Pod Anti-Affinity** → schedule pods **away from other pods** (spread workloads).
* Preferred vs Required allows **soft vs hard rules**.

---

# 🔹 **What is `weight` in Kubernetes Affinity?**

* **Weight** is used **only in `preferredDuringSchedulingIgnoredDuringExecution`** (soft rules).
* It defines **how strongly the scheduler should try to satisfy this preference**.
* Range: **1–100** (1 = lowest priority, 100 = highest priority).
* Multiple soft rules can be defined, and **weight determines which rule is more important**.

---

# 🔹 **How Weight Works**

* Scheduler evaluates all nodes.
* For each node, it calculates a **score** based on which preferences are matched.
* Node with **highest total score** is preferred.
* Weight lets you **prioritize some rules over others**.

---

# 🔹 **Node Affinity Example with Weight**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: weighted-node-affinity
spec:
  containers:
  - name: nginx
    image: nginx
  affinity:
    nodeAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 5
        preference:
          matchExpressions:
          - key: region
            operator: In
            values:
            - us-east
      - weight: 10
        preference:
          matchExpressions:
          - key: disktype
            operator: In
            values:
            - ssd
```

✅ **Interpretation**:

* Scheduler **prefers nodes with `disktype=ssd` more strongly** than nodes in `region=us-east`.
* Both are soft preferences, but `disktype=ssd` has **double the priority** (weight 10 vs 5).

---

# 🔹 **Pod Affinity Example with Weight**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: weighted-pod-affinity
  labels:
    app: frontend
spec:
  containers:
  - name: nginx
    image: nginx
  affinity:
    podAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 50
        podAffinityTerm:
          labelSelector:
            matchExpressions:
            - key: app
              operator: In
              values:
              - frontend
          topologyKey: "kubernetes.io/hostname"
      - weight: 20
        podAffinityTerm:
          labelSelector:
            matchExpressions:
            - key: env
              operator: In
              values:
              - prod
          topologyKey: "failure-domain.beta.kubernetes.io/zone"
```

✅ **Interpretation**:

* Scheduler **strongly prefers pods on the same node as other `app=frontend` pods** (weight 50).
* It also prefers pods in the same zone as `env=prod` pods, but with **lower priority** (weight 20).

---

# 🔹 **Key Points**

1. **Weight only applies to soft preferences** (`preferredDuringSchedulingIgnoredDuringExecution`).
2. **Hard rules** (`requiredDuringSchedulingIgnoredDuringExecution`) are **mandatory**, weight does not apply.
3. Multiple soft preferences **sum their weights** for scoring.
4. Higher weight → **higher priority** in scheduling.

---

