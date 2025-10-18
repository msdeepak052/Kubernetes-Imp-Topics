# K8S Core - DNS

## 🧠 What is CoreDNS in Kubernetes?

---

## 🔹 **Definition**

**CoreDNS** is the **default DNS server** used in modern Kubernetes clusters (since v1.13+). It is a **modular, flexible DNS server written in Go**, designed to provide **name resolution (DNS)** inside the Kubernetes cluster.

It is deployed as a **Kubernetes Deployment**, and runs as **pods** in the **`kube-system`** namespace.

> In simple terms: CoreDNS enables **pods and services** in Kubernetes to find and talk to each other **by name**, not IP.

[CoreDNS Administration Guide](https://kubernetes.io/docs/tasks/administer-cluster/coredns/)
[DNS Debugging and Resolution Guide](https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/)

---

## 📡 Why is CoreDNS Important?

In Kubernetes:

* Pods have **dynamic IPs**.
* You need **service discovery** so that one pod can find another **without knowing its IP**.

That’s where **CoreDNS** steps in:

* It maps **service names** (like `backend.default.svc.cluster.local`) to their respective **Cluster IPs**.
* It acts as a **DNS resolver** for all pods.

---

## 🧱 CoreDNS Architecture in Kubernetes

### 🎯 High-Level Flow:

```
[Pod] --> [CoreDNS Pod] --> [Kube-API / Upstream DNS]
```

### CoreDNS as a DNS Server:

* **Listens** on port 53 inside the cluster
* Deployed as a **Deployment** with a **Service**
* Each pod uses CoreDNS via `/etc/resolv.conf`

### 📁 Pods' resolv.conf file (example):

```bash
nameserver 10.96.0.10  # IP of CoreDNS ClusterIP Service
search default.svc.cluster.local svc.cluster.local cluster.local
options ndots:5
```

This configuration ensures that when a pod tries to resolve `backend`, CoreDNS attempts:

1. `backend.default.svc.cluster.local`
2. `backend.svc.cluster.local`
3. `backend.cluster.local`
4. `backend` (fallback)

---

## 🧪 Example: How CoreDNS Works in a Real Kubernetes Cluster

Let’s say you have:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: default
spec:
  selector:
    app: backend
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
```

And a pod with:

```yaml
command: ["curl", "http://backend"]
```

### 🔍 What Happens:

1. Pod tries to resolve `backend` → CoreDNS receives query.
2. CoreDNS sees that `backend.default.svc.cluster.local` is a service in the `default` namespace.
3. CoreDNS responds with the **ClusterIP** of the service.
4. Pod sends traffic to `http://10.96.33.5` (for example), which routes to the backend pod.

Without CoreDNS, this DNS resolution **wouldn’t happen**, and service discovery would fail.

---

## 🧩 CoreDNS ConfigMap – How CoreDNS is Configured

The configuration lives in a **ConfigMap** in `kube-system` namespace:

```bash
kubectl -n kube-system get configmap coredns -o yaml
```

### 🧾 Sample CoreDNS Config:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: coredns
  namespace: kube-system
data:
  Corefile: |
    .:53 {
        errors
        health
        ready
        kubernetes cluster.local in-addr.arpa ip6.arpa {
            pods insecure
            fallthrough in-addr.arpa ip6.arpa
        }
        prometheus :9153
        forward . /etc/resolv.conf
        cache 30
        loop
        reload
        loadbalance
    }
```

### 🔍 Breakdown of Modules:

| Module                       | Description                                                     |
| ---------------------------- | --------------------------------------------------------------- |
| `kubernetes`                 | Enables Kubernetes service discovery (`.svc.cluster.local`)     |
| `forward . /etc/resolv.conf` | Forward external DNS queries (e.g., google.com) to upstream DNS |
| `cache`                      | Caches DNS responses                                            |
| `loop`                       | Prevents infinite query loops                                   |
| `prometheus`                 | Enables metrics on port 9153                                    |
| `reload`                     | Reload config without restarting                                |
| `health`, `ready`            | For health and readiness probes                                 |

---

## 🔄 How CoreDNS Resolves Names Internally

### Internal DNS Queries

* **Pod → Service DNS**

  * Pod → `backend.default.svc.cluster.local` → CoreDNS → returns service ClusterIP.

* **Pod → Pod IP (not common)**

  * Requires `hostnames` or `headless services`.

### External DNS Queries

* Pod tries to `curl google.com`
* CoreDNS forwards this request to the IPs in `/etc/resolv.conf` (e.g., Google DNS or cloud provider DNS)

---

## 🔐 CoreDNS Security & High Availability

* CoreDNS is typically deployed with **2 or more replicas**.
* Uses **ClusterIP** service, so kube-proxy forwards traffic to a healthy CoreDNS pod.
* Supports **RBAC**, **TLS** (for plugins like etcd), and **NetworkPolicy** for isolation.
* Supports monitoring via **Prometheus metrics** on port 9153.

---

## 🔍 Troubleshooting CoreDNS

### 🔧 Common issues:

| Issue                        | Fix                                                |
| ---------------------------- | -------------------------------------------------- |
| DNS lookup fails             | Check if CoreDNS pods are running                  |
| External DNS fails           | Check `forward` in Corefile and `/etc/resolv.conf` |
| Internal names not resolving | Check service and pod names                        |
| Long resolution time         | Reduce `ndots` or tweak `cache` settings           |

### 🔍 Debug Example:

```bash
kubectl exec -it testpod -- nslookup backend.default.svc.cluster.local
```

If it fails:

* Check CoreDNS logs:

```bash
kubectl -n kube-system logs -l k8s-app=kube-dns
```

---

## 🔄 CoreDNS vs kube-dns (Legacy)

| Feature       | CoreDNS   | kube-dns     |
| ------------- | --------- | ------------ |
| Written in    | Go        | Go + Dnsmasq |
| Modular       | ✅ Yes     | ❌ No         |
| Performance   | ✅ Better  | ⚠️ Slower    |
| Extensibility | ✅ Plugins | ❌ No         |
| Active Dev    | ✅ Yes     | ❌ Deprecated |

---

## ✅ Summary

| Aspect          | Details                                                     |
| --------------- | ----------------------------------------------------------- |
| What            | CoreDNS is the **DNS server for Kubernetes**                |
| Why             | Provides **name resolution** for services and pods          |
| Works by        | Mapping `.svc.cluster.local` names to IPs                   |
| Deployed as     | Pods in `kube-system` namespace                             |
| Config          | Controlled via **Corefile** in ConfigMap                    |
| Uses            | Plugins like `kubernetes`, `forward`, `cache`, `prometheus` |
| Troubleshooting | Use `nslookup`, logs, config inspection                     |
| Benefits        | Fast, modular, extensible, Prometheus-ready                 |

---

> Let’s walk through a **hands-on CoreDNS lab in Kubernetes**. This will simulate a **service discovery issue** and teach you how to debug and fix DNS resolution using **CoreDNS**.

---

# 🧪 CoreDNS Hands-On Lab: Service Discovery Debugging in Kubernetes

---

## 🧰 **Lab Setup Requirements**

* A running Kubernetes cluster (minikube, kind, EKS, etc.)
* `kubectl` configured
* Basic YAML editing ability

---

## 🏗️ **Step 1: Verify CoreDNS is Running**

```bash
kubectl get pods -n kube-system -l k8s-app=kube-dns
```

> Expected Output:

```bash
NAME                       READY   STATUS    RESTARTS   AGE
coredns-74ff55c5b-xxxx     1/1     Running   0          3h
coredns-74ff55c5b-yyyy     1/1     Running   0          3h
```

Also verify the **ClusterIP** of CoreDNS service:

```bash
kubectl get svc -n kube-system kube-dns
```

> Look for something like: `10.96.0.10`

---

## 🧪 **Step 2: Create a Test Backend Service**

### backend.yaml

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: backend
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
spec:
  selector:
    app: backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
```

Apply it:

```bash
kubectl apply -f backend.yaml
```

---

## 🧪 **Step 3: Create a BusyBox Test Pod to Simulate DNS Requests**

### dns-test.yaml

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: dns-test
spec:
  containers:
  - name: dnsutils
    image: busybox
    command:
      - sleep
      - "3600"
```

Apply:

```bash
kubectl apply -f dns-test.yaml
```

Wait until it’s running:

```bash
kubectl get pod dns-test
```

---

## 🧪 **Step 4: Test DNS Resolution**

### Open a shell inside the pod:

```bash
kubectl exec -it dns-test -- sh
```

### Run DNS lookup (nslookup):

```bash
nslookup backend.default.svc.cluster.local
```

> You should see a result like:

```bash
Name: backend.default.svc.cluster.local
Address: 10.109.245.137
```

If it fails:

```bash
;; connection timed out; no servers could be reached
```

---

## 🕵️‍♂️ **Step 5: Simulate DNS Failure**

Let’s **edit the CoreDNS config** to remove the Kubernetes plugin (simulating a broken setup):

```bash
kubectl -n kube-system edit configmap coredns
```

Look for this block:

```hcl
kubernetes cluster.local in-addr.arpa ip6.arpa {
    pods insecure
    fallthrough in-addr.arpa ip6.arpa
}
```

🛑 **Comment it out** or delete it.

Save and exit.

Then **restart the CoreDNS pods**:

```bash
kubectl -n kube-system rollout restart deployment coredns
```

Wait for them to become ready:

```bash
kubectl -n kube-system get pods -l k8s-app=kube-dns
```

---

## 🔁 Re-Test DNS (Expected Failure)

```bash
kubectl exec -it dns-test -- nslookup backend.default.svc.cluster.local
```

Now, DNS will **fail** because CoreDNS can’t resolve Kubernetes service names.

---

## 🛠️ **Step 6: Debugging CoreDNS**

### View logs:

```bash
kubectl -n kube-system logs -l k8s-app=kube-dns
```

Look for errors like:

```
plugin/kubernetes: no API server connection
```

### Check CoreDNS health:

```bash
kubectl -n kube-system get endpoints kube-dns
```

Make sure it has **2 IPs** (CoreDNS pods).

---

## 🔁 **Step 7: Fix CoreDNS and Redeploy**

Edit ConfigMap again:

```bash
kubectl -n kube-system edit configmap coredns
```

Paste back the `kubernetes` plugin block:

```hcl
kubernetes cluster.local in-addr.arpa ip6.arpa {
    pods insecure
    fallthrough in-addr.arpa ip6.arpa
}
```

Restart CoreDNS:

```bash
kubectl -n kube-system rollout restart deployment coredns
```

---

## ✅ Step 8: Re-test and Verify Resolution Works

```bash
kubectl exec -it dns-test -- nslookup backend.default.svc.cluster.local
```

You should now get a successful DNS response.

---

## 📊 Bonus: View DNS Metrics in Prometheus

If Prometheus is running, CoreDNS exposes metrics at:

```
http://<coredns-pod-ip>:9153/metrics
```

You can also use **Grafana dashboards** to monitor DNS latency, cache hits, etc.

---

## ✅ Summary of What You Learned

| Step | What You Did                             |
| ---- | ---------------------------------------- |
| 1    | Verified CoreDNS and Service             |
| 2    | Deployed test backend service            |
| 3    | Created test pod to simulate DNS queries |
| 4    | Performed real DNS lookup                |
| 5    | Broke DNS by editing CoreDNS ConfigMap   |
| 6    | Observed DNS failure and logs            |
| 7    | Fixed CoreDNS config and restarted pods  |
| 8    | Verified successful resolution again     |

---

> Let’s walk through **CoreDNS**, its detailed role in Kubernetes, and how it relates to the older **kube-dns**. I’ll cover:

---

### 🔹 What is CoreDNS?

**CoreDNS** is the **default DNS server** in modern Kubernetes clusters (v1.13+). It provides **service discovery** by resolving Kubernetes service names to their cluster IPs.

It is deployed as a **Deployment** (usually in the `kube-system` namespace) and acts as the **DNS resolver** for all Pods inside the cluster.

---

### 🔹 Why DNS is Needed in Kubernetes?

In Kubernetes:

* Every **Service** gets a DNS name (e.g., `my-service.my-namespace.svc.cluster.local`).
* Every **Pod** or **application** needing to access a service can use that DNS name.
* CoreDNS resolves that name into the **ClusterIP** of the Service.

🟢 Example:

Imagine you have:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-backend
  namespace: default
spec:
  selector:
    app: backend
  ports:
    - port: 80
```

A frontend pod can **resolve** `my-backend.default.svc.cluster.local` to access it.

---

### 🔹 CoreDNS Architecture in Kubernetes

```plaintext
        +------------------+
        |     Pod          |
        |   (frontend)     |
        +--------+---------+
                 |
            DNS Request: my-backend.default.svc.cluster.local
                 |
        +--------v---------+
        |    CoreDNS       |
        |  (kube-system ns)|
        +--------+---------+
                 |
           Queries Kubernetes API
                 |
        +--------v---------+
        |   kube-apiserver |
        +------------------+
```

---

### 🔹 CoreDNS Deployment (Typical)

You’ll find this by:

```bash
kubectl get pods -n kube-system -l k8s-app=kube-dns
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: coredns
  namespace: kube-system
spec:
  replicas: 2
  selector:
    matchLabels:
      k8s-app: kube-dns
  template:
    metadata:
      labels:
        k8s-app: kube-dns
    spec:
      containers:
      - name: coredns
        image: coredns/coredns:1.10.1
        args: [ "-conf", "/etc/coredns/Corefile" ]
        volumeMounts:
        - name: config-volume
          mountPath: /etc/coredns
```

---

### 🔹 CoreDNS Configuration (Corefile)

`Corefile` is the config file for CoreDNS, found in a ConfigMap:

```bash
kubectl -n kube-system get configmap coredns -o yaml
```

Sample snippet:

```txt
.:53 {
    errors
    health
    kubernetes cluster.local in-addr.arpa ip6.arpa {
       fallthrough in-addr.arpa ip6.arpa
    }
    prometheus :9153
    forward . /etc/resolv.conf
    cache 30
    loop
    reload
    loadbalance
}
```

🔸 Key plugin here is `kubernetes`:

* It tells CoreDNS to look for service and pod names in the `cluster.local` domain using Kubernetes API.

---

### 🔹 How CoreDNS Resolves a Service?

For example, Pod wants to reach `my-backend.default.svc.cluster.local`:

1. Pod sends DNS query to the cluster DNS (CoreDNS pod IP).
2. CoreDNS parses domain:

   * `my-backend` → service name
   * `default` → namespace
3. CoreDNS queries kube-apiserver for the Service.
4. CoreDNS returns the Service's **ClusterIP** to the Pod.
5. Pod uses that IP to send request.

---

### 🔹 kube-dns vs CoreDNS

| Feature          | kube-dns  | CoreDNS                   |
| ---------------- | --------- | ------------------------- |
| Plugin-based     | ❌ No      | ✅ Yes (Highly Extensible) |
| Performance      | 🟡 Slower | 🟢 Faster (written in Go) |
| Memory Footprint | 🔺 Higher | 🔻 Lower                  |
| Config Format    | Hardcoded | Simple `Corefile` config  |
| Default Since    | < v1.11   | v1.13+                    |

✅ CoreDNS **replaced kube-dns** as default DNS server because:

* Better performance
* Flexible architecture
* Easy plugin support (e.g., logging, rewriting, caching)

---

### 🔹 Bonus: Debugging CoreDNS Issues

```bash
kubectl logs -n kube-system -l k8s-app=kube-dns
```

Test DNS resolution:

```bash
kubectl exec -it <pod-name> -- nslookup my-backend.default.svc.cluster.local
```

---

> Let's break this down step-by-step for **why the CoreDNS service is still called `kube-dns`** in Kubernetes, even though the actual DNS server running is **CoreDNS**.

---

### 🔍 TL;DR

The **service name `kube-dns` is preserved for backward compatibility**, even though **CoreDNS** has replaced **kube-dns** as the default DNS server in Kubernetes clusters since version 1.11.

---

### 🧠 Understanding the Evolution: kube-dns vs CoreDNS

| Feature       | `kube-dns` (older)                     | `CoreDNS` (current default)           |
| ------------- | -------------------------------------- | ------------------------------------- |
| Type          | Pod running dnsmasq, kube-dns, sidecar | Single binary plugin-based DNS server |
| Extensibility | Hard to extend                         | Highly extensible (plugins)           |
| Performance   | Slower due to sidecars                 | Faster (no sidecars, more efficient)  |
| Default since | ≤ v1.10                                | v1.11 onwards                         |

---

### 🧭 Why the Service is Still Called `kube-dns`?

Even though **CoreDNS** is deployed, the **Service name is not changed**:

```bash
kubectl get svc -n kube-system
```

You'll see:

```bash
NAME       TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)         AGE
kube-dns   ClusterIP   10.96.0.10     <none>        53/UDP,53/TCP   xxx
```

#### 🔧 Reason: Backward Compatibility

Many applications and scripts within the Kubernetes ecosystem reference `kube-dns` as the **DNS service name**. Changing the name would:

* Break existing deployments.
* Require updates in clients using the DNS service.
* Introduce unnecessary migration overhead.

So, instead of renaming the service to `coredns`, the Kubernetes maintainers **kept the name `kube-dns`** but pointed it to CoreDNS Pods under the hood.

---

### 🔄 What Actually Happens Behind the Scenes

#### 🔹 Service (kube-dns)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: kube-dns
  namespace: kube-system
spec:
  clusterIP: 10.96.0.10
  ports:
  - name: dns
    port: 53
    protocol: UDP
  - name: dns-tcp
    port: 53
    protocol: TCP
  selector:
    k8s-app: kube-dns
```

> 📌 `k8s-app: kube-dns` is the key label used to select the pods. Even CoreDNS pods are labeled this way for compatibility.

#### 🔹 Pods (Actually CoreDNS)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: coredns
  namespace: kube-system
spec:
  selector:
    matchLabels:
      k8s-app: kube-dns
  template:
    metadata:
      labels:
        k8s-app: kube-dns
    spec:
      containers:
      - name: coredns
        image: coredns/coredns:1.8.0
```

> ✅ Though the deployment is for `coredns`, the label still uses `k8s-app: kube-dns`, so it’s selected by the existing Service.

---

### 📞 What Happens When a Pod Does DNS Lookup?

1. A pod tries to resolve a service like `myapp.default.svc.cluster.local`.
2. It sends a DNS query to the DNS service IP (`10.96.0.10`) — this is the ClusterIP of `kube-dns`.
3. This IP routes the request to one of the CoreDNS pods (based on the label selector).
4. CoreDNS resolves the name using its plugin chain and returns the response.

---

### 🔐 Bonus: `/etc/resolv.conf` in Pod

Inside any pod:

```bash
cat /etc/resolv.conf
```

You'll see something like:

```
nameserver 10.96.0.10
search default.svc.cluster.local svc.cluster.local cluster.local
```

So all DNS queries go to `10.96.0.10`, which is the IP of `kube-dns` — which actually routes to CoreDNS.

---

### ✅ Summary

| Question                                        | Answer                                                    |
| ----------------------------------------------- | --------------------------------------------------------- |
| Why is the DNS service still called `kube-dns`? | For **backward compatibility**.                           |
| Is `kube-dns` still the DNS server?             | No. It’s a **Service** pointing to **CoreDNS pods**.      |
| How does CoreDNS replace kube-dns?              | By using the same labels and service name.                |
| What do applications see?                       | No change — they continue to query `kube-dns` service IP. |

---



