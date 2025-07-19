# Operators in Kubernetes

In Kubernetes, **Operators** are powerful components that help you **automate the lifecycle of complex, stateful applications** (like databases, caches, etc.) in a Kubernetes-native way. They encapsulate the operational knowledge of managing an application and extend Kubernetes with **custom resources** and **custom controllers**.

---

## 🔧 What Are Operators in Kubernetes?

Operators are software extensions that **use custom resources (CRs)** to manage applications and their components. They are written using **controller patterns** and interact with the Kubernetes API just like native controllers (like Deployment, StatefulSet, etc.).

> 👉 An operator **watches** for changes in custom resources and **reacts** by taking actions (create/update/delete resources) to reconcile the current state with the desired state.

<img width="1458" height="820" alt="image" src="https://github.com/user-attachments/assets/876a3ebb-5563-4fad-ad44-5a6f296d1ac2" />

---

## 🧠 Why Do We Need Operators?

While Kubernetes does a great job of managing **stateless applications**, managing **stateful applications** (like databases, queues, or custom software) involves:

* Taking backups and restores
* Upgrading in a controlled way
* Scaling based on metrics
* Managing configurations and secrets
* Handling failovers

These tasks often require **human intervention or external automation scripts**. Operators encode these operational tasks into **Kubernetes-native constructs**, enabling:

* **Day-2 operations automation** (beyond deploy)
* **GitOps-style workflows**
* **Self-healing** custom logic
* **Full app lifecycle management** within Kubernetes

---

## 🆚 Operators vs Other Kubernetes Concepts

| Feature                      | Operators        | Helm Charts                    | StatefulSets           | Custom Controllers                      |
| ---------------------------- | ---------------- | ------------------------------ | ---------------------- | --------------------------------------- |
| Handles install/upgrade      | ✅                | ✅                              | ❌                      | ❌                                       |
| Custom resource definitions  | ✅                | ❌                              | ❌                      | ✅                                       |
| Reconciles continuously      | ✅                | ❌ (only during `helm upgrade`) | ✅ (limited)            | ✅                                       |
| Day-2 ops (backup, failover) | ✅                | ❌                              | ❌                      | ✅ (if coded)                            |
| Encodes domain knowledge     | ✅                | ❌                              | ❌                      | ✅                                       |
| Example use                  | MongoDB Operator | Helm chart for NGINX           | PostgreSQL StatefulSet | CR controller for custom business logic |

Operators are more **intelligent** and **customizable** than Helm or plain manifests.

---

## 🧰 Use Cases of Operators

1. **Database management**

   * MongoDB, PostgreSQL, MySQL, Redis
   * Backup, restore, scaling, upgrade

2. **Big Data tools**

   * Kafka, Cassandra, Elasticsearch
   * Partition management, rebalancing, cluster scaling

3. **Custom Business Applications**

   * Complex microservices with interdependencies
   * Reconciliation logic specific to internal workflows

4. **CI/CD systems**

   * ArgoCD Operator
   * Automate GitOps deployment pipelines

---

## ⚙️ Components of an Operator

1. **Custom Resource Definition (CRD)**

   * Defines a new resource type like `CronTab`, `MongoDB`, etc.

2. **Custom Resource (CR)**

   * An actual instance of the custom type, e.g., `mongo-db.yaml`.

3. **Controller**

   * Watches the CRs and takes action to make actual resources match the desired state.

---

## ✅ Example: Writing a Simple Operator

Let’s say we want to manage a `CronTab` custom resource.

### Step 1: Define CRD

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: crontabs.stable.example.com
spec:
  group: stable.example.com
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
                schedule:
                  type: string
                image:
                  type: string
  scope: Namespaced
  names:
    plural: crontabs
    singular: crontab
    kind: CronTab
    shortNames:
    - ct
```

### Step 2: Install the CRD

```bash
kubectl apply -f crd.yaml
```

---

### Step 3: Create a CR (Instance)

```yaml
apiVersion: stable.example.com/v1
kind: CronTab
metadata:
  name: sample-cron
spec:
  schedule: "* * * * *"
  image: busybox
```

```bash
kubectl apply -f cr.yaml
```

---

### Step 4: Operator Controller Logic (Python Example with `kubernetes` client)

```python
from kubernetes import client, config, watch

def main():
    config.load_incluster_config()
    api = client.CustomObjectsApi()
    batch_v1 = client.BatchV1Api()
    w = watch.Watch()
    for event in w.stream(api.list_namespaced_custom_object,
                          group="stable.example.com",
                          version="v1",
                          namespace="default",
                          plural="crontabs"):
        cr = event['object']
        name = cr['metadata']['name']
        spec = cr['spec']
        print(f"🚀 Watching CR: {name}, Schedule: {spec['schedule']}")

        # Create CronJob based on CR
        job = client.V1CronJob(
            metadata=client.V1ObjectMeta(name=name),
            spec=client.V1CronJobSpec(
                schedule=spec['schedule'],
                job_template=client.V1JobTemplateSpec(
                    spec=client.V1JobSpec(
                        template=client.V1PodTemplateSpec(
                            spec=client.V1PodSpec(
                                containers=[
                                    client.V1Container(
                                        name="main",
                                        image=spec['image'],
                                        args=["/bin/sh", "-c", "date; echo Hello"]
                                    )
                                ],
                                restart_policy="OnFailure"
                            )
                        )
                    )
                )
            )
        )
        batch_v1.create_namespaced_cron_job(namespace="default", body=job)

main()
```

---

### Step 5: Package and Deploy the Operator

* Dockerize the Python script
* Deploy using a Deployment manifest
* Provide a ServiceAccount with necessary RBAC

```bash
kubectl apply -f deployment.yaml
```

---

## 📦 Tools for Building Operators

1. **Operator SDK** (Go, Ansible, Helm based)

   * Developed by RedHat (used for most OpenShift Operators)
   * CLI: `operator-sdk init`, `operator-sdk create api`

2. **Kubebuilder** (Go based)

   * Framework to build operators natively using Go and CRDs

3. **Metacontroller** (JSON-based logic for dynamic controllers)

4. **Kopf (Kubernetes Operator Pythonic Framework)**

   * Python-based, easier to get started
   * Example:

     ```python
     import kopf
     @kopf.on.create('stable.example.com', 'v1', 'crontabs')
     def create_fn(spec, **kwargs):
         print(f"Creating cron job with schedule {spec['schedule']}")
     ```

---

## 🧪 Real-World Operator Examples

| Operator                   | Function                                   |
| -------------------------- | ------------------------------------------ |
| **MongoDB Operator**       | Scales clusters, manages backups, restores |
| **Prometheus Operator**    | Manages Prometheus & Alertmanager CRDs     |
| **Kafka Operator**         | Automates brokers, topics, zookeepers      |
| **ArgoCD Operator**        | Automates GitOps CD pipelines              |
| **ElasticSearch Operator** | Handles node scaling, upgrades, monitoring |

---

## 🧵 Summary

* **Operators = CRDs + Controllers** to manage complex apps
* Provide **declarative, Kubernetes-native lifecycle management**
* Ideal for **stateful apps and custom automation**
* Built using SDKs like `Operator SDK`, `Kubebuilder`, or `Kopf`
* Enable **day-2 operations** in CI/CD, databases, monitoring, etc.

---

Here's a complete hands‑on walkthrough with **cert‑manager** (the Kubernetes Operator) — from installation to issuing TLS certificates using real YAML files:

---

## 🌐 1. Install cert‑manager with CRDs

You can install cert‑manager using Helm. This automatically installs the CRDs (CustomResourceDefinitions) that cert‑manager uses (e.g. `Certificate`, `Issuer`, `ClusterIssuer`):

```bash
# Ensure the namespace exists
kubectl create namespace cert-manager

# Add Jetstack Helm repo
helm repo add jetstack https://charts.jetstack.io
helm repo update

# Install cert-manager including CRDs
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --version v1.16.5 \
  --set installCRDs=true
```

After a minute, verify it's running:

```bash
kubectl get pods -n cert-manager
```

You should see pods like `cert-manager-...`, `cainjector-...`, `webhook-...` running ([cert-manager.io][1], [f5.com][2], [min.io][3], [docs.redhat.com][4]).

---

## 2. Create a **ClusterIssuer** (Let's Encrypt staging)

This defines how certificates are issued cluster-wide. Save as `clusterissuer-staging.yaml`:

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
spec:
  acme:
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-staging
    solvers:
      - http01:
          ingress:
            class: nginx
```

Apply it:

```bash
kubectl apply -f clusterissuer-staging.yaml
```

---

## 3. Create an **Issuer** scoped to a namespace

Useful if you want namespace-level issuers. Save as `issuer-dev.yaml`:

```yaml
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: dev-issuer
  namespace: dev
spec:
  acme:
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: dev-letsencrypt
    solvers:
      - http01:
          ingress:
            class: nginx
```

```bash
kubectl create namespace dev
kubectl apply -f issuer-dev.yaml
```

---

## 4. Request a **Certificate** via cert‑manager

Set up TLS for an Ingress in `dev` namespace. Save as `certificate.yaml`:

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: example-tls
  namespace: dev
spec:
  secretName: example-tls-secret
  dnsNames:
    - example.dev.yourdomain.com
  issuerRef:
    name: dev-issuer
    kind: Issuer
```

Apply:

```bash
kubectl apply -f certificate.yaml
```

cert‑manager will:

1. Detect the new `Certificate` object.
2. Use the `Issuer` solver to complete the ACME challenge.
3. Store the issued cert + key in the `example-tls-secret` Secret.

---

## 5. Use the TLS secret in an Ingress

For a service running `app.dev.svc`, you can reference the secret:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  namespace: dev
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-staging"
spec:
  tls:
  - hosts:
    - example.dev.yourdomain.com
    secretName: example-tls-secret
  rules:
  - host: example.dev.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app
            port:
              number: 80
```

Deploy and watch:

```bash
kubectl apply -f ingress.yaml
kubectl describe certificate example-tls -n dev
kubectl get secret example-tls-secret -n dev
```

---

## 🧠 What's happening behind the scenes?

* **CRDs** define new resource types: `Certificate`, `Issuer`, etc. ([cert-manager.io][5], [docs.redhat.com][4], [github.com][6])
* You create **CRs** (Issuer, Certificate), which are declarative desired states.
* The **cert‑manager Operator** (custom controller) watches these CRs and automatically reconciles them by managing Ingress objects, Secrets, ACME solver pods, and retries until successful.

---

## 💡 Common Variations

* Use a **ClusterIssuer** if you want cross-namespace scope.
* Switch `solvers` to DNS‑01 for wildcard certs.
* Use production Let’s Encrypt by changing ACME server to `https://…/v02/api…/directory`.
* Employ the **cert-manager Operator on OpenShift** — installed via OLM, managing the cert‑manager lifecycle ([docs.redhat.com][4]).

---

## ✅ Validation & Troubleshooting

Check status:

```bash
kubectl describe certificate example-tls -n dev
kubectl logs -l app=webhook -n cert-manager
```

Logs offer rich insights into ACME challenges and retries.

---

## 🔚 Summary

This hands‑on guide showed you:

1. How to install cert‑manager (Operator + CRDs).
2. Define Issuer/ClusterIssuer and Certificate CRs.
3. Automate TLS for Ingress using cert‑manager logic.

Let me know if you'd like to explore DNS‑01 challenges, wildcard certs, or integration with Vault!

[1]: https://cert-manager.io/v1.1-docs/installation/kubernetes/?utm_source=chatgpt.com "Kubernetes - cert-manager Documentation"
[2]: https://www.f5.com/company/blog/nginx/automating-certificate-management-in-a-kubernetes-environment?utm_source=chatgpt.com "Automating Certificate Management in a Kubernetes Environment"
[3]: https://min.io/docs/minio/kubernetes/upstream/operations/cert-manager/cert-manager-operator.html?utm_source=chatgpt.com "cert-manager for Operator — MinIO Object Storage for Kubernetes"
[4]: https://docs.redhat.com/en/documentation/openshift_container_platform/4.14/html/security_and_compliance/cert-manager-operator-for-red-hat-openshift?utm_source=chatgpt.com "Chapter 9. cert-manager Operator for Red Hat OpenShift | 4.14"
[5]: https://cert-manager.io/docs/tutorials/?utm_source=chatgpt.com "Tutorials - cert-manager Documentation"
[6]: https://github.com/openshift/cert-manager-operator?utm_source=chatgpt.com "OpenShift Cert-Manager Operator - GitHub"

