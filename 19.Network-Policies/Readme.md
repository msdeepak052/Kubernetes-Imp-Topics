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
minikube start --cni=calico
```

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

---

## 🧩 6. Test the Policy

✅ Frontend → Backend (allowed)

```bash
kubectl exec -n netpol-demo frontend -- curl -s backend
```

👉 Should work.

❌ Another Pod → Backend (blocked)

```bash
kubectl run attacker -n netpol-demo --image=curlimages/curl -it -- sh
# Inside pod:
curl backend
```

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
