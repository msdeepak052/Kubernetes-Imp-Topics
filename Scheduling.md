# **Kubernetes Pod Scheduling: Complete Guide with Examples**  

Pod scheduling in Kubernetes determines **where and how a Pod runs** in a cluster. The **kube-scheduler** assigns Pods to Nodes based on resource requirements, constraints, and policies.  

---

## **1. Default Scheduling (Automated by kube-scheduler)**  
The scheduler selects the best Node based on:  
✅ **Resource requests** (CPU, memory).  
✅ **Node availability** (disk pressure, network readiness).  
✅ **Taints & Tolerations** (whether a Pod can tolerate a Node’s taint).  

### **Example: Basic Pod Scheduling**  
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
spec:
  containers:
  - name: nginx
    image: nginx
    resources:
      requests:
        cpu: "500m"
        memory: "512Mi"
```
- The scheduler picks a **Node with enough CPU and memory**.  

---

## **2. Manual Scheduling (Node Selector)**  
Force a Pod to run on a **specific Node** using labels.  

### **Step 1: Label a Node**  
```sh
kubectl label nodes <node-name> disktype=ssd
```  

### **Step 2: Use `nodeSelector` in Pod Spec**  
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
    disktype: ssd  # Runs only on Nodes with this label
```

---

## **3. Advanced Scheduling (Affinity & Anti-Affinity)**  
Control Pod placement **based on rules** (soft/hard requirements).  

### **a) Node Affinity (Prefer Specific Nodes)**  
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-affinity
spec:
  containers:
  - name: nginx
    image: nginx
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:  # Hard rule
        nodeSelectorTerms:
        - matchExpressions:
          - key: disktype
            operator: In
            values: [ssd]
      preferredDuringSchedulingIgnoredDuringExecution:  # Soft rule
      - weight: 1
        preference:
          matchExpressions:
          - key: zone
            operator: In
            values: [us-east-1a]
```
- **Hard rule (`requiredDuringScheduling`)** → Must run on `disktype=ssd`.  
- **Soft rule (`preferredDuringScheduling`)** → Prefers `zone=us-east-1a`.  

### **b) Pod Anti-Affinity (Avoid Co-Location)**  
```yaml
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector:
        matchExpressions:
        - key: app
          operator: In
          values: [redis]
      topologyKey: kubernetes.io/hostname  # Avoid same Node
```
- Ensures **no two `app=redis` Pods run on the same Node**.  

---

## **4. Taints & Tolerations (Restrict Pods from Nodes)**  
- **Taints** repel Pods unless they have a matching **toleration**.  
- Useful for **dedicated Nodes** (e.g., GPU nodes).  

### **Step 1: Taint a Node**  
```sh
kubectl taint nodes <node-name> gpu=true:NoSchedule
```  

### **Step 2: Add Toleration in Pod Spec**  
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: gpu-pod
spec:
  containers:
  - name: cuda-container
    image: nvidia/cuda
  tolerations:
  - key: "gpu"
    operator: "Equal"
    value: "true"
    effect: "NoSchedule"
```
- Only Pods with this toleration can run on the tainted Node.  

---

## **5. Pod Topology Spread Constraints (Even Distribution)**  
Spread Pods across **zones, hosts, or regions** for high availability.  

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-spread
spec:
  containers:
  - name: nginx
    image: nginx
  topologySpreadConstraints:
  - maxSkew: 1  # Max allowed imbalance
    topologyKey: zone  # Spread across zones
    whenUnsatisfiable: DoNotSchedule  # Hard requirement
    labelSelector:
      matchLabels:
        app: nginx
```
- Ensures **equal distribution of `app=nginx` Pods across zones**.  

---

## **6. Manual Scheduling (Static Pods & `nodeName`)**  
### **a) Using `nodeName` (Bypass Scheduler)**  
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-manual
spec:
  nodeName: worker-node-1  # Runs explicitly on this Node
  containers:
  - name: nginx
    image: nginx
```  

### **b) Static Pods (Managed by kubelet)**  
- Defined in `/etc/kubernetes/manifests/` on a Node.  
- Example: `nginx.yaml` placed in the manifests directory.  

---

## **Summary: Pod Scheduling Options**  
| Method | Use Case | Example |
|--------|----------|---------|
| **Default Scheduling** | Automatic placement | Pod with `resources.requests` |
| **Node Selector** | Simple node targeting | `nodeSelector: disktype=ssd` |
| **Node Affinity** | Advanced node rules | `affinity.nodeAffinity` |
| **Pod Anti-Affinity** | Avoid co-location | `podAntiAffinity` |
| **Taints & Tolerations** | Dedicated nodes | `tolerations` for `gpu=true` |
| **Topology Spread** | HA across zones | `topologySpreadConstraints` |
| **Manual (`nodeName`)** | Force a Node | `nodeName: worker-node-1` |

---

### **When to Use Which?**  
- **Default**: Most cases (let Kubernetes decide).  
- **Node Selector/Affinity**: When Pods need specific hardware (SSD, GPU).  
- **Anti-Affinity**: For HA (avoid single-point failures).  
- **Taints/Tolerations**: For reserved Nodes (e.g., only monitoring Pods).  
- **Topology Spread**: For multi-zone deployments.  

Would you like a deep dive into **scheduler configuration** or **custom schedulers**?
