## 🌐 1. What are Admission Controllers?

In Kubernetes, **Admission Controllers** are plugins that **intercept requests** to the API server **after authentication and authorization**, but **before objects are persisted** in etcd.

### 🧩 In short:

* They act as **“gatekeepers”** that can *validate*, *modify*, or *reject* API requests.
* They ensure **policies, security, and compliance** are enforced automatically.

---

## ⚙️ 2. Flow of a Kubernetes API Request

When you submit something (e.g., `kubectl apply -f pod.yaml`), here’s what happens:

```
kubectl → API Server
  → Authentication
  → Authorization
  → Admission Controllers
       ├─ Mutating Admission Controllers (can modify request)
       └─ Validating Admission Controllers (can validate or deny)
  → etcd (persistent store)
```
<img width="1473" height="520" alt="image" src="https://github.com/user-attachments/assets/269cd592-c479-4451-922c-7856d765ff68" />
<img width="1591" height="513" alt="image" src="https://github.com/user-attachments/assets/63745d24-8684-4120-afe0-36d0e5752f1a" />

---

## 🧠 3. Why were Admission Controllers needed?

### 🔴 Without Admission Controllers:

* Kubernetes would accept *any* valid YAML as long as it passes syntax and RBAC.
* Example:

  * A user could deploy containers as `root`.
  * A pod could mount host paths (`/etc`, `/var/run/docker.sock`).
  * Teams could use arbitrary images from the internet.
  * Namespaces could exceed resource quotas.
* There’s **no automatic guardrail**.

### ✅ With Admission Controllers:

* We can enforce policies **centrally**:

  * Prevent privilege escalation.
  * Enforce image repositories.
  * Add default labels or sidecars.
  * Validate required fields.
  * Inject secrets, certificates, or configurations.

---

## 🧩 4. Types of Admission Controllers

| Type           | Description                                             | Example                             |
| -------------- | ------------------------------------------------------- | ----------------------------------- |
| **Mutating**   | Can modify incoming requests before they are persisted. | Add default labels, inject sidecars |
| **Validating** | Only validate — can accept or reject requests.          | Reject pods running as root         |

---

## 🧰 5. Common Built-in Admission Controllers

Kubernetes has many built-ins (enabled by default on most clusters):

| Controller                                                | Purpose                                                         |
| --------------------------------------------------------- | --------------------------------------------------------------- |
| `NamespaceLifecycle`                                      | Prevent deletion of active namespaces                           |
| `LimitRanger`                                             | Enforce default CPU/memory limits                               |
| `ResourceQuota`                                           | Enforce quotas per namespace                                    |
| `PodSecurity`                                             | Enforce Pod Security Standards (Restricted/Baseline/Privileged) |
| `MutatingAdmissionWebhook` / `ValidatingAdmissionWebhook` | Allow custom admission logic via webhooks                       |

---

## 💡 6. Real-Life Demo: **Prevent Pods Running as Root**

### 🎯 Goal:

In many enterprises, **running containers as root is prohibited** for security compliance.
We’ll enforce this using a **Validating Admission Webhook**.

---

## 🧩 7. Demo Setup — Step by Step

> You can perform this in Minikube, Kind, or EKS (with permissions).

---

### **Step 1: Create a Validation Webhook Server**

We’ll write a small webhook server that checks if a Pod’s `securityContext.runAsNonRoot=true`.
If not, the request will be **denied**.

📁 `validate-pod.py`

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/validate', methods=['POST'])
def validate():
    req = request.get_json()
    uid = req["request"]["uid"]
    allowed = True
    msg = "Pod is valid"
    pod_spec = req["request"]["object"]["spec"]
    containers = pod_spec.get("containers", [])

    for c in containers:
        sc = c.get("securityContext", {})
        if not sc.get("runAsNonRoot", False):
            allowed = False
            msg = f"Container '{c['name']}' must set runAsNonRoot=true"
            break

    response = {
        "apiVersion": "admission.k8s.io/v1",
        "kind": "AdmissionReview",
        "response": {"uid": uid, "allowed": allowed, "status": {"message": msg}}
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443, ssl_context=('tls.crt', 'tls.key'))
```

---

### **Step 2: Create TLS Certificate for the Webhook**

```bash
# Create namespace
kubectl create ns webhook-demo

# Create certs
openssl req -newkey rsa:2048 -nodes -keyout tls.key -x509 -days 365 -out tls.crt -subj "/CN=pod-validator.webhook-demo.svc"
kubectl create secret tls webhook-tls --cert=tls.crt --key=tls.key -n webhook-demo
```

---

### **Step 3: Deploy the Webhook Server**

📁 `deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pod-validator
  namespace: webhook-demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: pod-validator
  template:
    metadata:
      labels:
        app: pod-validator
    spec:
      containers:
      - name: validator
        image: python:3.9
        command: ["python3", "-u", "validate-pod.py"]
        volumeMounts:
        - name: webhook-code
          mountPath: /app
        - name: tls-certs
          mountPath: /certs
        workingDir: /app
      volumes:
      - name: webhook-code
        hostPath:
          path: /path/to/code  # adjust path
      - name: tls-certs
        secret:
          secretName: webhook-tls
---
apiVersion: v1
kind: Service
metadata:
  name: pod-validator
  namespace: webhook-demo
spec:
  ports:
  - port: 443
    targetPort: 443
  selector:
    app: pod-validator
```

---

### **Step 4: Create the ValidatingWebhookConfiguration**

📁 `validating-webhook.yaml`

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: pod-validator
webhooks:
  - name: pod-validator.webhook-demo.svc
    rules:
      - apiGroups: [""]
        apiVersions: ["v1"]
        operations: ["CREATE"]
        resources: ["pods"]
    clientConfig:
      service:
        name: pod-validator
        namespace: webhook-demo
        path: "/validate"
      caBundle: <BASE64_ENCODED_CA_CERT>
    admissionReviewVersions: ["v1"]
    sideEffects: None
```

> Replace `<BASE64_ENCODED_CA_CERT>` with:
> `cat tls.crt | base64 | tr -d '\n'`

---

### **Step 5: Test the Policy**

#### 🚫 Pod without runAsNonRoot

📁 `bad-pod.yaml`

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: badpod
spec:
  containers:
  - name: nginx
    image: nginx
```

Apply it:

```bash
kubectl apply -f bad-pod.yaml
```

➡️ Result:

```
Error from server (Container 'nginx' must set runAsNonRoot=true)
```

#### ✅ Pod with runAsNonRoot

📁 `good-pod.yaml`

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: goodpod
spec:
  containers:
  - name: nginx
    image: nginx
    securityContext:
      runAsNonRoot: true
```

Apply it:

```bash
kubectl apply -f good-pod.yaml
```

➡️ Result:

```
pod/goodpod created
```

---

## 🔐 8. Real-World Impact

This webhook:

* Enforces **security policy** cluster-wide.
* Prevents **human error or negligence**.
* Acts as a **guardrail** to meet compliance (like CIS Benchmarks).

**Without it** → Developers might unknowingly deploy insecure workloads.
**With it** → Security is enforced automatically.

---

## 🚀 9. Summary

| Concept               | Purpose                                                 |
| --------------------- | ------------------------------------------------------- |
| Admission Controllers | Enforce rules before persisting to etcd                 |
| Mutating              | Modify requests (e.g., inject defaults)                 |
| Validating            | Approve or reject requests                              |
| Real-life need        | Enforce security, compliance, labeling, resource limits |
| Demo outcome          | Prevent running pods as root automatically              |

---


