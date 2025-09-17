# ReplicaSet (RS), ReplicationController (RC), and Deployment in Kubernetes

---

# 🔹 1. ReplicationController (RC)

### ✅ What it is:

* One of the **oldest controllers** in Kubernetes.
* Ensures a **specified number of Pod replicas** are running at all times.
* If a Pod dies, it creates a new one. If extra Pods exist, it deletes them.
* **Now replaced by ReplicaSet** (deprecated but still supported for backward compatibility).

### 🛠 Backend functioning:

* Continuously watches the API server.
* Compares the **desired state (spec.replicas)** with the **current state (running pods)**.
* If mismatch → adds/deletes pods to match desired state.

### 📄 Example RC YAML:

```yaml
apiVersion: v1
kind: ReplicationController
metadata:
  name: my-rc
spec:
  replicas: 3   # Desired number of pods
  selector:
    app: myapp   # Which pods to manage
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: mycontainer
        image: nginx:1.17
        ports:
        - containerPort: 80
```

### 🔑 Important Terms:

* **replicas** → Desired number of pods
* **selector** → Which pods RC controls (based on labels)
* **template** → Pod template (blueprint for new pods)

---

# 🔹 2. ReplicaSet (RS)

### ✅ What it is:

* **Modern replacement** for RC.
* Works the same way but **supports more advanced label selectors** (e.g., `matchExpressions`).
* Rarely used directly → usually created by **Deployment**.

### 🛠 Backend functioning:

* Same as RC, but smarter in **label matching**.
* Makes sure the exact number of replicas are running.
* If you scale replicas up/down → RS ensures it happens.

### 📄 Example RS YAML:

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: my-rs
spec:
  replicas: 3
  selector:
    matchLabels:    # Advanced selectors possible
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: mycontainer
        image: nginx:1.18
        ports:
        - containerPort: 80
```

### 🔑 Important Terms:

* **replicas** → Desired pod count
* **selector.matchLabels** → Matches pods with specific labels
* **template** → Pod definition
* **matchExpressions** (only in RS, not in RC):
  Example:

  ```yaml
  selector:
    matchExpressions:
    - key: tier
      operator: In
      values:
        - frontend
        - backend
  ```

---

# 🔹 3. Deployment

### ✅ What it is:

* A **higher-level controller** that manages ReplicaSets.
* Provides **rolling updates**, **rollbacks**, and easy scaling.
* You almost always use **Deployment** instead of RS directly.

### 🛠 Backend functioning:

* When you create a Deployment → it creates a **ReplicaSet**.
* During updates:

  * Creates a **new RS** with the updated pod template.
  * Gradually scales **down old RS** and **up new RS** (rolling update).
* Rollback → switches back to the old RS.

### 📄 Example Deployment YAML:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  strategy:               # Deployment strategy
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1   # At most 1 pod unavailable during update
      maxSurge: 1         # At most 1 extra pod created
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: mycontainer
        image: nginx:1.19
        ports:
        - containerPort: 80
```

### 🔑 Important Terms:

* **replicas** → How many pods Deployment wants
* **selector** → Links to RS labels
* **strategy** → Update strategy (RollingUpdate / Recreate)
* **rollingUpdate** → Fine-tunes update behavior
* **revisionHistoryLimit** → Number of old RS versions to keep for rollback

---

# 🔹 Key Differences (RC vs RS vs Deployment)

| Feature           | ReplicationController (RC) | ReplicaSet (RS)         | Deployment                    |
| ----------------- | -------------------------- | ----------------------- | ----------------------------- |
| Status            | Deprecated (old)           | Active, but rarely used | Most commonly used            |
| Label selectors   | Only equality-based        | Equality + expressions  | Uses RS underneath            |
| Updates (rolling) | Manual                     | Manual                  | Automatic (rolling, rollback) |
| Rollback support  | ❌ No                       | ❌ No                    | ✅ Yes                         |
| Usage today       | Rare (legacy apps)         | Created by Deployment   | Standard for apps             |

---
### Service to run the application

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-nodeport
spec:
  type: NodePort
  selector:
    app: myapp   # Must match Deployment/Pod labels
  ports:
  - port: 80           # Service Port (cluster-internal)
    targetPort: 80     # Container Port
    nodePort: 30080    # NodePort (range 30000-32767)
```

✅ With this:

Option 1: Access via NodePort → http://<NodeIP>:30080

Option 2: Port forward → kubectl port-forward svc/java-deepak-webapp-svc 8080:80 -n test-ns
---

# 🔹 Why We Need Them

* **RC**: Historical, first version → ensured pod replication.
* **RS**: Improved, flexible label selection.
* **Deployment**: The **real-world tool** → handles lifecycle, updates, and rollbacks with zero downtime.

---

👉 So, in practice:

* You don’t use **RC** anymore (legacy only).
* You don’t use **RS** directly (Deployment manages it).
* You almost always use a **Deployment** to run stateless apps.

---
