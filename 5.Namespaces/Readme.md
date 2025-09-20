# Namespaces in Kubernetes

## What are Namespaces?

Namespaces in Kubernetes are virtual clusters that provide a way to divide cluster resources between multiple users, teams, or applications. They create logical isolation within a single physical cluster, allowing different groups to work independently without interfering with each other.

## Why Use Namespaces?

1. **Resource Isolation**: Prevent naming conflicts between different teams/projects
2. **Access Control**: Apply RBAC policies to specific namespaces
3. **Resource Quotas**: Limit resource consumption per namespace
4. **Organization**: Group related resources together
5. **Environment Separation**: Create dev, staging, and prod environments in the same cluster

# 🔹 Default Namespaces

Kubernetes comes with some built-in namespaces:

* `default` → Where resources are created if no namespace is specified.
* `kube-system` → For cluster system components (kube-dns, kube-proxy, etc.).
* `kube-public` → Public resources, readable by all users.
* `kube-node-lease` → Tracks node heartbeats.

## Creating Namespaces

### 1. Imperative Method (using kubectl)

```bash
# Create a namespace
kubectl create namespace my-app

# Create namespace with labels
kubectl create namespace my-app --dry-run=client -o yaml | kubectl apply -f -

# Verify namespace creation
kubectl get namespaces
```

### 2. Declarative Method (using YAML)

Create a file `my-namespace.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: my-app
  labels:
    environment: development
    team: backend
```

Apply the YAML file:
```bash
kubectl apply -f my-namespace.yaml
```

### 3. Viewing and Managing Namespaces

```bash
# Create a Pod in a Namespace (Imperative)

kubectl run nginx --image=nginx -n dev
```



```bash
# Get resources from a Namespace

kubectl get pods -n dev
kubectl get svc -n dev
```
```bash
# List all namespaces
kubectl get namespaces
kubectl get ns

# Describe a specific namespace
kubectl describe namespace my-app

# Set default namespace for current context
kubectl config set-context --current --namespace=my-app

# View resources in a specific namespace
kubectl get pods -n my-app
```

## Namespaces and FQDN (Fully Qualified Domain Name)

### How Namespaces Form FQDNs

In Kubernetes, services within the same namespace can communicate using just the service name. However, for cross-namespace communication, you need to use the FQDN.

The FQDN format for Kubernetes services is:
```
<service-name>.<namespace-name>.svc.cluster.local
```

### Why FQDN is Needed

1. **Cross-Namespace Communication**: Allows services in different namespaces to discover and communicate with each other
2. **DNS Resolution**: Kubernetes DNS automatically resolves these FQDNs to the correct service IP
3. **Explicit Routing**: Ensures traffic goes to the correct service in the correct namespace

### Examples

**Within the same namespace:**
```yaml
# Service in namespace "frontend"
apiVersion: v1
kind: Service
metadata:
  name: web-service
  namespace: frontend
```

A pod in the `frontend` namespace can access this service using:
- `web-service` (short name)
- `web-service.frontend.svc.cluster.local` (FQDN)

**Cross-namespace communication:**
```yaml
# Service in namespace "backend"
apiVersion: v1
kind: Service
metadata:
  name: api-service
  namespace: backend
```

A pod in the `frontend` namespace must use the FQDN to access this service:
- `api-service.backend.svc.cluster.local`

## Practical Examples

### Example 1: Multi-tier Application

```yaml
# frontend-namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: frontend
  labels:
    tier: frontend
---
# backend-namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: backend
  labels:
    tier: backend
---
# database-namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: database
  labels:
    tier: database
```

### Example 2: Service Communication

Frontend service (in frontend namespace) connecting to backend API:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend-app
  namespace: frontend
spec:
  template:
    spec:
      containers:
      - name: frontend
        image: nginx
        env:
        - name: API_URL
          value: "http://api-service.backend.svc.cluster.local:8080"
```

### Example 3: Resource Quotas per Namespace

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: dev-quota
  namespace: development
spec:
  hard:
    requests.cpu: "2"
    requests.memory: 2Gi
    limits.cpu: "4"
    limits.memory: 4Gi
    pods: "10"
```

If you just write `my-app` inside the **same namespace**, Kubernetes resolves it automatically.
If you’re in a **different namespace**, you must use the FQDN.

## Best Practices

1. **Use meaningful names**: `dev`, `staging`, `production`, `team-a`, etc.
2. **Apply RBAC**: Restrict access to namespaces based on teams
3. **Use resource quotas**: Prevent one namespace from consuming all cluster resources
4. **Default namespace**: Avoid using the `default` namespace for production workloads
5. **Namespace-scoped resources**: Most resources are namespace-scoped, but some (like Nodes, PersistentVolumes) are cluster-scoped

## Default Namespaces

Kubernetes comes with several built-in namespaces:
- `default`: Where resources are created if no namespace is specified
- `kube-system`: For system components (not for user applications)
- `kube-public**: Readable by all users (for public cluster information)
- `kube-node-lease`: For node lease objects (heartbeats)

Namespaces are essential for managing complex Kubernetes environments, enabling better organization, security, and resource management across multiple teams and applications.
