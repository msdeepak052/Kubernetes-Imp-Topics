# **Kubernetes Services**
---

## 1. What is a Service in Kubernetes?

* A **Service** in Kubernetes is an abstraction that defines a logical set of Pods and a policy by which to access them.
* Pods are **ephemeral** (IP changes if they restart), so Services provide a **stable IP** and **DNS name**.
* Services route traffic to the backend Pods using **selectors**.

---

## 2. Types of Services in Kubernetes

There are mainly **4 types**:

<img width="3000" height="3900" alt="image" src="https://github.com/user-attachments/assets/a62afa06-309b-48f1-a631-db27f0fb2035" />


### (A) **ClusterIP** (default)

* Exposes the Service **inside the cluster only**.
* Gets a **virtual IP** accessible only within the cluster.
* Useful for **internal communication** between microservices.

#### Example YAML (ClusterIP)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-clusterip
  namespace: test-ns
spec:
  selector:
    app: my-app   # Labels of target pods
  ports:
    - protocol: TCP
      port: 80        # Service port (clients use this)
      targetPort: 8080  # Pod's containerPort
  type: ClusterIP
```

🔑 **Important Terms**:

* **selector** → Which Pods this service points to.
* **port** → Port exposed by the Service.
* **targetPort** → Pod container port.
* **type: ClusterIP** → Defines service as internal.

---

### (B) **NodePort**

* Exposes the Service **on each Node’s IP** at a static **port (30000–32767)**.
* Accessible from **outside the cluster** using `<NodeIP>:<NodePort>`.
* Used mainly for **testing/dev**.

#### Example YAML (NodePort)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-nodeport
spec:
  selector:
    app: my-app
  ports:
    - protocol: TCP
      port: 80          # Service port
      targetPort: 8080  # Pod container port
      nodePort: 30080   # Fixed port on Node
  type: NodePort
```

🔑 **Important Terms**:

* **nodePort** → Exposes on all worker node IPs.
* **range** → 30000–32767 (default).
* Still **creates a ClusterIP internally**.

---

### (C) **LoadBalancer**

* Exposes the Service **externally using cloud provider’s LoadBalancer** (AWS ELB, Azure LB, GCP LB).
* Ideal for **production apps**.
* Each service gets a **public IP/DNS**.

#### Example YAML (LoadBalancer)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-loadbalancer
spec:
  selector:
    app: my-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer
```

🔑 **Important Terms**:

* **type: LoadBalancer** → Tells cloud provider to provision an LB.
* **external IP/DNS** assigned.
* Works **only on cloud platforms** with LB integrations.

---

### (D) **ExternalName**

* Maps the Service to an **external DNS name** (like `mydb.example.com`).
* Does not use selectors or create endpoints.
* Used when you want in-cluster apps to access an **external service** via a consistent DNS name.

#### Example YAML (ExternalName)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-external-service
spec:
  type: ExternalName
  externalName: mydb.example.com
  ports:
    - port: 3306
```

🔑 **Important Terms**:

* **externalName** → DNS name of external service.
* Works like a **CNAME record**.
* No Pods/endpoints involved.

---

## 3. Summary Table

| Service Type     | Scope         | Accessible From             | Example Use Case                            |
| ---------------- | ------------- | --------------------------- | ------------------------------------------- |
| **ClusterIP**    | Internal      | Inside cluster only         | Communication between microservices         |
| **NodePort**     | Semi-external | NodeIP\:NodePort            | Simple external access, dev/test            |
| **LoadBalancer** | External      | Internet via LB             | Production apps exposed to users            |
| **ExternalName** | External DNS  | Maps DNS → external service | Use external DB/Service from inside cluster |

---

✅ That covers **Services, Types, YAMLs, and important terms**.

#### **Kubernetes Service discussion** into **Session Persistence** (also called **Session Affinity**).

---

## 🔹 What is Session Persistence?

* Normally, a Kubernetes Service **load balances traffic randomly (round-robin)** across backend Pods.
* Sometimes, applications (like legacy apps, shopping carts, or banking apps) need a client to always talk to the **same Pod** for the duration of a session.
* This behavior is called **Session Persistence / Affinity / Sticky Sessions**.

---

## 🔹 Types of Session Affinity in Kubernetes

### 1. **ClientIP (Most Common)**

* Based on the **client’s IP address**.
* A client with a given IP always gets routed to the **same Pod** (as long as the Pod is alive).

#### Example YAML (ClusterIP with Session Affinity)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-clusterip
spec:
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 8080
  type: ClusterIP
  sessionAffinity: ClientIP   # <--- Sticky session
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800   # Optional (default: 10800 = 3 hours)
```

🔑 **Important Terms**:

* **sessionAffinity: ClientIP** → enables sticky sessions.
* **timeoutSeconds** → how long a session remains sticky (default = 3 hours).

---

### 2. **None (Default)**

* No stickiness. Traffic is load-balanced **randomly** to any available Pod.
* This is the default if you don’t set `sessionAffinity`.

```yaml
sessionAffinity: None
```

---

### 3. **Cookie-based (Ingress Controllers / Service Mesh)**

* Not native to Kubernetes `Service`, but many **Ingress controllers (NGINX, Traefik, Istio)** support **sticky sessions with cookies**.
* Example: NGINX Ingress can add a cookie like `NGINX_STICKY=pod-id`, so the client always lands on the same Pod.

---

## 🔹 When to Use Session Persistence?

✅ Good for:

* Shopping carts (before data is persisted in DB)
* Legacy apps that store session in **memory** instead of DB/Redis
* Stateful workloads without external session management

⚠️ Not recommended for:

* **Stateless applications** (modern microservices should store session state in DB/Redis, not Pod memory)
* **High availability systems** (if Pod dies, session is lost)

---

## 🔹 Quick Summary

* **Default**: `sessionAffinity: None` → load-balanced randomly.
* **Sticky**: `sessionAffinity: ClientIP` → same client IP → same Pod.
* **Advanced**: Cookie-based → supported via Ingress controllers, not Service.

---

 #### **How Kubernetes Services distribute traffic across Pods** 

---

## 🔹 How Requests Are Sent to Pods (Default Behavior)

Kubernetes Services use **kube-proxy** to handle traffic routing:

* kube-proxy programs **iptables** or **IPVS** rules in the Node OS.
* When a client hits a **Service IP (ClusterIP, NodePort, LoadBalancer)**, kube-proxy picks one of the Pods behind the Service.
* By default, traffic is sent in a **round-robin fashion** (or near-random, depending on proxy mode).

---

## 🔹 kube-proxy Modes and Load Balancing

### 1. **iptables mode** (default in most clusters)

* Packets are routed using **NAT rules** in iptables.
* **Selection is random** (not strict round robin).
* Lightweight and scales well.

### 2. **IPVS mode** (recommended for large clusters)

* Uses **Linux IPVS (IP Virtual Server)** for load balancing.
* Supports **multiple algorithms**:

  * `rr` → round robin
  * `lc` → least connection
  * `dh` → destination hashing
  * `sh` → source hashing
  * `sed` → shortest expected delay
  * `nq` → never queue

👉 With IPVS you can actually configure **load-balancing strategies**.

---

## 🔹 Can We Configure Load Balancing in Service YAML?

* **Service YAML itself doesn’t let you choose round robin vs least connection**.
* By default:

  * In `iptables` mode → random (approx. round robin).
  * In `ipvs` mode → round robin (but configurable with kube-proxy flags).

⚡ Example: If cluster is running in **IPVS mode**, you can check the scheduler with:

```bash
kubectl get configmap kube-proxy -n kube-system -o yaml
```

And look for:

```yaml
mode: "ipvs"
ipvs:
  scheduler: "rr"
```

You could change `scheduler` to `lc` (least connection), `sh` (source hashing), etc., then restart kube-proxy.

---

## 🔹 Traffic Flow Example

1. **Client → Service IP (ClusterIP, NodePort, LB)**
2. kube-proxy intercepts request
3. Chooses Pod according to load-balancing strategy:

   * iptables → random Pod each time
   * ipvs (`rr`) → Pod1 → Pod2 → Pod3 → Pod1 …
   * ipvs (`lc`) → Pod with least active connections

---

## 🔹 Special Case: Session Affinity

If you enable `sessionAffinity: ClientIP`, load balancing is **overridden**:

* Same client IP always goes to the **same Pod** (until timeout).

---

✅ **Summary Table**

| Proxy Mode           | Default Behavior              | Configurable?                  |
| -------------------- | ----------------------------- | ------------------------------ |
| iptables             | Random (close to round robin) | ❌ No                           |
| ipvs                 | Round robin (default)         | ✅ Yes (`rr`, `lc`, `sh`, etc.) |
| With SessionAffinity | Same Pod per client           | ✅ Yes (via `sessionAffinity`)  |

---

 ## **Handy list of important Service-related commands** 

---

## 🔹 Basic Service Commands

### 1. List Services

```bash
kubectl get svc
kubectl get svc -n test-ns
```

👉 Lists all Services in the default or specific namespace.

---

### 2. Detailed Service Information

```bash
kubectl describe svc my-service
```

👉 Shows selector, ports, sessionAffinity, endpoints (important for debugging).

---

### 3. Show Endpoints of a Service

```bash
kubectl get endpoints my-service
kubectl describe endpoints my-service
```

👉 Confirms which Pods are backing the Service. If `ENDPOINTS` is empty → Service selector mismatch.

---

### 4. Get Service in YAML Format

```bash
kubectl get svc my-service -o yaml
```

👉 Useful for checking `sessionAffinity`, `ClusterIP`, annotations, etc.

---

### 5. Expose a Deployment as a Service

```bash
kubectl expose deployment my-app --name=my-service --port=80 --target-port=8080 --type=ClusterIP
```

👉 Quick way to create a Service without writing YAML.

---

## 🔹 Service Testing Commands

### 6. Access Service Inside the Cluster

```bash
kubectl run test-pod --rm -it --image=busybox:1.28 -- sh
# Inside pod shell:
wget -O- http://my-service:80
```

👉 Validates DNS & connectivity to Service.

---

### 7. Access Service Outside the Cluster

* **NodePort**

```bash
curl http://<NodeIP>:<NodePort>
```

* **LoadBalancer**

```bash
kubectl get svc my-service
# Copy EXTERNAL-IP
curl http://<External-IP>:80
```

---

### 8. Port Forwarding (Useful for Local Debugging)

```bash
kubectl port-forward svc/my-service 8080:80
```

👉 Maps Service port 80 to localhost:8080.

---

## 🔹 Advanced / Troubleshooting Commands

### 9. Check Cluster DNS for Service

```bash
kubectl exec -it <pod-name> -- nslookup my-service
kubectl exec -it <pod-name> -- nslookup my-service.test-ns.svc.cluster.local
```

👉 Verifies Service DNS resolution.

---

### 10. Delete a Service

```bash
kubectl delete svc my-service
```

---

### 11. Debug Service Traffic Flow

```bash
kubectl get endpoints my-service
kubectl logs <pod-name>
```

👉 Ensures traffic is hitting correct Pods.

---

### 12. Show All Services in All Namespaces

```bash
kubectl get svc -A
```

---

### 13. Debug NodePort Range (30000–32767)

```bash
kubectl get svc my-service -o wide
```

👉 Shows which NodePort is allocated.

---

### 14. Verify Session Affinity

```bash
kubectl describe svc my-service | grep -i sessionAffinity
```

---

✅ **Quick Reference for Interview/Hands-on**

* `kubectl get svc` → list services
* `kubectl describe svc <name>` → details & endpoints
* `kubectl get endpoints <svc>` → backend Pods
* `kubectl expose` → create Service quickly
* `kubectl port-forward` → test locally
* `kubectl exec` + `nslookup` → DNS debugging

---

> Here’s a **one-page Kubernetes Services Cheat Sheet** with the most important commands, grouped logically for **creation, testing, and debugging**.

---

# 🚀 Kubernetes Services – One Page Cheat Sheet

## 🔹 Create & Manage Services

```bash
# List Services in current namespace
kubectl get svc

# List Services in all namespaces
kubectl get svc -A

# Create Service from Deployment
kubectl expose deployment my-app \
  --name=my-service --port=80 --target-port=8080 --type=ClusterIP

# Get Service details in YAML
kubectl get svc my-service -o yaml

# Delete a Service
kubectl delete svc my-service
```

---

## 🔹 Inspect Services

```bash
# Describe a Service (selectors, ports, sessionAffinity)
kubectl describe svc my-service

# Show Endpoints (Pods backing the Service)
kubectl get endpoints my-service
kubectl describe endpoints my-service

# Show Service with NodePort/ClusterIP info
kubectl get svc my-service -o wide
```

---

## 🔹 Test Connectivity

```bash
# Run a temporary Pod to test Service from inside cluster
kubectl run test-pod --rm -it --image=busybox:1.28 -- sh
wget -O- http://my-service:80

# Test DNS resolution
kubectl exec -it <pod> -- nslookup my-service
kubectl exec -it <pod> -- nslookup my-service.test-ns.svc.cluster.local

# Port-forward Service to local machine
kubectl port-forward svc/my-service 8080:80

# Access NodePort Service from outside
curl http://<NodeIP>:<NodePort>

# Access LoadBalancer Service from outside
kubectl get svc my-service
curl http://<External-IP>:80
```

---

## 🔹 Session Affinity

```bash
# Check sessionAffinity setting
kubectl describe svc my-service | grep -i sessionAffinity
```

---

✅ **Pro Tips**

* **ClusterIP** → internal only
* **NodePort** → `<NodeIP>:<NodePort>`
* **LoadBalancer** → Cloud external IP
* **ExternalName** → DNS alias
* **Endpoints empty?** → Service selector mismatch

---










