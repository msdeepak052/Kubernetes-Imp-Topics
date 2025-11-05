## What are Static Pods?

Static Pods are pods that are managed **directly by the `kubelet` agent** on a specific node, rather than by the Kubernetes API server (e.g., via a Deployment, DaemonSet). The `kubelet` watches a directory on the node's filesystem (`/etc/kubernetes/manifests/` by default) and automatically creates, deletes, and restarts the pods defined by the YAML/JSON files it finds there.

## Why Are They Used? The Critical Use Case

The primary and most important use case for Static Pods is **bootstrapping the Kubernetes control plane itself.**

Think about the chicken-and-egg problem:
*   To have a cluster, you need the API server running.
*   But the API server is what's supposed to manage pods (like the API server pod!).

Static Pods solve this:
1.  You install `kubelet` on a node.
2.  You place a Pod manifest for `kube-apiserver`, `kube-controller-manager`, `kube-scheduler`, and `etcd` in the Static Pod directory.
3.  The `kubelet` reads this directory and starts these pods.
4.  **Now your control plane is running.** Once the API server is up, the `kubelet` can then register the node with the API server and report the status of the Static Pods it's running.

**Other use cases include:**
*   Running a cluster-level component that must be running before the API server is available.
*   Running a custom node-level agent that is too critical to be managed by the cluster's scheduler (which depends on the API server being healthy).

---

## How are They Controlled?

Static Pods are controlled in a very simple way: **by directly managing files on the node's filesystem.**

*   **To create a Static Pod:** Place a valid Pod manifest file (`.yaml` or `.json`) in the designated directory (e.g., `/etc/kubernetes/manifests/`).
*   **To update a Static Pod:** Edit the manifest file in place. The `kubelet` will detect the change and restart the pod with the new configuration.
*   **To delete a Static Pod:** Remove the manifest file from the directory. The `kubelet` will terminate the pod.

This is very different from "normal" pods, which are controlled by sending commands to the API server (`kubectl apply/delete`).

### The "Mirror Pod" Concept

There's a clever trick that makes Static Pods visible in the Kubernetes API. For each Static Pod it creates, the `kubelet` automatically creates a **Mirror Pod** in the Kubernetes API server.

*   The **Mirror Pod** is a read-only representation of the Static Pod.
*   You can see it with `kubectl get pods`.
*   **You cannot manage the Mirror Pod with `kubectl`.** If you try to `kubectl delete` a Mirror Pod, it will be recreated moments later by the `kubelet` because the static manifest file still exists on the node.
*   The Mirror Pod's name is typically prefixed with the node name (e.g., `kube-apiserver-my-master-node`).

This allows cluster administrators to use `kubectl` to check the status of the critical control plane components running as Static Pods.

---

## Where Do They Reside?

Static Pod manifests reside on the **local filesystem of the node** where they are meant to run. The specific directory is defined by the `kubelet`'s configuration.

*   **The default location is `/etc/kubernetes/manifests/`.** This is the path used by most installation tools like `kubeadm`.
*   The exact path can be set by the `--pod-manifest-path` argument passed to the `kubelet` process.

You can find the exact path on a node by checking the `kubelet` process:

```bash
# SSH into a node (especially a control-plane node)
ssh master-node

# Check the kubelet process to see the configured manifest path
ps aux | grep kubelet | grep manifest-path
# You will often see: ... /usr/bin/kubelet ... --pod-manifest-path=/etc/kubernetes/manifests ...
```

---

## Practical Example: Let's Look at a Real Control Plane

This is the best way to understand. If you set up a cluster with `kubeadm`, your control plane components are Static Pods.

**1. Let's see the pods. Notice the node names in the pod names:**
```bash
kubectl get pods -n kube-system -o wide
```
You will see pods like this (note the `control-plane` node name in each pod name):
```
NAME                               READY   STATUS    RESTARTS   AGE
etcd-control-plane                 1/1     Running   0          10d
kube-apiserver-control-plane       1/1     Running   0          10d
kube-controller-manager-control-plane  1/1     Running   0          10d
kube-scheduler-control-plane       1/1     Running   0          10d
coredns-xxxxxx-yyy                 1/1     Running   0          10d
...other pods...
```
The ones with the node name prefix are the Mirror Pods for the Static Pods.

**2. Now, let's SSH into the control-plane node and look at the manifest directory:**
```bash
# SSH into your master node (named 'control-plane' in this example)
ssh control-plane

# List the contents of the static pod manifest directory
ls -la /etc/kubernetes/manifests/
```
You will see the actual YAML files that define the control plane:
```
total 32
-rw------- 1 root root 2290 Feb 19 12:34 etcd.yaml
-rw------- 1 root root 3983 Feb 19 12:34 kube-apiserver.yaml
-rw------- 1 root root 3411 Feb 19 12:34 kube-controller-manager.yaml
-rw------- 1 root root 1425 Feb 19 12:34 kube-scheduler.yaml
```

**3. Let's examine one of these files (e.g., the API server):**
```bash
cat /etc/kubernetes/manifests/kube-apiserver.yaml
```
You will see a perfectly normal Pod manifest! It defines a pod with the `kube-apiserver` container, its command arguments, liveness probes, and volumes (like TLS certificates for secure communication).

**4. Try to delete it via kubectl (it will restart!):**
```bash
# From your local machine, not the node, try to delete the API server pod
kubectl delete pod -n kube-system kube-apiserver-control-plane

# Watch it get deleted and then almost immediately recreated.
kubectl get pods -n kube-system -w | grep apiserver

# The pod will have a new age and restarted count, but it's back.
# This proves you can't manage it via the API; you must manage the file on the node.
```

## Summary

| Feature | Static Pods | Normal Pods (via API) |
| :--- | :--- | :--- |
| **Managed by** | The `kubelet` on a specific node | The Kubernetes API Server & Controllers |
| **Configuration** | YAML/JSON files on the node's filesystem | API objects (e.g., `kubectl apply`, Deployments) |
| **Deletion** | Remove the manifest file | `kubectl delete pod <name>` |
| **Primary Use** | Bootstrapping control plane components | All regular application workloads |
| **Visibility** | Visible as read-only **Mirror Pods** in the API | Fully manageable API objects |

In short, **Static Pods are the foundation upon which a self-hosted Kubernetes control plane is built.** They provide a simple, reliable mechanism to get the cluster's management services running before the cluster itself fully exists.

---

# 🔄 Manual Rescheduling in Kubernetes

## 🔹 What does it mean?

* In Kubernetes, **Pods are not automatically rescheduled** if a node becomes unschedulable (e.g., deleted, cordoned, or fails) **unless** the Pod is controlled by a higher-level controller like a **Deployment, ReplicaSet, StatefulSet, or DaemonSet**.
* **Manual rescheduling** refers to **manually intervening** to move workloads (Pods) to a healthy node.

---

## 🔹 Why is Manual Rescheduling Needed?

1. **Static Pods or standalone Pods**

   * If you created Pods **without a controller**, they will not reschedule automatically when a node fails.
2. **Maintenance of a node**

   * When draining/cordoning a node, workloads must move elsewhere.
3. **Performance or troubleshooting**

   * If you need to move Pods to a different node for debugging or performance balancing.
4. **Testing scenarios**

   * To see how apps behave when Pods are deleted or recreated.

---

## 🔹 Ways to Do Manual Rescheduling

### 1️⃣ Delete the Pod (controller recreates it on a new node)

If the Pod is managed by a **Deployment/ReplicaSet/StatefulSet**:

```bash
kubectl delete pod <pod-name>
```

* The controller will immediately create a new Pod on a healthy node.

📌 Example with Deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deploy
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
        image: nginx:latest
```

👉 If you delete one Pod, a new one is scheduled automatically on another node.

---

### 2️⃣ Evict Pods from a Node (Cordon & Drain)

When you want to move workloads away from a specific node:

```bash
kubectl cordon <node-name>   # Mark node unschedulable
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data
```

* All Pods (except DaemonSet and static Pods) will be evicted and rescheduled elsewhere.
* Useful for **node maintenance**.

---

### 3️⃣ Manually Edit Pod Spec (Not Recommended in Prod)

For standalone Pods (no controller), you can:

```bash
kubectl delete pod <pod-name>
kubectl apply -f pod.yaml
```

If you add `nodeSelector` or `affinity` in YAML, you can force it onto a different node.

📌 Example:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
spec:
  nodeSelector:
    kubernetes.io/hostname: worker-node-2   # force scheduling on worker-node-2
  containers:
  - name: nginx
    image: nginx
```

---

### 4️⃣ Pod Disruption Budgets (PDBs) + Evictions

You can set **PodDisruptionBudget** to control voluntary disruptions (like manual rescheduling during drain).

📌 Example PDB:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: nginx-pdb
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: nginx
```

* Ensures at least **1 Pod always stays running** during rescheduling.

---

## 🔹 Summary

* **Manual Rescheduling** = moving Pods when they don’t move automatically.
* Needed for: **standalone Pods, node failures, maintenance, balancing**.
* Types:

  1. Delete Pod (controller reschedules it)
  2. Cordon + Drain node (evicts Pods)
  3. Reapply Pod with `nodeSelector` / `affinity`
  4. Use PDBs to control safe evictions


---

# 🔹 **Labels in Kubernetes**

* **Definition**: Labels are key-value pairs attached to Kubernetes objects (Pods, Services, Deployments, etc.).
* **Purpose**:

  * Organize and categorize resources.
  * Allow grouping of objects for operations (like scaling, monitoring, or cleanup).
  * Work as “tags” for filtering.

👉 Syntax:

```yaml
metadata:
  labels:
    key: value
```

### Example: Labeling Pods

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
    env: dev
spec:
  containers:
  - name: nginx
    image: nginx
```

Here, the pod has **two labels**:

* `app: nginx`
* `env: dev`

---

# 🔹 **Selectors in Kubernetes**

* **Definition**: Selectors are used to **filter or match objects** based on labels.
* **Usage**:

  * Services → select Pods.
  * ReplicaSets/Deployments → manage Pods.
  * Jobs, CronJobs, and DaemonSets also use selectors.

👉 Types of Label Selectors:

1. **Equality-based**

   * Check for equality (`=` or `==`) or inequality (`!=`).
   * Example: `env = dev`
2. **Set-based**

   * Check whether label values belong to a set.
   * Example: `env in (dev, qa)` OR `tier notin (frontend)`

---

# 🔹 **Example 1: Service with Label Selector**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx        # selects pods with label app=nginx
  ports:
    - port: 80
      targetPort: 80
```

👉 This service automatically selects all pods labeled with `app=nginx`.

---

# 🔹 **Example 2: Deployment with Labels**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx       # must match pod labels
  template:
    metadata:
      labels:
        app: nginx
        env: prod
    spec:
      containers:
      - name: nginx
        image: nginx
```

Here:

* The **Deployment selector** matches pods with `app: nginx`.
* Extra labels like `env: prod` help differentiate.

---

# 🔹 **Example 3: Set-based Selector in ReplicaSet**

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: nginx-rs
spec:
  replicas: 2
  selector:
    matchExpressions:
      - key: env
        operator: In
        values:
          - dev
          - qa
  template:
    metadata:
      labels:
        app: nginx
        env: dev
    spec:
      containers:
      - name: nginx
        image: nginx
```

👉 This ReplicaSet manages pods only if `env=dev` OR `env=qa`.

---

# 🔹 Why are Labels & Selectors Needed?

* Flexible grouping without rigid hierarchy.
* Attach **environment info** (`env=prod`, `env=dev`).
* Identify **application tiers** (`tier=frontend`, `tier=backend`, `tier=db`).
* Useful in **rollouts, monitoring, scaling, CI/CD pipelines**.
* Critical for **network policies, service discovery, scheduling**.

---

# 🔹 Key Commands

```bash
# Get pods with a label
kubectl get pods -l app=nginx

# Get pods with set-based selector
kubectl get pods -l 'env in (dev,qa)'

# Add a label
kubectl label pod nginx-pod team=devops

# Remove a label
kubectl label pod nginx-pod team-
```

---

✅ **Summary**:

* **Labels = tags** for objects.
* **Selectors = queries** that pick objects by labels.
* They decouple resource definitions, making Kubernetes **dynamic and scalable**.

---

👍 — Many people confuse **Selectors** with **NodeSelectors** in Kubernetes. Let’s clearly differentiate them:

---

# 🔹 **1. Label Selectors**

* **Scope**: Work across Kubernetes objects (Pods, Deployments, Services, ReplicaSets, etc.).
* **Purpose**: Select resources **based on their labels**.
* **Usage Examples**:

  * A **Service** selects Pods using labels (`app=nginx`).
  * A **ReplicaSet** manages Pods matching labels.
  * A **NetworkPolicy** applies to Pods with specific labels.

👉 Example: Service selecting Pods by labels

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: nginx        # selects Pods with label app=nginx
  ports:
  - port: 80
    targetPort: 80
```

Here, `selector` = tells Kubernetes which **Pods** this service should forward traffic to.

---

# 🔹 **2. Node Selectors**

* **Scope**: Apply **only to Pod scheduling**.
* **Purpose**: Constrain Pods to **run only on specific Nodes** by matching **Node labels**.
* **Simplest way to schedule Pods on specific nodes**.
* **Limitation**: Very basic; can’t do advanced rules (use **node affinity** for that).

👉 Example: Pod scheduled using `nodeSelector`

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
spec:
  containers:
  - name: nginx
    image: nginx
  nodeSelector:
    disktype: ssd     # pod will only schedule on nodes with label disktype=ssd
```

For this to work, the Node must be labeled:

```bash
kubectl label node worker-node-1 disktype=ssd
```

---

# 🔹 **Key Differences: Selector vs NodeSelector**

| Feature              | Label Selector                                                          | Node Selector                             |
| -------------------- | ----------------------------------------------------------------------- | ----------------------------------------- |
| **Scope**            | Works across all Kubernetes objects (Pods, Services, Deployments, etc.) | Works only at **Pod scheduling level**    |
| **Matches**          | Labels on **resources** (like Pods)                                     | Labels on **Nodes**                       |
| **Use case**         | Service discovery, grouping, scaling, networking                        | Controlling **where Pods run**            |
| **Example**          | Service selecting Pods with `app=nginx`                                 | Pod scheduled to Node with `disktype=ssd` |
| **Advanced options** | Yes (e.g., matchExpressions)                                            | No (use NodeAffinity for advanced rules)  |

---

✅ **In simple terms**:

* **Selectors** = connect Kubernetes objects (e.g., Services → Pods).
* **NodeSelector** = control where Pods run (Pods → Nodes).

---





