# Custom-Metrics-Server

### **Custom Metrics Server vs. Kubernetes Metrics Server**
To understand the **Custom Metrics Server**, let's first clarify the difference between the standard **Metrics Server** and the **Custom Metrics Server**.

#### **1. Kubernetes Metrics Server**
- **What it does**:  
  - The Metrics Server is a built-in component that collects resource usage metrics (CPU and memory) from Kubernetes nodes and pods.
  - It provides basic metrics to the **Horizontal Pod Autoscaler (HPA)** for scaling based on CPU/memory utilization.
- **Limitations**:  
  - It **only** provides CPU and memory metrics.
  - It **cannot** fetch application-specific metrics (e.g., requests per second, queue length, database connections).

#### **2. Custom Metrics Server**
- **What it does**:  
  - A **Custom Metrics Server** (like Prometheus Adapter, Datadog, or others) allows HPA to scale based on **application-specific metrics** (not just CPU/memory).
  - It extends HPA to work with metrics like:
    - HTTP requests per second
    - Queue length (e.g., RabbitMQ, Kafka)
    - Database connections
    - GPU usage
    - Business logic metrics (e.g., "orders per minute")
- **Why it was introduced**:  
  - Many applications need scaling based on **business logic**, not just CPU/memory.
  - Example: An e-commerce app may need to scale when there are **1000 orders/min**, even if CPU usage is low.

---

### **How Custom Metrics Server Works**
1. **Metrics Collection**  
   - A monitoring tool (like **Prometheus, Datadog, or Stackdriver**) collects custom metrics from your application.
   - Example: Prometheus scrapes an `/metrics` endpoint exposed by your app.

2. **Custom Metrics Adapter**  
   - A **Custom Metrics Adapter** (e.g., Prometheus Adapter) converts these metrics into a format that Kubernetes understands.
   - It exposes them via the **Kubernetes Custom Metrics API**.

3. **HPA Uses Custom Metrics**  
   - HPA queries the **Custom Metrics API** (instead of just the Metrics Server).
   - Scaling decisions are made based on these custom metrics.

---

### **Integration Example (Prometheus Adapter)**
#### **Scenario:**  
- You have a web app that exposes `http_requests_total` (requests per second).
- You want HPA to scale when requests exceed **100 RPS**.

#### **Steps:**
1. **Deploy Prometheus**  
   - Install Prometheus to scrape `/metrics` from your app.
   ```sh
   helm install prometheus prometheus-community/prometheus
   ```

2. **Deploy Prometheus Adapter**  
   - The adapter converts Prometheus metrics into Kubernetes custom metrics.
   ```sh
   helm install prometheus-adapter prometheus-community/prometheus-adapter
   ```

3. **Configure HPA to Use Custom Metrics**  
   ```yaml
   apiVersion: autoscaling/v2
   kind: HorizontalPodAutoscaler
   metadata:
     name: myapp-hpa
   spec:
     scaleTargetRef:
       apiVersion: apps/v1
       kind: Deployment
       name: myapp
     minReplicas: 1
     maxReplicas: 10
     metrics:
     - type: Pods
       pods:
         metric:
           name: http_requests_per_second
         target:
           type: AverageValue
           averageValue: 100
   ```

4. **Verify Custom Metrics**  
   ```sh
   kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta1" | jq .
   ```

---

### **What Happens If You Don’t Use Custom Metrics?**
| Scenario | With Custom Metrics | Without Custom Metrics |
|----------|---------------------|------------------------|
| **HTTP Traffic Spike** | HPA scales up when requests exceed 100 RPS. | HPA **does not react** (unless CPU/memory increases). |
| **Queue Processing** | HPA scales based on queue length (e.g., Kafka backlog). | HPA **cannot scale** based on queue length. |
| **Business Logic Scaling** | HPA scales when "orders per minute" exceed a threshold. | HPA **ignores business metrics**. |

---

### **Real-World Use Cases**
1. **E-Commerce App**  
   - Scale based on **orders per minute**, not just CPU.
2. **Streaming Service**  
   - Scale based on **concurrent viewers**.
3. **Microservices with High Variability**  
   - Scale based on **API call rate** rather than CPU.

---

### **Conclusion**
- **Metrics Server**: Only CPU/memory scaling (basic use cases).
- **Custom Metrics Server**: Enables scaling based on **application-specific metrics** (advanced use cases).
- **When to use**:  
  - Use **Custom Metrics** when scaling depends on business logic, traffic, or external systems.
  - Use **Metrics Server** if CPU/memory scaling is sufficient.

You're asking a great question that touches the heart of **Kubernetes autoscaling architecture**. Let's break it down in the deepest, most intuitive way possible, using an analogy first to get the mental model right, and then diving into the full technical internals:

---

### 🧠 HIGH-LEVEL INTUITION: Imagine a Restaurant Kitchen

Suppose you run a large restaurant. The **head chef (Kubernetes HPA)** adjusts the number of line cooks (**Pods**) based on how **busy the kitchen** is.

* You install a **thermometer** (metrics-server) to measure **kitchen temperature and humidity**. These are **basic, built-in metrics** — analogous to **CPU and memory usage**.
* But then, your restaurant starts getting fancy. You want to scale based on **number of orders in queue**, or **average waiting time for a table**. You can't get these from the thermometer.
* Now you need a **custom sensor** system — maybe connected to the ordering system or table waitlist. This is your **custom metrics server**.

Let’s now translate this analogy into Kubernetes terms.

---

### 🔧 WHAT IS THE METRICS SERVER?

**Metrics Server** is a cluster-wide aggregator of resource usage data — but it **only collects standard metrics**, namely:

* **CPU usage**
* **Memory usage**

…and only **from Pods and Nodes**.

This is enough for **basic Horizontal Pod Autoscaler (HPA)** setups. You can scale pods up/down based on CPU or memory usage.

> But what if you want to scale your app based on:
>
> * Request rate (e.g. HTTP requests per second)
> * Queue length (e.g. pending jobs in RabbitMQ)
> * Custom business metrics (e.g. number of active users)
>
> ➡️ You need a **Custom Metrics API** and a **Custom Metrics Server**.

---

### 🔧 WHAT IS A CUSTOM METRICS SERVER?

A **Custom Metrics Server** is a component that implements the **Custom Metrics API**, which is an extension of the Kubernetes API that allows your autoscalers to use **application-level or business-level metrics** instead of just CPU/Memory.

It exposes these metrics at:

```
/apis/custom.metrics.k8s.io/v1beta1/
```

So you can say:

> "Hey HPA, scale my pods not by CPU, but by how many jobs are in the queue."

---

### 🚀 WHY WAS THIS NEEDED?

Let’s get super clear:

| Without Custom Metrics Server | With Custom Metrics Server                             |
| ----------------------------- | ------------------------------------------------------ |
| Can only scale on CPU/memory  | Can scale on anything measurable                       |
| Metrics come from Kubelet     | Metrics can come from Prometheus, HTTP endpoints, etc. |
| Good for compute-heavy apps   | Good for async workers, queues, web servers, etc.      |

---

### ⚙️ HOW IS CUSTOM METRICS SERVER INTEGRATED?

It works through **adapters** that implement the **Custom Metrics API**. One of the most common is:

> **Prometheus Adapter** – integrates **Prometheus metrics** with Kubernetes HPA.

#### ✅ Integration Flow (Step-by-step):

1. **App exposes custom metrics**, e.g. `http_requests_total` or `queue_depth`, using a Prometheus client library.
2. **Prometheus scrapes** those metrics.
3. **Prometheus Adapter** is deployed — a Kubernetes API extension that allows HPA to query Prometheus.
4. You define a **Custom HPA** that scales based on a Prometheus metric.
5. When needed, HPA queries the Kubernetes Custom Metrics API, which is served by the Prometheus Adapter.

---

### 📦 EXAMPLE USE CASE

Imagine a **video processing system** where each pod picks up a video job from a queue (e.g., RabbitMQ or Redis Queue). You want to scale the number of pods depending on how many jobs are in the queue.

#### Without Custom Metrics Server:

* Can’t scale based on queue size.
* Pods may be idle (too many) or overloaded (too few).

#### With Custom Metrics Server:

* You expose a metric `queue_depth` via Prometheus.
* HPA scales pods from 1 to 20 based on `queue_depth > 50`.
* Your system stays responsive without wasting resources.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: video-processor
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: video-processor
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: External
    external:
      metric:
        name: queue_depth
      target:
        type: Value
        value: "50"
```

---

### ❌ WHAT IF YOU DON’T USE A CUSTOM METRICS SERVER?

Let’s see both **symptoms and consequences**.

#### Symptoms:

* You can only scale on CPU/memory.
* Your autoscaler becomes **blind** to app-specific load.
* You try to force application behavior into CPU/memory usage, which can be imprecise.

#### Consequences:

* **Under-scaling**: Your queue might grow unbounded while CPU is idle.
* **Over-scaling**: You might waste resources during low-traffic times.
* **Latency spikes**: If your pods don’t scale fast enough to match load, you’ll get delays.

---

### 🔄 RECAP:

| Feature                     | Metrics Server | Custom Metrics Server |
| --------------------------- | -------------- | --------------------- |
| Scales on CPU/memory        | ✅ Yes          | ❌ No                  |
| Scales on app-level metrics | ❌ No           | ✅ Yes                 |
| Requires Prometheus         | ❌ No           | ✅ Usually             |
| Exposes `/metrics` endpoint | ❌ No           | ✅ Yes                 |

---

Excellent — these are the most fundamental and technical questions when diving into **Kubernetes autoscaling internals**. Let me answer them in depth, using intuitive analogies and full technical detail.

---

## 🧠 1. How does the Kubernetes HPA communicate with the metrics server? What API does it use, and how are metrics discovered?

### 🔧 Technical Answer:

The **Horizontal Pod Autoscaler (HPA)** controller runs inside the Kubernetes controller manager. Every **period (default: 15 seconds)**, it:

1. **Reads the current state of the workload** (e.g., Deployment, StatefulSet).
2. **Queries the Kubernetes Metrics APIs** to fetch usage stats.

   * For **CPU/memory**: it hits the **Resource Metrics API** (`/apis/metrics.k8s.io/v1beta1`).
   * This API is **served by the metrics-server**.
3. Then HPA computes the ratio:

   ```
   currentMetric / targetMetric = scalingFactor
   ```

   and adjusts replicas accordingly.

The HPA doesn’t talk **directly** to metrics-server. Instead:

* It uses **Kubernetes API aggregation layer**.
* The `metrics-server` **registers** itself as an API service to serve `/apis/metrics.k8s.io`.

### 🧠 Analogy:

Imagine HPA is a **restaurant manager** asking the front desk:

> “How hot is the kitchen (CPU)? How much water have we used (memory)?”

The **front desk** (Kube API server) doesn't have these numbers but knows that the **utility monitor (metrics-server)** does, so it redirects the request.

---

## 🧠 2. In what way is the `HorizontalPodAutoscaler` API different when using CPU-based scaling vs custom metric-based scaling?

### 🔧 Technical Answer:

In **`autoscaling/v1`**, the only supported metrics are:

```yaml
metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 80
```

When you want to scale on **custom or external metrics**, you must use **`autoscaling/v2` or `v2beta2`**.

In `v2`, the `metrics` section supports:

* **Resource** (CPU, memory)
* **Pods** (custom metrics aggregated per pod)
* **Object** (metrics attached to Kubernetes objects)
* **External** (outside the cluster, like a cloud service)

```yaml
metrics:
- type: External
  external:
    metric:
      name: queue_length
    target:
      type: Value
      value: "100"
```

### 🧠 Analogy:

Think of `autoscaling/v1` as an old thermostat:

> It only adjusts based on **room temperature (CPU)**.

`autoscaling/v2` is a smart thermostat:

> It considers **humidity, sunlight, CO₂ levels**, or even **tweets about weather** (external sources).

---

## 🧠 3. How does the Prometheus Adapter know how to map Prometheus metrics into Kubernetes resource names? What mechanism is used for this mapping?

### 🔧 Technical Answer:

Prometheus Adapter needs to **map Prometheus metric labels** to **Kubernetes object references** (pods, deployments, etc.) so the HPA knows what the metric refers to.

This is done via **configuration in the adapter** (typically in a ConfigMap), which defines **rules using label selectors and regexes**.

Key components:

* **Rules** define how to interpret metrics and which labels identify Kubernetes objects.
* Labels like `pod`, `namespace`, or `deployment` must exist on the metric series.
* Adapter exposes the metrics at `/apis/custom.metrics.k8s.io` or `/apis/external.metrics.k8s.io`.

Example configuration (simplified):

```yaml
rules:
  - seriesQuery: 'http_requests_total{namespace!="",pod!=""}'
    resources:
      overrides:
        namespace: {resource: "namespace"}
        pod: {resource: "pod"}
    name:
      matches: "http_requests_total"
      as: "http_requests"
    metricsQuery: 'sum(rate(http_requests_total{<<.LabelMatchers>>}[2m])) by (<<.GroupBy>>)'
```

### 🧠 Analogy:

Imagine Prometheus metrics are **emails**:

> Each email has a **subject (metric name)** and **metadata (labels)**.

Prometheus Adapter is like an **email filter system**:

> It reads the subject and metadata, and sorts the emails into **employee folders (pods, namespaces)**.

---

## 🧠 4. Why does custom metrics-based HPA typically require the `v2` HPA API instead of `v1`?

### 🔧 Technical Answer:

The `autoscaling/v1` API was designed **only for CPU and memory**.

When you use **custom metrics**, you need:

* Support for **multiple metric types**
* Flexible ways to define **targets** (like "average value", "utilization", "per-pod" or "object-level")
* Support for **external metrics**, like from cloud APIs

These were introduced in **`autoscaling/v2beta2`**, and finalized in **`v2`**.

### 🧠 Analogy:

Think of `v1` as a **flip phone** — it can only call or text (CPU/memory).

`v2` is a **smartphone** — it can run apps, browse the web, track your location, and connect to external APIs.

---

## 🧠 5. How do you ensure the time-series resolution of Prometheus metrics is suitable for autoscaling decisions (i.e., what’s the effect of scrape interval and metric freshness)?

### 🔧 Technical Answer:

To ensure effective autoscaling:

* **Scrape Interval** (how often Prometheus pulls data) should be short — ideally every 15s or less.
* **HPA polling period** defaults to 15s — it checks metrics periodically.
* If your scrape interval is too long (e.g., 60s), metrics may **lag**, and autoscaler decisions become stale or misleading.
* **PromQL expressions** like `rate(metric[2m])` need sufficient samples within the window. Too sparse = unstable results.

To tune:

* Reduce `scrape_interval` in Prometheus config:

```yaml
global:
  scrape_interval: 15s
```

* Ensure metrics use **proper timestamps** and are exported with high enough **granularity**.

### 🧠 Analogy:

Imagine Prometheus as a **weather station**:

* If it reports the temperature once an hour, your **AC (HPA)** will react too slowly.
* You want **frequent updates** (every 15 seconds), so the AC keeps the room steady.

---

## ✅ NEXT STEP: Want to Dive Deeper?

You're stepping right into expert-level Kubernetes systems design — I love it.

We'll now go **layer-by-layer**, addressing all 4 of these with **deep technical detail** and **intuitive analogies**, so you’ll not just know what’s happening but *why* it's architected this way.

---

## **1. Internals of the Kubernetes API Aggregation Layer**

---

### 🔧 **What is it?**

The **API aggregation layer** allows Kubernetes to **extend its API surface** by delegating parts of its API tree to **custom API servers**, which register themselves with the **core API server**.

For example:

* `custom.metrics.k8s.io`
* `external.metrics.k8s.io`
* `metrics.k8s.io`

These aren't served by the kube-apiserver itself. Instead, kube-apiserver **proxies requests** to **registered API services** via the **APIService resource**.

---

### 📦 Architecture Flow

1. You deploy a component (like **Prometheus Adapter**).

2. It registers an `APIService` with the Kube API:

   ```yaml
   apiVersion: apiregistration.k8s.io/v1
   kind: APIService
   metadata:
     name: v1beta1.custom.metrics.k8s.io
   spec:
     service:
       name: prometheus-adapter
       namespace: custom-metrics
     group: custom.metrics.k8s.io
     version: v1beta1
   ```

3. The **kube-apiserver** sees this and says:

   > “Okay, I don’t serve `/apis/custom.metrics.k8s.io` myself. I’ll **proxy** requests to this service.”

4. When HPA queries `custom.metrics.k8s.io`, the core API server **transparently proxies the request** to the Prometheus Adapter.

5. The adapter implements a REST server that returns Kubernetes-style JSON.

---

### 🧠 Analogy:

Think of the Kubernetes API server as a **front desk at a huge building**.

When someone asks, “Can I speak to the **custom metrics department**?”, the front desk says:

> “We don’t handle that ourselves — but let me forward your call to the **external extension office** across the street.”

That’s the aggregation layer at work.

---

### 🧠 Bonus Insight: Security

Because kube-apiserver proxies the request, it handles **authentication, RBAC, and audit logging**, even for aggregated services. This keeps **extensibility without compromising security**.

---

## **2. Writing Your Own Metrics Adapter (Custom Metrics Server)**

---

### 🏗️ Goal:

Build a **Kubernetes-compatible REST API server** that serves metrics at:

```
/apis/custom.metrics.k8s.io/v1beta1
```

or

```
/apis/external.metrics.k8s.io/v1beta1
```

### 🔧 Core Requirements:

* **Implements Custom Metrics API spec**: See [Custom Metrics API types](https://github.com/kubernetes/metrics/tree/master/pkg/apis/custom_metrics).
* **Serves a RESTful HTTP API**.
* **Maps metric names + labels to Kubernetes resources** (pods, namespaces, etc.).
* **Uses an `APIService` object** to register itself.
* **Returns metrics as JSON-encoded Go structs matching the Kubernetes API schema.**

---

### 🧠 High-Level Components:

| Component              | Role                                                              |
| ---------------------- | ----------------------------------------------------------------- |
| REST API Server        | Handles HTTP requests at `/apis/...`                              |
| Metrics Backend Client | Scrapes or pulls metrics from Prometheus, Datadog, InfluxDB, etc. |
| Translator Layer       | Converts backend metrics into Kubernetes metric objects           |
| Resource Mapper        | Maps label-based metrics to Kubernetes objects                    |
| Registration Layer     | Registers itself via `APIService`                                 |

---

### 🧰 Frameworks/Libraries You Can Use:

* **client-go** – for Kubernetes resource discovery.
* **apimachinery** – for creating type-safe APIs.
* **custom-metrics-apiserver** – a reference server implementation.

You can clone the [k8s.io/sample-apiserver](https://github.com/kubernetes/sample-apiserver) repo as a starting point.

---

### 🧠 Analogy:

You're building a **Kubernetes-native “translator” server** that:

1. Understands business metrics (e.g., HTTP request rate),
2. Converts them to **Kubernetes dialect** (structured resource metrics),
3. And speaks via the **official API door** so the HPA can understand.

---

## **3. PromQL Mastery – Optimized Queries for Autoscaling**

---

### 🧠 First, Why Is This Hard?

Because **autoscaling depends on real-time decisions**, PromQL must:

* Be **fast** (don’t over-fetch)
* Be **stable** (don’t spike due to noise)
* Be **accurate** (track real load, not misleading spikes)

---

### 🔧 Best Practices:

#### ✅ Use `rate()` or `irate()`:

Avoid raw counters. Use:

```promql
rate(http_requests_total[2m])
```

to get per-second rate over a 2-minute window.

#### ✅ Use `avg_over_time()` or `max_over_time()` for gauges:

```promql
avg_over_time(queue_length[2m])
```

Smooths out random fluctuations.

#### ✅ Normalize metrics:

Convert raw counts to **per-pod, per-request, per-second** as appropriate.

#### ✅ Group by Kubernetes object:

```promql
sum(rate(requests_total{namespace="default"}[1m])) by (pod)
```

#### ✅ Limit cardinality:

Avoid queries with high-cardinality labels (e.g., `user_id`, `path`, etc.)

---

### ❌ Common Pitfalls:

| Mistake                           | Problem                            |
| --------------------------------- | ---------------------------------- |
| Using `queue_length` directly     | Might be a snapshot, not trend     |
| Using `rate()` on gauges          | Rate doesn't apply to non-counters |
| Using `sum()` without grouping    | Breaks pod-level metrics           |
| Very short time windows (`[10s]`) | Leads to erratic scaling behavior  |

---

### 🧠 Analogy:

Think of PromQL like a **dashboard camera** for your service. If you:

* Zoom in too close = noisy, blurry
* Zoom out too far = delayed reactions
* Mislabel = can’t tell which car (pod) is crashing

You want the **Goldilocks zone**: not too hot, not too cold.

---

## **4. Designing Metrics for Scale – Avoiding Noisy Metrics**

---

### ❌ Problem:

If metrics are noisy or bursty, HPA can:

* Oscillate up/down
* Overreact to transient events
* Create a **scaling storm** that destabilizes the system

---

### ✅ Strategies:

#### 1. **Smoothing windows**:

Use time windows like `rate(...[2m])`, not `[30s]`. Avoid spikes.

#### 2. **Target stable metrics**:

Pick metrics like:

* `request rate`
* `queue size`
* `latency P95`

Avoid:

* `logins per second`
* `cache misses`
* metrics with unpredictable variance

#### 3. **Per-pod normalization**:

Don’t scale on total request rate — divide by pod count:

```promql
sum(rate(requests_total[2m])) / count(kube_pod_info)
```

#### 4. **Avoid high-cardinality metrics**:

Don’t track per-user, per-path, per-customer.

#### 5. **Add hysteresis**:

Kubernetes doesn’t support hysteresis natively, but you can:

* Use `max_over_time` to delay scale-down.
* Use prediction buffers in custom controllers.

---

### 🧠 Analogy:

Designing autoscaling metrics is like setting up a **motion detector for security**:

* Too sensitive = alarms every 2 minutes (autoscale up/down)
* Too slow = break-ins go undetected (missed load spike)

You want a detector that triggers **only when real, sustained activity occurs**.

---

## ✅ Summary of All Four

| Topic                             | Key Insight                                                                                 |
| --------------------------------- | ------------------------------------------------------------------------------------------- |
| **API Aggregation Layer**         | Lets Kubernetes forward API calls to external metric APIs securely.                         |
| **Writing Custom Metrics Server** | Build a REST server that implements the Custom Metrics API and maps metrics to k8s objects. |
| **PromQL Mastery**                | Use `rate()`, group wisely, avoid cardinality, and use smoothing to stabilize autoscaling.  |
| **Metric Design for Scale**       | Choose durable, noise-resistant, meaningful metrics with long enough observation windows.   |

---

Fantastic! Let’s go with a **hands-on demo using Prometheus + Prometheus Adapter** to enable HPA scaling based on **HTTP requests per second** (a common real-world use case).  

---

## **🔧 Hands-On Demo: Scaling Based on Custom Metrics (Prometheus)**
### **Scenario**
- You have a **web app** that exposes Prometheus metrics (e.g., `http_requests_total`).
- You want **HPA to scale** when requests exceed **10 RPS (requests per second)** per pod.

---

### **🛠️ Prerequisites**
1. A **Kubernetes cluster** (Minikube, Kind, EKS, AKS, etc.).
2. **Helm** installed (`brew install helm` / `choco install kubernetes-helm`).
3. **kubectl** configured.

---

## **🚀 Step-by-Step Setup**
### **1. Deploy a Sample App (Exposes Prometheus Metrics)**
We’ll use a simple **Go/Python HTTP server** that exposes a `/metrics` endpoint.

#### **Deploy the app:**
```sh
kubectl create deploy demo-app --image=ghcr.io/nginxinc/nginx-prometheus-exporter:latest --port=9113
kubectl expose deploy demo-app --port=9113 --target-port=9113
```
*(This is a simple NGINX Prometheus exporter for demo purposes. In real cases, use your own app with `/metrics`.)*

---

### **2. Install Prometheus (Metrics Collector)**
We’ll use **Helm** for easy installation.

#### **Add Prometheus Helm repo:**
```sh
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

#### **Install Prometheus:**
```sh
helm install prometheus prometheus-community/prometheus
```

#### **Verify Prometheus is scraping metrics:**
```sh
kubectl port-forward svc/prometheus-server 9090
```
Open **http://localhost:9090** → Check **Targets** (should see `demo-app:9113`).

---

### **3. Install Prometheus Adapter (Custom Metrics API)**
This converts Prometheus metrics → Kubernetes Custom Metrics API.

#### **Install Prometheus Adapter:**
```sh
helm install prometheus-adapter prometheus-community/prometheus-adapter \
  --set prometheus.url=http://prometheus-server
```

#### **Verify Custom Metrics API:**
```sh
kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta1" | jq .
```
*(You should see Prometheus metrics exposed as Kubernetes custom metrics.)*

---

### **4. Configure HPA to Scale on HTTP Requests**
We’ll create an **HPA that scales when `nginx_http_requests_total` > 10 RPS per pod**.

#### **Apply HPA:**
```yaml
cat <<EOF | kubectl apply -f -
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: demo-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: demo-app
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Pods
    pods:
      metric:
        name: nginx_http_requests_total
      target:
        type: AverageValue
        averageValue: 10
EOF
```

#### **Check HPA:**
```sh
kubectl get hpa
```
*(Initially, it may show `<unknown>`. Wait a few minutes.)*

---

### **5. Generate Traffic to Trigger Scaling**
Let’s simulate traffic using `curl` in a loop.

#### **Run a temporary pod to send requests:**
```sh
kubectl run -it --rm load-generator --image=busybox -- /bin/sh -c "while true; do wget -q -O- http://demo-app:9113/metrics; done"
```

#### **Watch HPA scale up:**
```sh
watch kubectl get hpa
```
*(After ~1-2 mins, you should see **REQUESTS** increase and **REPLICAS** scale up!)*

---

## **📊 Expected Output**
```
NAME           REFERENCE             TARGETS     MINPODS   MAXPODS   REPLICAS   AGE
demo-app-hpa   Deployment/demo-app   500m/10     1         5         3          2m
```
*(Here, `500m` means 0.5 requests per second. If it exceeds `10`, HPA scales up.)*

---

## **🔍 Troubleshooting**
- **No metrics?** Check Prometheus targets (`http://localhost:9090/targets`).
- **HPA shows `<unknown>`?** Ensure `prometheus-adapter` is running (`kubectl logs -f <prometheus-adapter-pod>`).
- **Still stuck?** Let me know! 🚀

---

## **🎯 Key Takeaways**
✅ **Custom Metrics Server** (Prometheus Adapter) lets HPA scale on **any metric**, not just CPU/memory.  
✅ **Prometheus** collects app metrics, **Prometheus Adapter** exposes them to Kubernetes.  
✅ **HPA + Custom Metrics** = Autoscaling based on **real-world needs** (traffic, queues, etc.).  

---

### **📌 Next Steps?**
- Try scaling based on **Kafka queue length** or **database connections**.
- Explore **Datadog/Stackdriver** for cloud-managed metrics.
- Need another demo? Let me know! 😊  

# **Complete Guide: Integrating HPA with Custom Metrics Server in Kubernetes**

This guide provides a **step-by-step setup** for using **Custom Metrics Server (Prometheus Adapter)** with **Horizontal Pod Autoscaler (HPA)** to scale applications based on **custom metrics** (e.g., HTTP requests, queue length, etc.) instead of just CPU/memory.

---

## **📌 Overview**
1. **Why Custom Metrics?**  
   - HPA normally scales based on **CPU/Memory** (via Metrics Server).  
   - **Custom Metrics Server** allows scaling based on **application-specific metrics** (e.g., requests per second, Kafka backlog, DB connections).  

2. **How It Works**  
   - **Prometheus** collects metrics from apps.  
   - **Prometheus Adapter** converts them into Kubernetes-compatible metrics.  
   - **HPA** uses these custom metrics for scaling decisions.  

---

## **🚀 Step-by-Step Setup**
### **Prerequisites**
✔ Kubernetes Cluster (Minikube, EKS, AKS, GKE, etc.)  
✔ `kubectl` & `helm` installed.  
✔ (Optional) `jq` for JSON parsing.  

---

## **1️⃣ Deploy a Sample Application (Exposing Metrics)**
We’ll deploy a simple **NGINX Prometheus Exporter** (for demo purposes).  

### **Deploy the App**
```sh
kubectl create deploy demo-app --image=nginx:latest
kubectl expose deploy demo-app --port=80 --target-port=80
```

### **Add Prometheus Metrics (Sidecar)**
Since `nginx:latest` doesn’t expose Prometheus metrics by default, we’ll attach a **sidecar exporter**:
```sh
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: demo-app
  template:
    metadata:
      labels:
        app: demo-app
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9113"
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
      - name: nginx-exporter
        image: nginx/nginx-prometheus-exporter:latest
        args:
          - '-nginx.scrape-uri=http://localhost:80/status'
        ports:
        - containerPort: 9113
EOF
```

### **Expose Metrics Service**
```sh
kubectl expose deploy demo-app --name=demo-app-metrics --port=9113 --target-port=9113
```

---

## **2️⃣ Install Prometheus (Metrics Collector)**
We’ll use **Helm** for easy installation.

### **Add Prometheus Helm Repo**
```sh
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

### **Install Prometheus**
```sh
helm install prometheus prometheus-community/prometheus \
  --set server.service.type=NodePort \
  --set server.persistentVolume.enabled=false
```

### **Verify Prometheus is Scraping Metrics**
```sh
kubectl port-forward svc/prometheus-server 9090
```
Open **http://localhost:9090** → Check **Targets** (`demo-app-metrics:9113` should be **UP**).

---

## **3️⃣ Install Prometheus Adapter (Custom Metrics API)**
This converts Prometheus metrics → Kubernetes Custom Metrics API.

### **Install Prometheus Adapter**
```sh
helm install prometheus-adapter prometheus-community/prometheus-adapter \
  --set prometheus.url=http://prometheus-server \
  --set prometheus.port=80
```

### **Verify Custom Metrics API**
```sh
kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta1" | jq .
```
*(You should see `nginx_http_requests_total` and other Prometheus metrics.)*

---

## **4️⃣ Configure HPA to Scale on Custom Metrics**
We’ll create an **HPA that scales when `nginx_http_requests_total` > 10 RPS per pod**.

### **Apply HPA**
```sh
kubectl apply -f - <<EOF
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: demo-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: demo-app
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Pods
    pods:
      metric:
        name: nginx_http_requests_total
      target:
        type: AverageValue
        averageValue: 10
EOF
```

### **Check HPA Status**
```sh
kubectl get hpa -w
```
*(Initially shows `<unknown>`. Wait ~2 mins for metrics to populate.)*

---

## **5️⃣ Generate Traffic to Trigger Scaling**
Simulate HTTP requests to increase the metric.

### **Run a Load Generator**
```sh
kubectl run -it --rm load-generator --image=busybox -- /bin/sh -c "while true; do wget -q -O- http://demo-app:80; done"
```

### **Watch HPA Scale Up**
```sh
watch kubectl get hpa
```
*(After ~1-2 mins, `TARGETS` should increase, and `REPLICAS` should scale up!)*

---

## **🔍 Troubleshooting**
| Issue | Fix |
|--------|------|
| **HPA shows `<unknown>`** | Check `prometheus-adapter` logs: `kubectl logs -f <prometheus-adapter-pod>` |
| **No metrics in Prometheus** | Check `http://localhost:9090/targets` |
| **HPA not scaling** | Verify metric name: `kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta1"` |

---

## **📌 Key Takeaways**
✅ **Custom Metrics Server** (Prometheus Adapter) enables **HPA scaling on any metric** (not just CPU/memory).  
✅ **Prometheus** collects metrics, **Prometheus Adapter** exposes them to Kubernetes.  
✅ **HPA + Custom Metrics** = **Autoscaling based on real-world needs** (traffic, queues, business logic).  

---

