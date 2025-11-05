## 1. Node Selector

### Basic Concept
Node Selector is the simplest way to schedule pods onto specific nodes based on node labels.

### Important Terms
- **Node Labels**: Key-value pairs attached to nodes
- **Selector**: Criteria defined in pod spec to match node labels

### Example
```yaml
# Label nodes
kubectl label nodes node1 disktype=ssd
kubectl label nodes node2 disktype=hdd

# Pod using nodeSelector
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

## 2. Node Affinity

### Types of Node Affinity

#### 1. requiredDuringSchedulingIgnoredDuringExecution
- **Hard requirement**: Pod MUST be scheduled on nodes meeting criteria
- If no matching node found, pod remains pending

#### 2. preferredDuringSchedulingIgnoredDuringExecution
- **Soft requirement**: Kubernetes tries to schedule but doesn't guarantee
- Uses weights (1-100) to indicate preference strength

### Important Terms
- **matchExpressions**: Complex matching rules
- **operator**: In, NotIn, Exists, DoesNotExist, Gt, Lt
- **weight**: For preferred rules (1-100)

### Examples

#### Required Node Affinity
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-required-affinity
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: disktype
            operator: In
            values:
            - ssd
            - nvme
          - key: gpu
            operator: Exists
  containers:
  - name: nginx
    image: nginx
```

#### Preferred Node Affinity with Weights
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-preferred-affinity
spec:
  affinity:
    nodeAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 80
        preference:
          matchExpressions:
          - key: disktype
            operator: In
            values:
            - ssd
      - weight: 20
        preference:
          matchExpressions:
          - key: environment
            operator: In
            values:
            - development
  containers:
  - name: nginx
    image: nginx
```

## 3. Pod Affinity & Anti-Affinity

### Types

#### 1. Pod Affinity
- Schedule pod **close to** other pods meeting criteria
- Useful for co-locating related pods

#### 2. Pod Anti-Affinity
- Schedule pod **away from** other pods meeting criteria
- Useful for high availability and spreading workload

### Scope
- **namespaces**: Which namespaces to consider for matching
- **topologyKey**: Defines the domain for affinity/anti-affinity

### Operators
- In, NotIn, Exists, DoesNotExist

### Weights in Pod Affinity/Anti-Affinity
- Only available for **preferredDuringSchedulingIgnoredDuringExecution**
- Range: 1-100
- Higher weight = stronger preference

## Examples

### Pod Anti-Affinity (Required)
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-server
  labels:
    app: web
spec:
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values:
            - web
        topologyKey: kubernetes.io/hostname
  containers:
  - name: web
    image: nginx
```

### Pod Affinity with Weights (Preferred)
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: cache-pod
  labels:
    app: cache
spec:
  affinity:
    podAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchExpressions:
            - key: app
              operator: In
              values:
              - database
          topologyKey: kubernetes.io/hostname
      - weight: 50
        podAffinityTerm:
          labelSelector:
            matchExpressions:
            - key: tier
              operator: In
              values:
              - backend
          topologyKey: topology.kubernetes.io/zone
  containers:
  - name: cache
    image: redis
```

## Complete Demo

Let me create a comprehensive demo covering all concepts:

### Step 1: Setup Nodes with Labels
```bash
# Label nodes (assuming 3-node cluster)
kubectl label nodes minikube disktype=ssd environment=production zone=zone-a
kubectl label nodes minikube-m02 disktype=hdd environment=staging zone=zone-b
kubectl label nodes minikube-m03 disktype=ssd environment=development zone=zone-a

# Verify labels
kubectl get nodes --show-labels

<img width="1898" height="269" alt="image" src="https://github.com/user-attachments/assets/9e9f8c42-5c83-4fab-8bcb-31db21f51843" />

```

### Step 2: Node Selector Demo
```yaml
# node-selector-demo.yaml
apiVersion: v1
kind: Pod
metadata:
  name: node-selector-pod
spec:
  containers:
  - name: nginx
    image: nginx
  nodeSelector:
    disktype: ssd
```
<img width="1085" height="152" alt="image" src="https://github.com/user-attachments/assets/e42035c6-f31c-4094-a51b-21433db580bf" />

---

## 🎯 Scenario:

You have multiple nodes with the **same label**, e.g.:

```bash
kubectl label node node1 disktype=ssd
kubectl label node node2 disktype=ssd
kubectl label node node3 disktype=ssd
```

And your pod uses a `nodeSelector` like:

```yaml
nodeSelector:
  disktype: ssd
```

---

## 🧠 What Happens:

When **multiple nodes match** the `nodeSelector` condition —
→ the **Kubernetes Scheduler** still has to choose **one node** to place the Pod.

Since `nodeSelector` only *filters eligible nodes*, the final choice depends on **Kubernetes scheduler’s internal scoring mechanism** (known as **Scheduling Policies**).

---

## ⚙️ Scheduler Decision Steps (Simplified)

### **Step 1: Filtering**

* Scheduler filters nodes that meet **all constraints**, like:

  * `nodeSelector` match ✅
  * Sufficient CPU/memory ✅
  * No taint mismatch ✅

👉 Suppose all 3 nodes (node1, node2, node3) pass filtering.

---

### **Step 2: Scoring**

* Scheduler assigns a **score (0–100)** to each eligible node.
* It uses various **built-in scoring plugins**, like:

  * `LeastRequestedPriority`: prefer nodes with more free resources.
  * `BalancedAllocation`: prefer balanced CPU/memory usage.
  * `ImageLocality`: prefer nodes already having the image.
  * `TopologySpreadConstraints`: for spreading pods.

👉 The scheduler picks the node with the **highest total score**.

If multiple nodes have the same score → it chooses **randomly** among them.

---

### 🧩 Example (Illustration)

| Node  | Label Match | Free CPU | Image Present | Final Score |
| ----- | ----------- | -------- | ------------- | ----------- |
| node1 | ✅           | 40%      | ✅             | 80          |
| node2 | ✅           | 60%      | ❌             | 70          |
| node3 | ✅           | 30%      | ✅             | 60          |

➡️ Pod will be scheduled on **node1** because it has the **highest total score** after internal calculations.

---

## 🧾 Summary:

| Step          | Description                                                               |
| ------------- | ------------------------------------------------------------------------- |
| 1️⃣ Filtering | Removes ineligible nodes (based on nodeSelector, taints, resources, etc.) |
| 2️⃣ Scoring   | Assigns preference scores to the remaining nodes                          |
| 3️⃣ Binding   | Schedules Pod on the **highest-scored** node (or random if tied)          |

---

### ⚠️ Important:

* You **cannot control** which node among matching labels the pod goes to using `nodeSelector` alone.
* To influence it, you’d use:

  * **Node Affinity** with weights, or
  * **Pod Topology Spread Constraints** (for even distribution).

---

### 🧩 Tip for CKA Exam:

If they ask —

> “What happens when multiple nodes satisfy a `nodeSelector` condition?”

✅ Answer:

> The scheduler filters all nodes that match the selector, scores them based on available resources and internal policies, and then places the Pod on the node with the highest score (or randomly if equal).

---

### Step 3: Node Affinity Demo
```yaml
# node-affinity-demo.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: node-affinity-demo
spec:
  replicas: 3
  selector:
    matchLabels:
      app: node-affinity-app
  template:
    metadata:
      labels:
        app: node-affinity-app
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: disktype
                operator: In
                values:
                - ssd
                - nvme
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 70
            preference:
              matchExpressions:
              - key: environment
                operator: In
                values:
                - production
          - weight: 30
            preference:
              matchExpressions:
              - key: zone
                operator: In
                values:
                - zone-a
      containers:
      - name: nginx
        image: nginx
```

<img width="1253" height="150" alt="image" src="https://github.com/user-attachments/assets/722883ad-fb9d-4cb4-b9d9-9164aa514cf2" />

### Step 4: Pod Anti-Affinity for High Availability
```yaml
# pod-anti-affinity-demo.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ha-web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ha-web
  template:
    metadata:
      labels:
        app: ha-web
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - ha-web
              topologyKey: kubernetes.io/hostname
          - weight: 50
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - ha-web
              topologyKey: topology.kubernetes.io/zone
      containers:
      - name: web
        image: nginx
```

<img width="1240" height="154" alt="image" src="https://github.com/user-attachments/assets/424fcfb0-6c46-416c-b195-645d7eda7dab" />


---

## 🔹 Concept: Pod Anti-Affinity

**Pod Anti-Affinity** ensures that a pod **prefers (or requires)** **not** to be scheduled on the same node (or topology domain) as other pods matching certain labels.

* **Affinity** → “I want to be close to these pods”
* **Anti-Affinity** → “I want to avoid these pods”

This is useful for **high availability**, **spreading replicas**, or avoiding a single-node failure.

---

## 🔹 Your YAML Explained

```yaml
spec:
  affinity:
    podAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchExpressions:
            - key: app
              operator: In
              values:
              - ha-web
          topologyKey: kubernetes.io/hostname
      - weight: 50
        podAffinityTerm:
          labelSelector:
            matchExpressions:
            - key: app
              operator: In
              values:
              - ha-web
          topologyKey: topology.kubernetes.io/zone
```

---

### 1️⃣ `preferredDuringSchedulingIgnoredDuringExecution`

* **Soft rule** → scheduler **prefers** to satisfy it but can ignore it if necessary.
* Unlike `requiredDuringSchedulingIgnoredDuringExecution` which is **mandatory**, soft rules only **influence scoring**.

---

### 2️⃣ `weight: 100` & `weight: 50`

* **Weight** determines the **priority of this anti-affinity rule** when choosing a node.
* Higher weight → scheduler **strongly prefers to avoid** violating this rule.
* Lower weight → less strict, softer preference.

In your case:

* `weight: 100` → avoid other `ha-web` pods **on the same node** (hostname level)
* `weight: 50` → avoid other `ha-web` pods **in the same zone** (topology spread level)

---

### 3️⃣ `podAffinityTerm`

This defines **which pods to avoid** and **where**:

#### a) `labelSelector`

```yaml
labelSelector:
  matchExpressions:
  - key: app
    operator: In
    values:
    - ha-web
```

* Scheduler looks for pods with label `app=ha-web`.
* The anti-affinity rule applies only to these pods.

#### b) `topologyKey`

```yaml
topologyKey: kubernetes.io/hostname
```

* The **domain to consider**.
* `kubernetes.io/hostname` → node level → avoid scheduling on the **same node** as matching pods.
* `topology.kubernetes.io/zone` → zone level → avoid scheduling in the **same zone** as matching pods (multi-AZ clusters).

---

### 4️⃣ How Scheduler Uses This

1. Scheduler finds **eligible nodes** based on **other constraints** (resources, taints, node affinity, etc.)
2. For each eligible node, scheduler **calculates a score**:

   * If a node **violates anti-affinity** (e.g., already has a pod `ha-web` on the same node), the score is **reduced based on weight**.
   * Nodes that satisfy the anti-affinity rule get **higher scores**.
3. Pod is scheduled on the node with the **highest total score**.

---

### 🔹 Example Scenario

Suppose you have 3 nodes:

| Node  | Pods running | Zone   |
| ----- | ------------ | ------ |
| node1 | ha-web-1     | zone-a |
| node2 | none         | zone-a |
| node3 | ha-web-2     | zone-b |

**Scheduling a new `ha-web` pod**:

* **Weight 100, hostname anti-affinity**: scheduler avoids node1 & node3 **because both have `ha-web` on the same node** → only node2 is preferred.
* **Weight 50, zone anti-affinity**: if node2 is in zone-a (same as node1), it slightly reduces score but still preferable.

✅ Result: Pod is scheduled on **node2** — spreads pods across nodes and zones, achieving high availability.

---

### 🔹 Key Points

| Field                                             | Notes                                                       |
| ------------------------------------------------- | ----------------------------------------------------------- |
| `podAntiAffinity`                                 | Avoid pods matching a label on same node/zone/etc.          |
| `preferredDuringSchedulingIgnoredDuringExecution` | Soft rule → scheduler may ignore if necessary               |
| `weight`                                          | Determines importance of the soft rule (1-100)              |
| `topologyKey`                                     | Level to apply the anti-affinity (node, zone, region, etc.) |
| `labelSelector`                                   | Defines which pods to consider for anti-affinity            |

---

💡 **Tip for CKA:**

* Use **hostname** for node-level HA.
* Use **zone** for multi-AZ HA.
* Use **weights** to prioritize one rule over another.
* Anti-affinity does **not prevent scheduling entirely** unless `requiredDuringSchedulingIgnoredDuringExecution` is used.

---



### Step 5: Pod Affinity for Co-location
```yaml
# pod-affinity-demo.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: database
spec:
  replicas: 2
  selector:
    matchLabels:
      app: database
      tier: backend
  template:
    metadata:
      labels:
        app: database
        tier: backend
    spec:
      containers:
      - name: db
        image: postgres:13
        env:
        - name: POSTGRES_PASSWORD
          value: mysecretpassword
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cache
spec:
  replicas: 2
  selector:
    matchLabels:
      app: cache
      tier: backend
  template:
    metadata:
      labels:
        app: cache
        tier: backend
    spec:
      affinity:
        podAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 80
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - database
              topologyKey: kubernetes.io/hostname
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - cache
            topologyKey: kubernetes.io/hostname
      containers:
      - name: redis
        image: redis:6
```

<img width="1197" height="182" alt="image" src="https://github.com/user-attachments/assets/ff936b07-0812-490e-bc95-c51b456230f9" />


### Step 6: Deploy and Verify
```bash
# Apply all manifests
kubectl apply -f node-selector-demo.yaml
kubectl apply -f node-affinity-demo.yaml
kubectl apply -f pod-anti-affinity-demo.yaml
kubectl apply -f pod-affinity-demo.yaml

# Check pod placement
kubectl get pods -o wide

# Check node assignments
kubectl describe pods | grep -A 5 "Node:"

# Verify anti-affinity (pods should be on different nodes)
kubectl get pods -l app=ha-web -o wide

# Verify affinity (cache and database should try to co-locate)
kubectl get pods -l tier=backend -o wide
```

## Key Differences Summary

| Feature | Node Selector | Node Affinity | Pod Affinity/Anti-Affinity |
|---------|---------------|---------------|----------------------------|
| **Complexity** | Simple | Complex | Most Complex |
| **Operators** | Equality only | In, NotIn, Exists, etc. | In, NotIn, Exists, etc. |
| **Weights** | No | Yes (preferred) | Yes (preferred) |
| **Scope** | Node labels | Node labels | Pod labels + topology |
| **Use Case** | Simple node selection | Advanced node selection | Pod placement relative to other pods |

## Best Practices

1. **Use Node Selector** for simple requirements
2. **Use Node Affinity** for complex node selection rules
3. **Use Pod Anti-Affinity** for high availability
4. **Use Pod Affinity** for performance (co-locating related services)
5. **Start with preferred** rules and use required only when necessary
6. **Use weights** to prioritize multiple preferences

This comprehensive guide should give you solid understanding of Kubernetes scheduling constraints for your CKA exam preparation!






