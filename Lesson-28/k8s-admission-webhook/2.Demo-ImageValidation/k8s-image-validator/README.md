# 🚀 Real-Life Example: **Image Registry Validator Webhook**

A production-grade webhook that enforces:
- ✅ Only allow images from approved registries
- ✅ Block latest tags
- ✅ Require resource limits
- ✅ Enforce specific security contexts

---

## 📁 Complete Repository Structure

```
k8s-image-validator/
├── README.md
├── Dockerfile
├── image-validator.py
├── tls/
│   ├── csr.conf
│   ├── tls.crt
│   └── tls.key
├── deployment.yaml
├── service.yaml
├── validating-webhook.yaml
├── configmap.yaml
├── test-pods/
│   ├── bad-pod-1.yaml (unapproved registry)
│   ├── bad-pod-2.yaml (latest tag)
│   ├── bad-pod-3.yaml (no resources)
│   └── good-pod.yaml
└── deploy.sh
```

---

## 1️⃣ Complete File Contents

### **📄 Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY image-validator.py /app/
COPY tls/ /certs/

RUN pip install flask

EXPOSE 8443

CMD ["python3", "image-validator.py"]
```

### **📄 image-validator.py** (Main Webhook Logic)
```python
from flask import Flask, request, jsonify
import logging
import os
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration - In production, this would come from ConfigMap
APPROVED_REGISTRIES = [
    "docker.io",
    "gcr.io",
    "k8s.gcr.io",
    "quay.io",
    "registry.k8s.io",
    "ghcr.io"
]

BLOCKED_TAGS = ["latest"]

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "status": "healthy", 
        "message": "Image Validator Webhook is running",
        "version": "1.0.0"
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

@app.route('/validate', methods=['POST'])
def validate():
    try:
        req = request.get_json()
        logger.info("Received pod validation request")
        
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
        if pod_namespace == "image-validator-demo":
            logger.info("Skipping validation for image-validator-demo namespace")
            return jsonify({
                "apiVersion": "admission.k8s.io/v1",
                "kind": "AdmissionReview",
                "response": {
                    "uid": uid,
                    "allowed": True,
                    "status": {"message": "Skipped validation in image-validator-demo namespace"}
                }
            })
        
        pod_spec = req["request"]["object"]["spec"]
        containers = pod_spec.get("containers", [])
        init_containers = pod_spec.get("initContainers", [])
        
        all_containers = containers + init_containers
        
        # Validate each container
        validation_errors = []
        
        for container in all_containers:
            container_name = container.get("name", "unknown")
            image = container.get("image", "")
            
            # Check 1: Image registry validation
            registry_approved, registry_msg = validate_image_registry(image, container_name)
            if not registry_approved:
                validation_errors.append(registry_msg)
            
            # Check 2: Block latest tags
            tag_blocked, tag_msg = validate_image_tag(image, container_name)
            if tag_blocked:
                validation_errors.append(tag_msg)
            
            # Check 3: Resource limits
            resources_valid, resources_msg = validate_resources(container, container_name)
            if not resources_valid:
                validation_errors.append(resources_msg)
            
            # Check 4: Security context
            security_valid, security_msg = validate_security_context(container, container_name)
            if not security_valid:
                validation_errors.append(security_msg)
        
        if validation_errors:
            allowed = False
            msg = " | ".join(validation_errors)
            logger.warning(f"Pod validation failed: {msg}")
        else:
            allowed = True
            msg = "All validations passed"
            logger.info(f"Pod validation passed: {pod_name}")
        
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

def validate_image_registry(image, container_name):
    """Validate that image comes from approved registry"""
    if not image:
        return False, f"Container '{container_name}': Image is required"
    
    # Extract registry
    parts = image.split('/')
    if len(parts) > 1:
        registry = parts[0]
        if '.' in registry or ':' in registry:  # It's a registry with domain/port
            if registry not in APPROVED_REGISTRIES:
                return False, f"Container '{container_name}': Registry '{registry}' not in approved list: {APPROVED_REGISTRIES}"
    
    return True, ""

def validate_image_tag(image, container_name):
    """Validate that image doesn't use blocked tags"""
    if not image:
        return False, f"Container '{container_name}': Image is required"
    
    # Extract tag
    tag = "latest"  # default
    if ':' in image:
        tag = image.split(':')[-1]
    
    if tag in BLOCKED_TAGS:
        return True, f"Container '{container_name}': Tag '{tag}' is blocked. Use specific version tags."
    
    return False, ""

def validate_resources(container, container_name):
    """Validate that container has resource limits and requests"""
    resources = container.get("resources", {})
    
    errors = []
    
    # Check limits
    limits = resources.get("limits", {})
    if not limits.get("cpu"):
        errors.append("CPU limits")
    if not limits.get("memory"):
        errors.append("memory limits")
    
    # Check requests
    requests = resources.get("requests", {})
    if not requests.get("cpu"):
        errors.append("CPU requests")
    if not requests.get("memory"):
        errors.append("memory requests")
    
    if errors:
        return False, f"Container '{container_name}': Missing {', '.join(errors)}"
    
    return True, ""

def validate_security_context(container, container_name):
    """Validate security context settings"""
    security_context = container.get("securityContext", {})
    
    errors = []
    
    # Check for runAsNonRoot
    if not security_context.get("runAsNonRoot", False):
        errors.append("runAsNonRoot=true")
    
    # Check for allowPrivilegeEscalation
    if security_context.get("allowPrivilegeEscalation", True):
        errors.append("allowPrivilegeEscalation=false")
    
    # Check for readOnlyRootFilesystem
    if not security_context.get("readOnlyRootFilesystem", False):
        errors.append("readOnlyRootFilesystem=true")
    
    if errors:
        return False, f"Container '{container_name}': Required {', '.join(errors)}"
    
    return True, ""

if __name__ == '__main__':
    logger.info("Starting Image Validator Webhook on port 8443")
    logger.info(f"Approved registries: {APPROVED_REGISTRIES}")
    logger.info(f"Blocked tags: {BLOCKED_TAGS}")
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
CN = image-validator.image-validator-demo.svc

[ v3_req ]
keyUsage = keyEncipherment, dataEncipherment, digitalSignature
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = image-validator
DNS.2 = image-validator.image-validator-demo
DNS.3 = image-validator.image-validator-demo.svc
DNS.4 = image-validator.image-validator-demo.svc.cluster.local
```

### **📄 deployment.yaml**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: image-validator
  namespace: image-validator-demo
  labels:
    app: image-validator
    version: v1
spec:
  replicas: 2
  selector:
    matchLabels:
      app: image-validator
  template:
    metadata:
      labels:
        app: image-validator
        version: v1
    spec:
      containers:
      - name: validator
        image: devopsdktraining/image-validator:1.0
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
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8443
            scheme: HTTPS
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 5
          failureThreshold: 3
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
      volumes:
      - name: certs
        secret:
          secretName: image-validator-certs
```

### **📄 service.yaml**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: image-validator
  namespace: image-validator-demo
  labels:
    app: image-validator
spec:
  selector:
    app: image-validator
  ports:
    - port: 8443
      targetPort: 8443
      protocol: TCP
  type: ClusterIP
```

### **📄 validating-webhook.yaml**
```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: image-validator
  labels:
    app: image-validator
webhooks:
  - name: image-validator.image-validator-demo.svc
    clientConfig:
      service:
        name: image-validator
        namespace: image-validator-demo
        path: "/validate"
        port: 8443
      caBundle: CA_BUNDLE_PLACEHOLDER
    rules:
      - apiGroups: [""]
        apiVersions: ["v1"]
        operations: ["CREATE", "UPDATE"]
        resources: ["pods"]
    failurePolicy: Fail
    sideEffects: None
    admissionReviewVersions: ["v1"]
    timeoutSeconds: 10
    namespaceSelector:
      matchExpressions:
        - key: kubernetes.io/metadata.name
          operator: NotIn
          values: [image-validator-demo, kube-system]
```

### **📄 configmap.yaml** (Optional - for configuration)
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: image-validator-config
  namespace: image-validator-demo
data:
  approved-registries: |
    docker.io
    gcr.io
    k8s.gcr.io
    quay.io
    registry.k8s.io
    ghcr.io
  blocked-tags: |
    latest
  log-level: "INFO"
```

---

## 2️⃣ Test Pods

### **📄 test-pods/bad-pod-1.yaml** (Unapproved Registry)
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: bad-pod-unapproved-registry
  labels:
    app: test-pod
spec:
  containers:
  - name: nginx
    image: myprivate.registry.com/nginx:1.25  # Unapproved registry
    resources:
      requests:
        memory: "64Mi"
        cpu: "50m"
      limits:
        memory: "128Mi"
        cpu: "100m"
    securityContext:
      runAsNonRoot: true
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
```

### **📄 test-pods/bad-pod-2.yaml** (Latest Tag)
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: bad-pod-latest-tag
  labels:
    app: test-pod
spec:
  containers:
  - name: nginx
    image: nginx:latest  # Blocked tag
    resources:
      requests:
        memory: "64Mi"
        cpu: "50m"
      limits:
        memory: "128Mi"
        cpu: "100m"
    securityContext:
      runAsNonRoot: true
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
```

### **📄 test-pods/bad-pod-3.yaml** (No Resources)
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: bad-pod-no-resources
  labels:
    app: test-pod
spec:
  containers:
  - name: nginx
    image: nginx:1.25-alpine
    # Missing resources section
    securityContext:
      runAsNonRoot: true
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
```

### **📄 test-pods/good-pod.yaml** (Compliant Pod)
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: good-pod
  labels:
    app: test-pod
spec:
  containers:
  - name: nginx
    image: nginx:1.25-alpine  # Approved registry, specific tag
    resources:
      requests:
        memory: "64Mi"
        cpu: "50m"
      limits:
        memory: "128Mi"
        cpu: "100m"
    securityContext:
      runAsNonRoot: true
      runAsUser: 1000
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
```

---

## 3️⃣ Deployment Script

### **📄 deploy.sh**
```bash
#!/bin/bash

set -e

echo "🚀 Starting Image Validator Webhook Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Step 1: Generate TLS certificates
print_status "Step 1: Generating TLS certificates..."
mkdir -p tls

cat > tls/csr.conf << 'EOF'
[ req ]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
x509_extensions = v3_req

[ dn ]
CN = image-validator.image-validator-demo.svc

[ v3_req ]
keyUsage = keyEncipherment, dataEncipherment, digitalSignature
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = image-validator
DNS.2 = image-validator.image-validator-demo
DNS.3 = image-validator.image-validator-demo.svc
DNS.4 = image-validator.image-validator-demo.svc.cluster.local
EOF

openssl req -newkey rsa:2048 -nodes -keyout tls/tls.key \
  -x509 -days 365 -out tls/tls.crt -config tls/csr.conf

print_status "TLS certificates generated successfully."

# Step 2: Create namespace
print_status "Step 2: Creating namespace..."
kubectl create namespace image-validator-demo --dry-run=client -o yaml | kubectl apply -f -

# Step 3: Create TLS secret
print_status "Step 3: Creating TLS secret..."
kubectl delete secret image-validator-certs -n image-validator-demo --ignore-not-found=true
kubectl create secret tls image-validator-certs \
  --namespace=image-validator-demo \
  --cert=tls/tls.crt \
  --key=tls/tls.key

# Step 4: Build and push Docker image
print_status "Step 4: Building Docker image..."
docker build -t devopsdktraining/image-validator:1.0 .
docker push devopsdktraining/image-validator:1.0

# Step 5: Get CA bundle
print_status "Step 5: Generating CA bundle..."
CA_BUNDLE=$(cat tls/tls.crt | base64 | tr -d '\n')

# Step 6: Update validating webhook configuration
print_status "Step 6: Updating webhook configuration..."
cp validating-webhook.yaml validating-webhook-temp.yaml
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i "" "s|CA_BUNDLE_PLACEHOLDER|$CA_BUNDLE|" validating-webhook-temp.yaml
else
    sed -i "s|CA_BUNDLE_PLACEHOLDER|$CA_BUNDLE|" validating-webhook-temp.yaml
fi

# Step 7: Deploy webhook server (without webhook enabled first)
print_status "Step 7: Deploying webhook server..."
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f configmap.yaml

# Step 8: Wait for pods to be ready
print_status "Step 8: Waiting for webhook pods to be ready..."
kubectl wait --for=condition=ready pod -l app=image-validator -n image-validator-demo --timeout=120s

# Step 9: Test the webhook internally
print_status "Step 9: Testing webhook internally..."
kubectl exec -n image-validator-demo deployment/image-validator -- curl -k https://localhost:8443/health

# Step 10: Enable the webhook
print_status "Step 10: Enabling validating webhook..."
kubectl apply -f validating-webhook-temp.yaml

# Step 11: Clean up temporary file
rm -f validating-webhook-temp.yaml

# Step 12: Test the webhook
print_status "Step 12: Testing webhook with sample pods..."

print_status "Testing bad pod (unapproved registry)..."
if kubectl apply -f test-pods/bad-pod-1.yaml 2>&1 | grep -q "denied"; then
    print_status "✅ Bad pod (unapproved registry) correctly rejected"
else
    print_error "❌ Bad pod (unapproved registry) was not rejected"
fi

print_status "Testing bad pod (latest tag)..."
if kubectl apply -f test-pods/bad-pod-2.yaml 2>&1 | grep -q "denied"; then
    print_status "✅ Bad pod (latest tag) correctly rejected"
else
    print_error "❌ Bad pod (latest tag) was not rejected"
fi

print_status "Testing bad pod (no resources)..."
if kubectl apply -f test-pods/bad-pod-3.yaml 2>&1 | grep -q "denied"; then
    print_status "✅ Bad pod (no resources) correctly rejected"
else
    print_error "❌ Bad pod (no resources) was not rejected"
fi

print_status "Testing good pod..."
if kubectl apply -f test-pods/good-pod.yaml; then
    print_status "✅ Good pod correctly created"
else
    print_error "❌ Good pod creation failed"
fi

# Step 13: Final verification
print_status "Step 13: Final verification..."
kubectl get pods -n image-validator-demo
kubectl get validatingwebhookconfiguration image-validator

echo ""
print_status "🎉 Image Validator Webhook deployment completed successfully!"
echo ""
print_status "📋 Validation Rules Enforced:"
print_status "  ✅ Only approved registries: docker.io, gcr.io, quay.io, etc."
print_status "  ✅ No 'latest' tags"
print_status "  ✅ Resource limits and requests required"
print_status "  ✅ Security context: runAsNonRoot, no privilege escalation, read-only root"
echo ""
print_status "All non-compliant pods will be automatically rejected!"
```

---

## 4️⃣ Manual Deployment Steps

```bash
# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh

# Or manually:
# 1. Generate certs, create namespace and secret
# 2. Build and push image
# 3. Deploy webhook components
# 4. Test with sample pods
```

---

## 5️⃣ Verification Commands

```bash
# Check all resources
kubectl get all -n image-validator-demo

# Check webhook configuration
kubectl get validatingwebhookconfiguration image-validator -o yaml

# Check webhook logs
kubectl logs -n image-validator-demo deployment/image-validator

# Monitor webhook metrics
kubectl top pods -n image-validator-demo

# Test ad-hoc
kubectl run test-pod --image=nginx:latest --dry-run=client -o yaml | kubectl apply -f -
```
<img width="1132" height="393" alt="image" src="https://github.com/user-attachments/assets/1772a069-f6b9-4f82-ab91-eb583417b3ce" />

---

## 🎯 **Expected Results**

**All bad pods should be rejected with specific error messages:**
- ❌ `bad-pod-unapproved-registry`: "Registry 'myprivate.registry.com' not in approved list"
- ❌ `bad-pod-latest-tag`: "Tag 'latest' is blocked. Use specific version tags."
- ❌ `bad-pod-no-resources`: "Missing CPU limits, memory limits, CPU requests, memory requests"

<img width="1155" height="324" alt="image" src="https://github.com/user-attachments/assets/2d51d7c4-7d93-4f43-b9ba-af02aa93f306" />


**Good pod should be created successfully:**
- ✅ `good-pod`: Pod created without issues

```bash
deepak@DeepakRK:~/Kubernetes-Imp-Topics/28.Admission_Controllers/k8s-admission-webhook/2.Demo-ImageValidation/k8s-image-validator$ kubectl apply -f test-pods/good-pod.yaml
pod/good-pod created
deepak@DeepakRK:~/Kubernetes-Imp-Topics/28.Admission_Controllers/k8s-admission-webhook/2.Demo-ImageValidation/k8s-image-validator$
```
---

## 🔧 **Real-World Use Cases**

This webhook demonstrates **enterprise-grade security policies**:
1. **Supply Chain Security** - Control where images come from
2. **Image Tag Management** - Prevent floating tags in production
3. **Resource Management** - Ensure proper resource allocation
4. **Security Hardening** - Enforce security best practices
5. **Compliance** - Meet regulatory requirements

Perfect for organizations needing to enforce:
- 🏢 Corporate security policies
- 🔒 Compliance standards (SOC2, HIPAA, PCI-DSS)
- 🚀 Production readiness checks
- 📦 Image provenance validation
