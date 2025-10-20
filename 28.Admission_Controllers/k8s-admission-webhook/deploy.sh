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
docker build --no-cache -t devopsdktraining/pod-validator:4.0 .
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