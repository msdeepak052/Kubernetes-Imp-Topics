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

# 🚀 Complete Kubernetes Admission Webhook Setup

## 📁 Final Repository Structure

```
k8s-admission-webhook/
├── README.md
├── Dockerfile
├── validate-pod.py
├── tls/
│   ├── csr.conf
│   ├── tls.crt
│   └── tls.key
├── deployment.yaml
├── service.yaml
├── validating-webhook.yaml
├── test-pods/
│   ├── bad-pod.yaml
│   └── good-pod.yaml
└── deploy.sh
```

---

## 1️⃣ Complete File Contents

### **📄 Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY validate-pod.py /app/
COPY tls/ /certs/

RUN chmod 644 /certs/tls.crt /certs/tls.key

RUN pip install flask

EXPOSE 8443

CMD ["python3", "validate-pod.py"]
```

### **📄 validate-pod.py**
```python
from flask import Flask, request, jsonify
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

@app.route('/validate', methods=['POST'])
def validate():
    try:
        req = request.get_json()
        logger.info(f"Received validation request")
        
        if not req or "request" not in req:
            return jsonify({
                "apiVersion": "admission.k8s.io/v1",
                "kind": "AdmissionReview",
                "response": {
                    "uid": "",
                    "allowed": False,
                    "status": {"message": "Invalid request"}
                }
            })
        
        uid = req["request"]["uid"]
        
        # Get pod metadata
        pod_metadata = req["request"]["object"].get("metadata", {})
        pod_namespace = pod_metadata.get("namespace", "")
        pod_name = pod_metadata.get("name", "")
        
        logger.info(f"Validating pod: {pod_name} in namespace: {pod_namespace}")
        
        # Skip validation for webhook's own namespace
        if pod_namespace == "webhook-demo":
            logger.info("Skipping validation for webhook-demo namespace")
            return jsonify({
                "apiVersion": "admission.k8s.io/v1",
                "kind": "AdmissionReview",
                "response": {
                    "uid": uid,
                    "allowed": True,
                    "status": {"message": "Skipped validation in webhook-demo namespace"}
                }
            })
        
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

        logger.info(f"Validation result: allowed={allowed}, message={msg}")
        
        response = {
            "apiVersion": "admission.k8s.io/v1",
            "kind": "AdmissionReview",
            "response": {
                "uid": uid, 
                "allowed": allowed, 
                "status": {"message": msg}
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error in validation: {str(e)}")
        return jsonify({
            "apiVersion": "admission.k8s.io/v1",
            "kind": "AdmissionReview",
            "response": {
                "uid": req.get("request", {}).get("uid", ""),
                "allowed": False,
                "status": {"message": f"Validation error: {str(e)}"}
            }
        })

if __name__ == '__main__':
    logger.info("Starting webhook server on port 8443")
    app.run(host='0.0.0.0', port=8443, ssl_context=('/certs/tls.crt', '/certs/tls.key'))
```

### **📄 tls/csr.conf**
```ini
[ req ]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
x509_extensions = v3_req

[ dn ]
CN = pod-validator.webhook-demo.svc

[ v3_req ]
keyUsage = keyEncipherment, dataEncipherment, digitalSignature
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = pod-validator
DNS.2 = pod-validator.webhook-demo
DNS.3 = pod-validator.webhook-demo.svc
DNS.4 = pod-validator.webhook-demo.svc.cluster.local
```

### **📄 deployment.yaml**
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
        image: devopsdktraining/pod-validator:2.0
        ports:
        - containerPort: 8443
        volumeMounts:
        - name: certs
          mountPath: /certs
          readOnly: true
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8443
            scheme: HTTPS
          initialDelaySeconds: 5
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8443
            scheme: HTTPS
          initialDelaySeconds: 5
          periodSeconds: 10
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
      volumes:
      - name: certs
        secret:
          secretName: webhook-certs
```

### **📄 service.yaml**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: pod-validator
  namespace: webhook-demo
spec:
  selector:
    app: pod-validator
  ports:
    - port: 8443
      targetPort: 8443
```

### **📄 validating-webhook.yaml**
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
        port: 8443
      caBundle: CA_BUNDLE_PLACEHOLDER
    admissionReviewVersions: ["v1"]
    sideEffects: None
    timeoutSeconds: 10
    namespaceSelector:
      matchExpressions:
        - key: kubernetes.io/metadata.name
          operator: NotIn
          values: [webhook-demo]
```

### **📄 test-pods/bad-pod.yaml**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: badpod
  labels:
    app: badpod
spec:
  containers:
  - name: nginx
    image: nginx:alpine
    resources:
      requests:
        memory: "64Mi"
        cpu: "50m"
      limits:
        memory: "128Mi"
        cpu: "100m"
```

### **📄 test-pods/good-pod.yaml**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: goodpod
  labels:
    app: goodpod
spec:
  containers:
  - name: nginx
    image: nginx:alpine
    securityContext:
      runAsNonRoot: true
      runAsUser: 1000
    resources:
      requests:
        memory: "64Mi"
        cpu: "50m"
      limits:
        memory: "128Mi"
        cpu: "100m"
```

### **📄 deploy.sh** (Automated Deployment Script)
```bash
#!/bin/bash

set -e

echo "🚀 Starting Kubernetes Admission Webhook Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: Generate TLS certificates
print_status "Step 1: Generating TLS certificates..."
mkdir -p tls

# Create CSR config
cat > tls/csr.conf << EOF
[ req ]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
x509_extensions = v3_req

[ dn ]
CN = pod-validator.webhook-demo.svc

[ v3_req ]
keyUsage = keyEncipherment, dataEncipherment, digitalSignature
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = pod-validator
DNS.2 = pod-validator.webhook-demo
DNS.3 = pod-validator.webhook-demo.svc
DNS.4 = pod-validator.webhook-demo.svc.cluster.local
EOF

# Generate certificates
openssl req -newkey rsa:2048 -nodes -keyout tls/tls.key \
  -x509 -days 365 -out tls/tls.crt -config tls/csr.conf

print_status "TLS certificates generated successfully."

# Step 2: Verify certificates
print_status "Step 2: Verifying certificates..."
openssl x509 -in tls/tls.crt -text -noout | grep -A 5 "Subject Alternative Name"

# Step 3: Create namespace
print_status "Step 3: Creating namespace..."
kubectl create namespace webhook-demo --dry-run=client -o yaml | kubectl apply -f -

# Step 4: Create TLS secret
print_status "Step 4: Creating TLS secret..."
kubectl delete secret webhook-certs -n webhook-demo --ignore-not-found=true
kubectl create secret tls webhook-certs \
  --namespace=webhook-demo \
  --cert=tls/tls.crt \
  --key=tls/tls.key

# Step 5: Build and push Docker image
print_status "Step 5: Building Docker image..."
docker build -t devopsdktraining/pod-validator:2.0 .
docker push devopsdktraining/pod-validator:2.0

# Step 6: Get CA bundle
print_status "Step 6: Generating CA bundle..."
CA_BUNDLE=$(cat tls/tls.crt | base64 | tr -d '\n')

# Step 7: Update validating webhook configuration
print_status "Step 7: Updating webhook configuration..."
cp validating-webhook.yaml validating-webhook-temp.yaml
if [[ "$OSTYPE" == "darwin"* ]]; then
    # MacOS
    sed -i "" "s|CA_BUNDLE_PLACEHOLDER|$CA_BUNDLE|" validating-webhook-temp.yaml
else
    # Linux
    sed -i "s|CA_BUNDLE_PLACEHOLDER|$CA_BUNDLE|" validating-webhook-temp.yaml
fi

# Step 8: Deploy webhook server (without webhook enabled first)
print_status "Step 8: Deploying webhook server..."
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Step 9: Wait for pod to be ready
print_status "Step 9: Waiting for webhook pod to be ready..."
if kubectl wait --for=condition=ready pod -l app=pod-validator -n webhook-demo --timeout=120s; then
    print_status "Webhook pod is ready."
else
    print_error "Webhook pod failed to start. Checking logs..."
    kubectl logs -n webhook-demo -l app=pod-validator
    exit 1
fi

# Step 10: Test webhook internally
print_status "Step 10: Testing webhook internally..."
kubectl exec -n webhook-demo deployment/pod-validator -- curl -k https://localhost:8443/health

# Step 11: Enable the webhook
print_status "Step 11: Enabling validating webhook..."
kubectl apply -f validating-webhook-temp.yaml

# Step 12: Clean up temporary file
rm -f validating-webhook-temp.yaml

# Step 13: Test the webhook
print_status "Step 13: Testing webhook with sample pods..."

print_status "Testing bad pod (should fail)..."
if kubectl apply -f test-pods/bad-pod.yaml 2>&1 | grep -q "denied"; then
    print_status "✅ Bad pod correctly rejected"
else
    print_error "❌ Bad pod was not rejected"
fi

print_status "Testing good pod (should succeed)..."
if kubectl apply -f test-pods/good-pod.yaml; then
    print_status "✅ Good pod correctly created"
else
    print_error "❌ Good pod creation failed"
fi

# Step 14: Final verification
print_status "Step 14: Final verification..."
kubectl get pods -n webhook-demo
kubectl get validatingwebhookconfiguration pod-validator

echo ""
print_status "🎉 Kubernetes Admission Webhook deployment completed successfully!"
echo ""
print_status "📋 Summary:"
print_status "  - Webhook server: Running in webhook-demo namespace"
print_status "  - ValidatingWebhookConfiguration: Enabled"
print_status "  - TLS certificates: Configured with proper SANs"
print_status "  - Tests: Bad pods rejected, good pods accepted"
echo ""
print_status "You can now test with your own pods!"
```

---

## 2️⃣ Complete Manual Deployment Steps

If you prefer manual deployment, here are the steps:

### **Step 1: Generate TLS Certificates**
```bash
chmod +x deploy.sh
./deploy.sh
```

### **OR Manual Steps:**

```bash
# 1. Create directory structure
mkdir -p k8s-admission-webhook/tls test-pods
cd k8s-admission-webhook

# 2. Create all the files as shown above

# 3. Generate TLS certificates
mkdir -p tls
cat > tls/csr.conf << 'EOF'
[ req ]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
x509_extensions = v3_req

[ dn ]
CN = pod-validator.webhook-demo.svc

[ v3_req ]
keyUsage = keyEncipherment, dataEncipherment, digitalSignature
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = pod-validator
DNS.2 = pod-validator.webhook-demo
DNS.3 = pod-validator.webhook-demo.svc
DNS.4 = pod-validator.webhook-demo.svc.cluster.local
EOF

openssl req -newkey rsa:2048 -nodes -keyout tls/tls.key \
  -x509 -days 365 -out tls/tls.crt -config tls/csr.conf

# 4. Create namespace
kubectl create namespace webhook-demo

# 5. Create TLS secret
kubectl create secret tls webhook-certs \
  --namespace=webhook-demo \
  --cert=tls/tls.crt \
  --key=tls/tls.key

# 6. Build and push image
docker build -t devopsdktraining/pod-validator:2.0 .
docker push devopsdktraining/pod-validator:2.0

# 7. Get CA bundle and update webhook config
CA_BUNDLE=$(cat tls/tls.crt | base64 | tr -d '\n')
sed "s|CA_BUNDLE_PLACEHOLDER|$CA_BUNDLE|" validating-webhook.yaml > validating-webhook-final.yaml

# 8. Deploy webhook server first
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# 9. Wait for pod to be ready
kubectl wait --for=condition=ready pod -l app=pod-validator -n webhook-demo --timeout=120s

# 10. Enable webhook
kubectl apply -f validating-webhook-final.yaml

# 11. Test
kubectl apply -f test-pods/bad-pod.yaml    # Should fail
kubectl apply -f test-pods/good-pod.yaml   # Should succeed
```
<img width="1147" height="249" alt="image" src="https://github.com/user-attachments/assets/3892580e-0bf6-4bed-b4aa-5565ba613e73" />

---

## 3️⃣ Verification Commands

```bash
# Check all resources
kubectl get all -n webhook-demo

# Check webhook configuration
kubectl get validatingwebhookconfiguration pod-validator -o yaml

# Check webhook logs
kubectl logs -n webhook-demo deployment/pod-validator

# Test webhook health
kubectl exec -n webhook-demo deployment/pod-validator -- curl -k https://localhost:8443/health

# Check events
kubectl get events -n webhook-demo --sort-by='.lastTimestamp'
```

---

## 4️⃣ Expected Output

**For bad-pod.yaml:**
```
Error from server: error when creating "test-pods/bad-pod.yaml": admission webhook "pod-validator.webhook-demo.svc" denied the request: Container 'nginx' must set runAsNonRoot=true
```

**For good-pod.yaml:**
```
pod/goodpod created
```

This complete setup ensures:
- ✅ Proper TLS certificates with SANs
- ✅ Webhook doesn't block its own deployment
- ✅ Proper error handling and logging
- ✅ Health checks and readiness probes
- ✅ Automated deployment script
- ✅ Comprehensive testing
- 
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

* The **webhook blocks pods running as root**.
* Using a **Docker image** removes hostPath and working dir issues.
* This setup is **production-ready**, portable, and versioned.
* You can extend it for other policies like **image repo restrictions**, **resource limits**, or **required labels**.

---









