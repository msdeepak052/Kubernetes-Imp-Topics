# **DaemonSets**
---

## 🔹 What is a DaemonSet?

* A **DaemonSet** ensures that **a copy of a Pod runs on all (or some) nodes** in a Kubernetes cluster.
* Whenever a new node joins the cluster, the DaemonSet automatically schedules a Pod on it.
* When a node leaves, the Pod is automatically removed.

👉 Think of it as “deploy everywhere in the cluster”.

---

## 🔹 Why DaemonSet is used?

Some **real-world use cases**:

1. **Cluster Monitoring**

   * Running **Prometheus Node Exporter** or **Datadog Agent** on every node to collect metrics.
2. **Log Collection**

   * Running **Fluentd / Filebeat / Logstash** on every node to forward logs.
3. **Networking**

   * Running **CNI plugins** (e.g., Calico, Weave, Flannel agents).
4. **Storage Daemons**

   * Running daemons like **Ceph, GlusterFS agents** on each node.
5. **Security**

   * Running **antivirus/IDS agents** (Falco, Sysdig) on all nodes.

---

## 🔹 Important Points about DaemonSets

* Unlike Deployments, **DaemonSets don’t scale** (they automatically run one Pod per node).
* If you taint a node, DaemonSets may not run unless you add tolerations.
* To restrict DaemonSet Pods to specific nodes, you can use:

  * `nodeSelector`
  * `nodeAffinity`
  * `tolerations`

---

## 🔹 Example 1: Simple DaemonSet (Nginx running on every node)

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: nginx-daemonset
  namespace: default
spec:
  selector:
    matchLabels:
      app: nginx-daemon
  template:
    metadata:
      labels:
        app: nginx-daemon
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
```

👉 This will deploy an **nginx Pod on every node** in your cluster.

---

## 🔹 Example 2: Real-life DaemonSet (Fluentd for Log Collection)

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
  namespace: kube-system
spec:
  selector:
    matchLabels:
      name: fluentd
  template:
    metadata:
      labels:
        name: fluentd
    spec:
      tolerations:
      - key: node-role.kubernetes.io/master
        operator: Exists
        effect: NoSchedule
      containers:
      - name: fluentd
        image: fluent/fluentd:v1.12
        resources:
          limits:
            memory: 200Mi
          requests:
            cpu: 100m
            memory: 200Mi
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
```

👉 This ensures **Fluentd runs on every node**, collecting logs from `/var/log` and forwarding them.

---

## 🔹 Example 3: Prometheus Node Exporter (Monitoring DaemonSet)

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: node-exporter
  template:
    metadata:
      labels:
        app: node-exporter
    spec:
      containers:
      - name: node-exporter
        image: prom/node-exporter:latest
        ports:
        - containerPort: 9100
          name: metrics
```

👉 Runs **Prometheus Node Exporter** on all nodes for metrics scraping.

---

## 🔹 Useful Commands

```bash
# List DaemonSets
kubectl get ds -A

# Describe a DaemonSet
kubectl describe ds <name> -n <namespace>

# See Pods created by DaemonSet
kubectl get pods -o wide --selector=app=nginx-daemon
```

---

✅ In short:

* **Deployment** → scalable apps
* **StatefulSet** → stateful apps (DBs)
* **DaemonSet** → node-level agents

---

Deepak, do you want me to also show you **how to expose a DaemonSet via Service** (e.g., making the nginx DaemonSet accessible on each node like a node-level web server)?
