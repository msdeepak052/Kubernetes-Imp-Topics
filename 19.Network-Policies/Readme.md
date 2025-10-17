# Kubernetes Network Policies

## 🧠 1. What is a Network Policy?

By default — **all Pods can communicate with all other Pods** in a Kubernetes cluster.

A **NetworkPolicy** acts like a firewall for Pods — it defines **which traffic is allowed** (Ingress or Egress).

Think of it as:

> “Which Pods are allowed to talk to me — and which destinations I can talk to?”

---

## ⚙️ 2. Prerequisites

✅ Your cluster must use a **CNI plugin** that supports network policies.
For example:

* Calico ✅
* Cilium ✅
* Weave Net ✅
* AWS VPC CNI ❌ (by default, doesn’t support policies; Calico can be added for that)
* kindnet (kind or minikube by default uses kindnet) ❌

<img width="1317" height="825" alt="image" src="https://github.com/user-attachments/assets/f0f32b0f-1a7b-4a7a-85e5-287026165021" />


If you’re using **Minikube**, enable Calico:

```bash
minikube delete  # optional clean start

minikube start --nodes 2 --cpus 4 --memory 8192 --driver=docker --cni=calico
```
<img width="1064" height="375" alt="image" src="https://github.com/user-attachments/assets/bed73eb5-5700-465d-a9fb-496219442163" />

---

## 🚀 3. Create a Demo Namespace and Pods

Let’s create a namespace and two apps (`frontend` and `backend`) to test communication.

```bash
kubectl create ns netpol-demo
```

### Deploy Backend Pod

```yaml
# backend.yaml
apiVersion: v1
kind: Pod
metadata:
  name: backend
  namespace: netpol-demo
  labels:
    app: backend
spec:
  containers:
  - name: backend
    image: nginx
    ports:
    - containerPort: 80

---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: netpol-demo
spec:
  selector:
    app: backend
  ports:
  - port: 80
    targetPort: 80
```

### Deploy Frontend Pod

```yaml
# frontend.yaml
apiVersion: v1
kind: Pod
metadata:
  name: frontend
  namespace: netpol-demo
  labels:
    app: frontend
spec:
  containers:
  - name: frontend
    image: curlimages/curl
    command: ["sleep", "3600"]
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: netpol-demo
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 80


```

Apply both:

```bash
kubectl apply -f backend.yaml -f frontend.yaml
```

---

## 🧪 4. Test Communication (Before NetworkPolicy)

```bash
kubectl exec -n netpol-demo frontend -- curl -s backend
```

✅ You’ll see the **HTML output** from Nginx — meaning communication is working.

<img width="1504" height="842" alt="image" src="https://github.com/user-attachments/assets/d2985424-8e98-4d2f-bf41-1f0ebc54c32f" />

---

## 🔒 5. Apply a NetworkPolicy to Restrict Traffic

Now let’s **block all incoming traffic** to the backend — only allow from the frontend Pod.

```yaml
# allow-frontend-to-backend.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend
  namespace: netpol-demo
spec:
  podSelector:
    matchLabels:
      app: backend        # applies policy to backend pods
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend   # only frontend can talk to backend
    ports:
    - protocol: TCP
      port: 80
```

Apply:

```bash
kubectl apply -f allow-frontend-to-backend.yaml
```
<img width="1238" height="79" alt="image" src="https://github.com/user-attachments/assets/0c8a5b11-dd52-484a-9dcf-39729f5997c7" />

---

## 🧩 6. Test the Policy

✅ Frontend → Backend (allowed)

```bash
kubectl exec -n netpol-demo frontend -- curl -s backend
```
<img width="1288" height="584" alt="image" src="https://github.com/user-attachments/assets/e1d5600b-138c-484d-ae39-a1134b10de59" />

👉 Should work.

❌ Another Pod → Backend (blocked)

```bash
kubectl run attacker -n netpol-demo --image=curlimages/curl -it -- sh
# Inside pod:
curl backend
```
<img width="1920" height="261" alt="image" src="https://github.com/user-attachments/assets/27063a3c-d9e2-464a-93ea-77afd70d362c" />

👉 Should **hang or fail** — blocked by the policy.

---

## 🧱 7. Summary

| Direction               | Allowed          | Description                          |
| ----------------------- | ---------------- | ------------------------------------ |
| Frontend → Backend      | ✅                | Allowed by policy                    |
| Any other Pod → Backend | ❌                | Blocked                              |
| Backend → Frontend      | ❌ (default deny) | Not allowed unless Egress is defined |

---

## 🧠 8. Pro Tips

* By default, if **any NetworkPolicy selects a Pod**, then all traffic **not explicitly allowed is denied**.
* You can add **`policyTypes: [Ingress, Egress]`** to control both directions.
* You can filter by **namespaceSelector**, **ipBlock**, or **podSelector**.

---
