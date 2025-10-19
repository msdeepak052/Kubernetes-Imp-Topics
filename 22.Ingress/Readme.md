# Ingress and Ingress Controller

## 🌐 1. What is Ingress and Ingress Controller?

### **Ingress**

An **Ingress** is a Kubernetes object that **manages external access** (usually HTTP/HTTPS) to services within your cluster.

Think of it as a **smart router** that decides:

* Which request goes to which service (based on URL or hostname).
* Can perform SSL termination (HTTPS).
* Can do load balancing.

🧠 **Analogy:**
Imagine your cluster as an apartment building (pods inside).
Ingress is like the **main gate security guard** that decides which visitor goes to which apartment (service).

---

### **Ingress Controller**

The **Ingress Controller** is the **actual program** that implements the routing logic defined in the Ingress resource.
Common controllers:

* **NGINX Ingress Controller (most popular)**
* Traefik
* HAProxy
* AWS ALB Ingress Controller (for EKS)

🧩 **Ingress** = rules
🧠 **Ingress Controller** = engine that enforces those rules

---

## 🧱 2. Example Architecture

```
                     +-----------------------------+
                     |        Internet User        |
                     +--------------+--------------+
                                    |
                                    v
                     +-----------------------------+
                     |   NGINX Ingress Controller  |   <-- Single Entry Point
                     +--------------+--------------+
                                    |
               +-------------------+-------------------+
               |                                       |
         +-----v-----+                           +-----v-----+
         | Service A |                           | Service B |
         +-----+-----+                           +-----+-----+
               |                                       |
         +-----v-----+                           +-----v-----+
         |  App A Pod|                           |  App B Pod|
         +-----------+                           +-----------+
```

---

## 🧩 3. Let’s Implement in **Minikube**

We’ll create **2 simple applications** (`app1` and `app2`)
Each has its **own Deployment + Service**, but both share a **single Ingress Controller** (NGINX).

---

### **Step 1: Start Minikube**

```bash
minikube start --cpus=4 --memory=8192 --nodes=2 --driver=docker
```

(Optional) enable NGINX Ingress Controller built-in addon:

```bash
minikube addons enable ingress
```

👉 This deploys NGINX Ingress Controller inside the `kube-system` namespace.

---

### **Step 2: Verify Ingress Controller is running**

```bash
kubectl get pods -n kube-system | grep ingress
```

You should see something like:

```
ingress-nginx-controller-xxxxx   1/1   Running
```

---

### **Step 3: Create two applications**

#### **app1-deploy.yaml**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app1-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: app1
  template:
    metadata:
      labels:
        app: app1
    spec:
      containers:
      - name: app1
        image: nginx
        ports:
        - containerPort: 80
        env:
        - name: APP_NAME
          value: "App1"
---
apiVersion: v1
kind: Service
metadata:
  name: app1-service
spec:
  selector:
    app: app1
  ports:
  - port: 80
    targetPort: 80
```

#### **app2-deploy.yaml**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app2-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: app2
  template:
    metadata:
      labels:
        app: app2
    spec:
      containers:
      - name: app2
        image: httpd
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: app2-service
spec:
  selector:
    app: app2
  ports:
  - port: 80
    targetPort: 80
```

Apply both:

```bash
kubectl apply -f app1-deploy.yaml
kubectl apply -f app2-deploy.yaml
```

---

### **Step 4: Create an Ingress Resource**

#### **ingress.yaml**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: demo-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: app1.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app1-service
            port:
              number: 80
  - host: app2.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app2-service
            port:
              number: 80
```

Apply it:

```bash
kubectl apply -f ingress.yaml
```

---

### **Step 5: Test Ingress**

Find Minikube IP:

```bash
minikube ip
```

Let’s say it returns: `192.168.49.2`

Add entries in your `/etc/hosts` (Linux/macOS) or
`C:\Windows\System32\drivers\etc\hosts` (Windows):

```
192.168.49.2   app1.local
192.168.49.2   app2.local
```

Now open:

* [http://app1.local](http://app1.local) → NGINX default page
* [http://app2.local](http://app2.local) → Apache default page

🎉 Both apps are served through the same NGINX Ingress Controller!

---

## ✅ **Recap**

| Component              | Role                           |
| ---------------------- | ------------------------------ |
| **Deployment**         | Runs the pods for each app     |
| **Service**            | Exposes each app internally    |
| **Ingress**            | Defines routing rules          |
| **Ingress Controller** | Implements those rules (NGINX) |
| **Minikube IP**        | Acts as external access point  |

---

Would you like me to show how to **enable path-based routing** (like `/app1` and `/app2` on the same hostname instead of separate domains)?
That’s another common pattern used in production setups.
