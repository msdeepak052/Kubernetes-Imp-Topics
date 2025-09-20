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

> If you just write `my-app` inside the **same namespace**, Kubernetes resolves it automatically.

> If you’re in a **different namespace**, you must use the FQDN.

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

---

### Communication Within the Cluster: Pod IPs

Yes, the Pod IP is the fundamental, routable address on the cluster's network. From anywhere that can route to the cluster's Pod Network (CNI), you can use a Pod IP to communicate directly with that pod.

| Source of Communication | Can it use a Pod IP? | Explanation |
| :--- | :--- | :--- |
| **Inside a Pod** (e.g., via `kubectl exec`) | ✅ **Yes** | The pod has a network interface on the cluster's CNI. It can directly route to any other Pod IP. |
| **On a Cluster Node** (e.g., SSH'd into a worker node) | ✅ **Yes** | The node's operating system has a network interface (like `cni0` or flannel agent) that is part of the pod network. It can directly route to any Pod IP. |
| **The Kubernetes Control Plane** (e.g., on the master node) | ✅ **Yes** | The master nodes are also configured to be part of the cluster network and can route to Pod IPs. |

---

### Practical Example & Verification

Let's assume we have two pods:
*   **Pod A:** IP `10.244.1.10`, running an NGINX web server.
*   **Pod B:** IP `10.244.2.15`, running a curl utility.

#### 1. From Inside Another Pod (Pod B)

This is the most common way to test and is guaranteed to work.

```bash
# Get a shell to Pod B
kubectl exec -it pod-b -- /bin/sh

# Now inside Pod B's container, curl Pod A's IP directly
curl http://10.244.1.10
```
**This will work.** The network namespace of Pod B is connected to the cluster's pod network.

#### 2. From a Cluster Node (Outside any container)

This is what you meant by "outside the pod but inside the cluster".

```bash
# 1. SSH into one of your Kubernetes worker nodes
ssh user@worker-node-ip

# 2. On the node itself, ensure you have curl installed.
# You can now curl the Pod IP directly from the node's OS.
curl http://10.244.1.10
```
**This will also work.** The node's networking is configured by the CNI plugin (like Flannel, Calico, etc.) to be able to route to all pods on all nodes.

#### Why is this useful?
This technique is very handy for cluster administrators and for debugging deep networking issues. If you can reach a pod from a node but not from another pod, it helps you isolate the problem to specific network policies, service configurations, or pod security contexts.

---

### Key Difference: Pod IP vs. Service IP/FQDN

The crucial point your question highlights is the difference between the **ephemeral Pod IP** and the **stable Service IP/DNS**.

*   **Pod IP (10.244.1.10):**
    *   **Direct & Ephemeral:** It's the actual endpoint. It changes every time the pod is recreated (e.g., during a rollout, if it crashes).
    *   **Universal:** Can be used from *anywhere on the cluster network* (pods, nodes).
    *   **Unreliable for Configuration:** You should almost never hardcode a Pod IP into an application because it will break.

*   **Service (ClusterIP) & FQDN (`my-svc.my-ns.svc.cluster.local`):**
    *   **Stable Abstraction:** The Service provides a permanent virtual IP (VIP) and DNS name that never changes. Traffic sent to the Service IP is automatically load-balanced to the current set of healthy pod IPs behind it.
    *   **Namespace-Aware:** The DNS resolution for short names (`my-svc`) only works within the same namespace. For cross-namespace communication, you must use the full FQDN.
    *   **Primary Method:** This is the **correct and recommended way** for pods to discover and communicate with each other. It's resilient to pod restarts and scaling events.

### Conclusion

The Pod IP is the lowest-level network address, and it is reachable from any context **inside the cluster's network boundary**, which includes:
1.  Other Pods
2.  Cluster Nodes (masters and workers)
3.  The control plane components

The FQDN and Service IP are higher-level abstractions built on top of this network to provide stability and easy service discovery, and they are primarily used by applications *running inside pods*.

Excellent! Let's build a practical example with two pods in **different namespaces** and use all possible ways to communicate, including the FQDN.

### Scenario Setup

1.  **Namespace:** `web`
    *   **Pod A:** `nginx-pod` | IP: `10.244.1.10`
    *   **Service A:** `nginx-service`

2.  **Namespace:** `utils`
    *   **Pod B:** `curl-pod` | IP: `10.244.2.15`

---

## Step 1: Create the Namespaces and Resources

**1. Create the namespaces:**
```bash
kubectl create namespace web
kubectl create namespace utils
```

**2. Create Pod A and its Service in the `web` namespace:**
```yaml
# nginx-pod-and-service.yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  namespace: web
  labels:
    app: nginx
spec:
  containers:
  - name: nginx-container
    image: nginx:alpine
    ports:
    - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
  namespace: web
spec:
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
```
Apply it: `kubectl apply -f nginx-pod-and-service.yaml`

**3. Create Pod B in the `utils` namespace:**
```yaml
# curl-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: curl-pod
  namespace: utils
spec:
  containers:
  - name: curl-container
    image: curlimages/curl:latest
    command: ["sleep", "infinity"] # Just keep the pod running
```
Apply it: `kubectl apply -f curl-pod.yaml`

---

## Step 2: Verification - Let's Test Communication

First, let's find the actual IPs and the ClusterIP of the service.

```bash
# Get the IP of nginx-pod
kubectl get pod -n web nginx-pod -o wide
# NAME        READY   STATUS    IP            NODE
# nginx-pod   1/1     Running   10.244.1.10   node-01

# Get the ClusterIP of nginx-service
kubectl get service -n web nginx-service
# NAME            TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
# nginx-service   ClusterIP   10.109.156.42   <none>        80/TCP    5m
```

Now, let's execute commands **inside `curl-pod`** (`utils` namespace) to test connectivity.

### Test 1: Communicate using Pod IP (Direct)

```bash
# Exec into the curl-pod
kubectl exec -n utils -it curl-pod -- /bin/sh

# Now inside the curl-pod container, try to curl the NGINX pod using its IP
curl -v http://10.244.1.10
```
**Expected Result:** `200 OK` (Success!). This proves direct pod-to-pod IP communication across namespaces works.

### Test 2: Communicate using Service ClusterIP

```bash
# From inside the curl-pod container, curl the Service's ClusterIP
curl -v http://10.109.156.42
```
**Expected Result:** `200 OK` (Success!). The service correctly load-balances to the pod.

### Test 3: Communicate using FQDN (The Key Test)

This is the most important test for service discovery.

```bash
# From inside the curl-pod container, curl using the FULL FQDN
curl -v http://nginx-service.web.svc.cluster.local

# You can also try just the FQDN without the port (since it's http on port 80)
curl http://nginx-service.web.svc.cluster.local
```
**Expected Result:** `200 OK` (Success!). The internal Kubernetes DNS (`CoreDNS`) successfully resolved the FQDN to the Service's ClusterIP.

### Test 4: Test DNS Shortname Resolution (Will Fail)

```bash
# Try using just the service name. This should FAIL.
curl -v http://nginx-service
```
**Expected Result:** **`Could not resolve host: nginx-service`**
**Why?** Because the `curl-pod` is in the `utils` namespace. The short name `nginx-service` is only resolvable within the same namespace (`web`). For cross-namespace communication, you **must** use the full FQDN.

### Test 5: Test Shortname from the same namespace (For Completeness)

Let's see what would happen if a pod *in the same namespace* tried the short name.

```bash
# Run a temporary curl pod in the SAME namespace ('web') as the service
kubectl run test-curl -n web --image=curlimages/curl --rm -it --command -- /bin/sh

# Now from inside this new pod in the 'web' namespace
curl http://nginx-service # Just the service name!
```
**Expected Result:** `200 OK` (Success!). From within the same namespace, the short name resolves correctly.

---

## Summary of Tests from `curl-pod` (utils namespace)

| Target | Command | Works? | Reason |
| :--- | :--- | :--- | :--- |
| **Pod IP** | `curl http://10.244.1.10` | ✅ Yes | Direct network routing on the pod network. |
| **Service IP** | `curl http://10.109.156.42` | ✅ Yes | Directly accessing the stable Service VIP. |
| **FQDN** | `curl http://nginx-service.web.svc.cluster.local` | ✅ Yes | Internal DNS resolves the full name to the Service IP. |
| **Short Name** | `curl http://nginx-service` | ❌ No | The pod is in a different namespace (`utils` vs `web`). |

This practical exercise demonstrates exactly why the FQDN is needed: it provides a **stable, discoverable, and namespaced** way for applications to find each other, without needing to hardcode unreliable Pod IPs or even Service IPs. The application only needs to know the name of the service and its namespace.

---

Here’s the detailed breakdown of why:

---

### 1. The Crucial Difference: Pod vs. Service

This is the most important concept to understand.

*   **Services get DNS names.** The Kubernetes DNS system (`CoreDNS`) automatically creates DNS records for **Services**. This is why you can use `nginx-service.web.svc.cluster.local`.
*   **Pods do *not* get stable DNS names by default.** A Pod's IP is ephemeral. When it dies and is recreated, it gets a new IP. Kubernetes does not automatically assign a stable DNS name for every pod because it would be a messy and constantly changing list.

There is an exception called a **Headless Service** (`clusterIP: None`), which can create DNS records for *individual pods*, but this is an advanced, explicit setup and not the default behavior.

**In our example, `nginx-pod` *does not* have an FQDN like `nginx-pod.web.pod.cluster.local` (unless specifically configured that way).**

---

### 2. How DNS Resolution Works in Kubernetes

The Kubernetes DNS resolver (`CoreDNS`) runs **as a pod in the `kube-system` namespace**. Its sole job is to answer DNS queries **from other pods**.

*   When a process *inside a pod* makes a DNS query, its `/etc/resolv.conf` file is configured to point to the `CoreDNS` service IP.
*   The `CoreDNS` pod then checks if the query is for a Kubernetes service (`*.svc.cluster.local`) or pod and returns the appropriate answer.

**A cluster node (or the master) does NOT have its `/etc/resolv.conf` configured to use the Kubernetes `CoreDNS` service for resolution.** It uses the system's default DNS resolver (e.g., `8.8.8.8`, `1.1.1.1`, or a corporate DNS server), which has no knowledge of the internal `cluster.local` domain.

---

### Practical Verification

Let's use our previous example with:
*   **Node IP:** `192.168.1.100`
*   **Service FQDN:** `nginx-service.web.svc.cluster.local`
*   **Service ClusterIP:** `10.109.156.42`
*   **Pod IP:** `10.244.1.10`

#### Test 1: From a Cluster Node (SSH into it)

```bash
# 1. SSH into the worker node
ssh user@192.168.1.100

# 2. Try to ping the FQDN. This will FAIL.
ping nginx-service.web.svc.cluster.local
# ping: nginx-service.web.svc.cluster.local: Name or service not known

# 3. Try to resolve the FQDN using the system's DNS tools. This will FAIL.
nslookup nginx-service.web.svc.cluster.local
# Server:         8.8.8.8
# Address:        8.8.8.8#53
# ** server can't find nginx-service.web.svc.cluster.local: NXDOMAIN

# 4. But you CAN still ping/curl the Pod IP and Service IP directly!
ping -c 4 10.244.1.10   # This will work (if ICMP is allowed)
curl -v http://10.244.1.10 # This will work

# You can also curl the Service's ClusterIP
curl -v http://10.109.156.42 # This will also work
```

#### Test 2: From a Master Node

The result will be identical to the worker node. The master node is also not configured to use the cluster's internal DNS for its own system queries.

#### Test 3: Forcing DNS Resolution (Advanced)

You could *temporarily* test DNS resolution by manually pointing to the `CoreDNS` Service IP from the node.

```bash
# First, find the CoreDNS service IP
kubectl get service -n kube-system | grep dns
# kube-dns   ClusterIP   10.96.0.10   <none>        53/UDP,53/TCP

# Now, on the node, use nslookup and manually specify the CoreDNS IP
nslookup nginx-service.web.svc.cluster.local 10.96.0.10
# Server:   10.96.0.10
# Address:  10.96.0.10#53
#
# Name: nginx-service.web.svc.cluster.local
# Address: 10.109.156.42  <-- SUCCESS! But this is a manual test.
```
This proves the DNS record exists, but you had to explicitly ask the Kubernetes DNS server. The node's operating system doesn't do this automatically.

---

### Summary: Communication Methods from a Cluster Node

| Target | Method | Works from a Node? | Why / Why Not? |
| :--- | :--- | :--- | :--- |
| **Another Pod** | **Pod IP** (`10.244.1.10`) | ✅ **Yes** | The node is on the cluster network and can route to the pod network directly. |
| **A Service** | **Service IP** (`10.109.156.42`) | ✅ **Yes** | The node can route to the Service's virtual IP, which is implemented by `kube-proxy`. |
| **A Service** | **FQDN** (`nginx-service.web.svc.cluster.local`) | ❌ **No** | The node's DNS resolver is not configured to query the Kubernetes DNS server (`CoreDNS`). |
| **A Pod** | **FQDN** | ❌ **No** | Pods don't get automatic DNS names, and even if they did, the node couldn't resolve the `cluster.local` domain. |

**Conclusion:** From outside a pod but within the cluster (nodes, master), you must use **IP addresses** (Pod IP or Service ClusterIP) for communication. The FQDN is a convenience feature **exclusively for processes running inside pods**, enabled by the pod's specially configured `resolv.conf`.
