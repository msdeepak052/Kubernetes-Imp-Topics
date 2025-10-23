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
kubectl label nodes node1 disktype=ssd environment=production zone=zone-a
kubectl label nodes node2 disktype=hdd environment=staging zone=zone-b
kubectl label nodes node3 disktype=ssd environment=development zone=zone-a

# Verify labels
kubectl get nodes --show-labels
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
