## **CRDs (Custom Resource Definitions)** in Kubernetes.

This explanation will include:

* ✅ What is a CRD in Kubernetes?
* ✅ How CRD fits into the Kubernetes architecture
* ✅ Real-world use case
* ✅ Step-by-step working behind the scenes
* ✅ Complete YAML examples (CRD + CR)
* ✅ Custom Controller explanation (how logic is applied)
* ✅ Why & when to use CRDs in production

---

## 📘 What is a CRD (Custom Resource Definition)?

### ✳️ CRD is a way to **extend Kubernetes** with **your own types**.

Just like Kubernetes has built-in types like:

* `Pod`
* `Deployment`
* `Service`

You can **define your own type**, like:

* `CronTab`
* `BackupJob`
* `KafkaCluster`
* `Database`

These are called **Custom Resources (CRs)**, and they are made possible through a **CRD**, which defines the schema and behavior of that resource.

> ✅ Think of a CRD as **adding a new API type** into Kubernetes.

---

### 💡 Why CRD?

Kubernetes was designed to be **extensible** — rather than adding everything to core, it allows developers to define their **own objects**, and control how they behave.

You define:

* What the resource looks like (`spec`)
* Optionally, create a controller that watches it and takes action

---

## 🏗️ How CRD fits in the Kubernetes Architecture?

```
               +----------------------+
               |     kubectl apply    |
               |     crontab.yaml     |
               +----------+-----------+
                          |
                 +--------v--------+
                 |   kube-apiserver |
                 +--------+--------+
                          |
                 +--------v--------+
                 |      etcd       |
                 +--------+--------+
                          |
                 +--------v--------+
                 | Custom Controller|
                 | (your logic)     |
                 +------------------+
```

<img width="1617" height="967" alt="image" src="https://github.com/user-attachments/assets/e114e0db-de38-4cf7-b822-ccef1cb9186e" />


* You create a new **CRD** (`kind: CustomResourceDefinition`)
* The API server now understands a new type (e.g., `crontabs.stable.example.com`)
* You can now `kubectl get crontabs`
* A custom controller can **watch for changes** to these objects and act accordingly

---

## ✅ Real-World Use Case: Scheduled Backup System

Let's say you're running a database and want to create a **custom Kubernetes resource** to manage backups.

Instead of writing bash scripts or external cron jobs, you want to:

* Define a new resource: `BackupJob`
* Specify schedule, storage location, and backup type
* Let a controller pick it up and create Pods to perform backup

---

## 🔧 Step-by-Step CRD Example: `CronTab`

We’ll simulate a real-world cron system using a custom resource.

---

### 1. Define the CRD (YAML)

```yaml
# crontab-crd.yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: crontabs.stable.example.com
spec:
  group: stable.example.com
  names:
    kind: CronTab
    plural: crontabs
    singular: crontab
    shortNames:
      - ct
  scope: Namespaced
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                cronSpec:
                  type: string
                image:
                  type: string
                replicas:
                  type: integer
```

---

### 2. Apply the CRD

```bash
kubectl apply -f crontab-crd.yaml
```

Kubernetes now knows a new type called `CronTab`.

Try:

```bash
kubectl get crontabs
```

---

### 3. Define a Custom Resource (CR)

```yaml
# crontab-cr.yaml
apiVersion: stable.example.com/v1
kind: CronTab
metadata:
  name: backup-cron
spec:
  cronSpec: "*/5 * * * *"
  image: busybox
  replicas: 2
```

Apply it:

```bash
kubectl apply -f crontab-cr.yaml
```

---

### 4. Build a Custom Controller (logic engine)

You can write this in Go, Python, or use tools like **Kubebuilder** or **Operator SDK**.

Here’s a **basic Python controller** using the `kubernetes` client:

```python
from kubernetes import client, config, watch

config.load_kube_config()
crd_api = client.CustomObjectsApi()

while True:
    stream = watch.Watch().stream(
        crd_api.list_namespaced_custom_object,
        group="stable.example.com",
        version="v1",
        namespace="default",
        plural="crontabs"
    )

    for event in stream:
        obj = event['object']
        spec = obj['spec']
        name = obj['metadata']['name']
        cron = spec['cronSpec']
        image = spec['image']
        replicas = spec['replicas']

        print(f"[{event['type']}] {name} → Schedule: {cron} → {image} × {replicas}")
        # Logic: create Jobs or Pods for backup if needed
```

This is a **controller loop** that:

* Watches for changes to `crontabs`
* Extracts spec fields
* Can take actions like:

  * Creating a `CronJob`
  * Running a `Pod`
  * Notifying external systems

---

## 💡 Production-Grade Use Case: **KubeDB, Prometheus Operator, ArgoCD**

* Tools like **KubeDB** allow DB management using CRDs:

  ```yaml
  kind: Postgres
  apiVersion: kubedb.com/v1alpha1
  spec:
    version: "13"
    storage:
      size: 10Gi
      class: gp2
  ```

* Tools like **Prometheus Operator** define:

  ```yaml
  kind: ServiceMonitor
  apiVersion: monitoring.coreos.com/v1
  ```

These tools:

* Define CRDs
* Provide controllers/operators that interpret them
* Abstract away complexity from end-users

---

## ✅ Benefits of CRDs

| Feature                    | Benefit                           |
| -------------------------- | --------------------------------- |
| Native kubectl support     | `kubectl get <your-resource>`     |
| API-based control          | Supports GitOps, CI/CD            |
| Schema enforcement         | Validates inputs                  |
| Namespaced or cluster-wide | Scoped control                    |
| Combine with controllers   | Implement your own platform logic |

---

## 📁 Folder Structure (Best Practice)

```
my-crd-project/
├── crds/
│   ├── crontab-crd.yaml
│   └── crontab-cr.yaml
├── controller/
│   └── crontab-controller.py
├── Dockerfile
└── README.md
```

You can Dockerize the controller and run it as a Deployment.

---

## 🧪 Testing

```bash
kubectl apply -f crds/crontab-crd.yaml
kubectl apply -f crds/crontab-cr.yaml
kubectl logs -f deployment/crontab-controller
```

You should see the controller detecting changes and acting.

---

## 🔚 Summary

* **CRDs = Custom API Types**
* Enable **domain-specific Kubernetes objects**
* Combine with controllers to make **custom operators**
* Used in real-world tools like ArgoCD, KubeDB, Prometheus Operator

---
Perfect Deepak 👌

Let’s build a **complete working example** of a **Kubernetes Custom Resource + Controller**, package it into a container, and deploy it as a Kubernetes `Deployment`.

We’ll use **Python** to keep it simple and understandable, and later you can enhance it with Go or Operator SDK.

---

## 💡 Use Case: `CronTab` Resource that Creates Echo Pods on a Schedule

We’ll define:

* A **CRD** named `CronTab`
* A **Custom Resource** (CR) named `hello-cron`
* A **Python Controller** that watches for this resource and creates a **Job**
* A **Docker image** to package the controller
* A **Kubernetes Deployment** to run the controller in-cluster

---

## ✅ 1. Create CRD YAML

```yaml
# crontab-crd.yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: crontabs.stable.deepak.com
spec:
  group: stable.deepak.com
  names:
    kind: CronTab
    plural: crontabs
    singular: crontab
  scope: Namespaced
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                cronSpec:
                  type: string
                message:
                  type: string
```

Apply:

```bash
kubectl apply -f crontab-crd.yaml
```

---

## ✅ 2. Create a Sample Custom Resource (CR)

```yaml
# crontab-cr.yaml
apiVersion: stable.deepak.com/v1
kind: CronTab
metadata:
  name: hello-cron
spec:
  cronSpec: "*/2 * * * *"
  message: "Hello from Deepak's controller!"
```

Apply:

```bash
kubectl apply -f crontab-cr.yaml
```

---

## ✅ 3. Python Controller Logic (crontab-controller.py)

```python
from kubernetes import client, config, watch
import time
import os

def create_cronjob(cron_name, cron_expr, msg):
    batch_v1 = client.BatchV1beta1Api()
    body = client.V1beta1CronJob(
        metadata=client.V1ObjectMeta(name=f"{cron_name}-job"),
        spec=client.V1beta1CronJobSpec(
            schedule=cron_expr,
            job_template=client.V1JobTemplateSpec(
                spec=client.V1JobSpec(
                    template=client.V1PodTemplateSpec(
                        spec=client.V1PodSpec(
                            restart_policy="OnFailure",
                            containers=[
                                client.V1Container(
                                    name="echo",
                                    image="busybox",
                                    args=["/bin/sh", "-c", f"echo {msg}"]
                                )
                            ]
                        )
                    )
                )
            )
        )
    )

    try:
        batch_v1.create_namespaced_cron_job(namespace="default", body=body)
        print(f"✅ Created CronJob: {cron_name}-job")
    except Exception as e:
        print(f"⚠️ Failed to create job: {e}")

def main():
    config.load_incluster_config() if os.getenv("KUBERNETES_SERVICE_HOST") else config.load_kube_config()
    api = client.CustomObjectsApi()

    w = watch.Watch()
    print("🚀 Watching CronTab custom resources...")
    for event in w.stream(api.list_namespaced_custom_object,
                          group="stable.deepak.com",
                          version="v1",
                          namespace="default",
                          plural="crontabs"):
        cr = event['object']
        etype = event['type']
        name = cr['metadata']['name']
        cronSpec = cr['spec']['cronSpec']
        message = cr['spec']['message']

        if etype == 'ADDED':
            print(f"📥 Detected new CronTab: {name}")
            create_cronjob(name, cronSpec, message)

if __name__ == "__main__":
    main()
```

---

## ✅ 4. Dockerfile

```Dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY crontab-controller.py .
RUN pip install kubernetes

CMD ["python", "crontab-controller.py"]
```

---

## ✅ 5. Build & Push Docker Image

```bash
docker build -t deepakdevops/crontab-controller:latest .
docker push deepakdevops/crontab-controller:latest
```

> Replace with your Docker Hub username.

---

## ✅ 6. Kubernetes Deployment YAML

```yaml
# controller-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crontab-controller
spec:
  replicas: 1
  selector:
    matchLabels:
      app: crontab-controller
  template:
    metadata:
      labels:
        app: crontab-controller
    spec:
      containers:
      - name: controller
        image: deepakdevops/crontab-controller:latest
        imagePullPolicy: Always
```

Deploy:

```bash
kubectl apply -f controller-deployment.yaml
```

---

## ✅ 7. Test

```bash
kubectl get cronjobs
kubectl get pods
kubectl logs deployment/crontab-controller
```

You should see:

* Your controller reacting to the CR
* A new `CronJob` created with the message printed every 2 minutes

---

## 📌 Summary

| File                         | Purpose                           |
| ---------------------------- | --------------------------------- |
| `crontab-crd.yaml`           | Registers the new `CronTab` kind  |
| `crontab-cr.yaml`            | A custom instance (CR)            |
| `crontab-controller.py`      | Watches CRs and takes action      |
| `Dockerfile`                 | Packages controller               |
| `controller-deployment.yaml` | Runs the controller in Kubernetes |

---
