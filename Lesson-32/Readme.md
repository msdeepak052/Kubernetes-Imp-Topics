# Helm - Complete Guide for CKA

## 1. What is Helm and Why It's Used?

### The Problem Helm Solves
**Without Helm:**
- Managing multiple Kubernetes YAML files manually
- No versioning of application deployments
- Difficult to share and reuse application configurations
- No easy way to parameterize configurations for different environments
- Complex application lifecycle management

**What Helm Fixes:**
- **Packaging**: Bundle all Kubernetes manifests into a single package
- **Versioning**: Track versions of your application deployments
- **Configuration Management**: Parameterize manifests for different environments
- **Sharing**: Share applications via Helm charts repositories
- **Lifecycle Management**: Install, upgrade, rollback applications easily

## 2. Helm vs Kustomize

| Aspect | Helm | Kustomize |
|--------|------|-----------|
| **Approach** | Templating-based | Patching-based |
| **Packaging** | Creates versioned charts | Uses plain YAML with overlays |
| **Configuration** | Values files | Kustomization.yaml + patches |
| **Learning Curve** | Steeper (templates + Go templating) | Easier (YAML only) |
| **Native Integration** | External tool | Built into kubectl |
| **Use Case** | Application distribution | Environment-specific customization |

## 3. Helm Architecture

### Components
```
Helm Architecture:
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Helm Client   │───▶│  Helm Repository │───▶│  Kubernetes     │
│   (helm CLI)    │    │   (ChartMuseum,  │    │   Cluster       │
│                 │    │    Harbor, etc.)  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
  - helm install          - Stores charts        - Tiller (v2) 
  - helm upgrade          - Version management   - No Tiller (v3)
  - helm rollback
```

### Helm v2 vs Helm v3
- **Helm v2**: Client-Server architecture with Tiller (in-cluster component)
- **Helm v3**: Client-only architecture (Tiller removed) - **CURRENT STANDARD**

## 4. Installation Steps

### Install Helm v3
```bash
# Method 1: Using script
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh

# Method 2: Using package managers
# macOS
brew install helm

# Ubuntu/Debian
sudo snap install helm --classic

# Windows
choco install kubernetes-helm

# Verify installation
helm version
helm help
```

### Initialize Helm (v3 - No setup needed)
```bash
# Helm v3 requires no initialization
helm version

# Add common repositories
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add stable https://charts.helm.sh/stable
helm repo update
```

## 5. How Helm Links with Kubernetes

### Integration Points
- **kubeconfig**: Uses same kubeconfig as kubectl
- **RBAC**: Respects Kubernetes RBAC rules
- **Storage**: Uses Kubernetes secrets to store release information
- **Resources**: Creates standard Kubernetes resources

## 6. Important Helm Concepts

### 1. Chart
A package containing all resource definitions to run an application.

### 2. Release
A deployed instance of a chart with specific configuration.

### 3. Repository
A place where charts can be stored and shared.

### 4. Values
Configuration parameters that can be set during helm install/upgrade.

### 5. Templates
Kubernetes manifest files with Go template placeholders.

### 6. Release Management
Track, upgrade, and rollback deployments.

## 7. Chart Structure
```
mychart/
├── Chart.yaml          # Chart metadata
├── values.yaml         # Default configuration values
├── charts/             # Subcharts/dependencies
├── templates/          # Template files
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   └── _helpers.tpl    # Helper templates
└── templates/NOTES.txt # Post-installation notes
```

## 8. All Helm Commands with Examples

### Repository Commands
```bash
# Add a repository
helm repo add bitnami https://charts.bitnami.com/bitnami

# List repositories
helm repo list

# Update repository information
helm repo update

# Remove a repository
helm repo remove bitnami

# Search for charts
helm search repo nginx
helm search hub nginx  # Search Artifact Hub
```

### Installation & Management Commands
```bash
# Install a chart
helm install my-release bitnami/nginx

# Install with custom values
helm install my-release bitnami/nginx -f values.yaml

# Install with set parameters
helm install my-release bitnami/nginx --set service.type=NodePort

# Upgrade a release
helm upgrade my-release bitnami/nginx --set replicaCount=3

# Rollback a release
helm rollback my-release 1

# Uninstall a release
helm uninstall my-release

# List releases
helm list
helm list --all-namespaces

# Show release status
helm status my-release

# Get release history
helm history my-release
```

### Chart Development Commands
```bash
# Create a new chart
helm create myapp

# Package a chart
helm package myapp/

# Lint a chart
helm lint myapp/

# Template a chart (dry-run)
helm template my-release ./myapp

# Install from local chart
helm install my-release ./myapp

# Dependency management
helm dependency update myapp/
helm dependency list myapp/
```

### Utility Commands
```bash
# Get values from a release
helm get values my-release

# Get all values (including defaults)
helm get values my-release --all

# Get manifest
helm get manifest my-release

# Show chart information
helm show chart bitnami/nginx

# Show all chart values
helm show values bitnami/nginx

# Test a release (run test pods)
helm test my-release
```

## 9. Complete Demo

### Demo 1: Using Existing Charts
```bash
# Search for MySQL chart
helm search repo mysql

# Install MySQL with custom values
helm install my-mysql bitnami/mysql \
  --set auth.rootPassword=secretpassword \
  --set auth.database=myapp \
  --set primary.persistence.size=10Gi

# Check what was installed
helm list
kubectl get all -l app.kubernetes.io/instance=my-mysql

# Upgrade the release
helm upgrade my-mysql bitnami/mysql \
  --set primary.persistence.size=20Gi \
  --set replicaCount=2

# Check history
helm history my-mysql

# Rollback if needed
helm rollback my-mysql 1
```

### Demo 2: Creating Your Own Chart
```bash
# Create a new chart
helm create mywebapp
cd mywebapp

# Explore the created structure
tree .
```

#### Customize the Chart
**Chart.yaml:**
```yaml
apiVersion: v2
name: mywebapp
description: A simple web application
type: application
version: 0.1.0
appVersion: "1.0.0"
```

**values.yaml:**
```yaml
replicaCount: 2

image:
  repository: nginx
  pullPolicy: IfNotPresent
  tag: "1.21"

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: false

resources:
  limits:
    cpu: 200m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi
```

**templates/deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "mywebapp.fullname" . }}
  labels:
    {{- include "mywebapp.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "mywebapp.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "mywebapp.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          ports:
            - name: http
              containerPort: 80
              protocol: TCP
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
```

#### Install Your Custom Chart
```bash
# Dry-run to see generated templates
helm template my-release ./mywebapp

# Install the chart
helm install my-webapp ./mywebapp

# Install with custom values
helm install my-webapp-staging ./mywebapp \
  --set replicaCount=3 \
  --set service.type=NodePort \
  --set image.tag=1.20

# Upgrade
helm upgrade my-webapp ./mywebapp --set replicaCount=4

# Check status
helm status my-webapp

# Uninstall
helm uninstall my-webapp
```

### Demo 3: Advanced Chart with Dependencies

**Chart.yaml with dependencies:**
```yaml
apiVersion: v2
name: myfullapp
description: Full application with dependencies
type: application
version: 0.1.0
appVersion: "1.0.0"

dependencies:
  - name: redis
    version: "16.0.0"
    repository: "https://charts.bitnami.com/bitnami"
  - name: postgresql
    version: "11.0.0"
    repository: "https://charts.bitnami.com/bitnami"
```

```bash
# Update dependencies
helm dependency update myfullapp/

# Install with all dependencies
helm install my-fullapp ./myfullapp
```

## 10. How Helm Helps with Your Own Application

### Scenario: Multi-Environment Deployment

**Directory Structure:**
```
myapp/
├── Chart.yaml
├── values.yaml
├── values-production.yaml
├── values-staging.yaml
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── configmap.yaml
    └── ingress.yaml
```

**values.yaml (default):**
```yaml
replicaCount: 1
image: 
  repository: myapp
  tag: latest
environment: development
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
```

**values-production.yaml:**
```yaml
replicaCount: 3
image: 
  repository: myapp
  tag: stable
environment: production
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"
```

**values-staging.yaml:**
```yaml
replicaCount: 2
image: 
  repository: myapp
  tag: beta
environment: staging
resources:
  requests:
    memory: "256Mi"
    cpu: "150m"
```

### Deployment Commands for Different Environments
```bash
# Development
helm install myapp-dev ./myapp

# Staging
helm install myapp-staging ./myapp -f values-staging.yaml

# Production
helm install myapp-prod ./myapp -f values-production.yaml

# Production with overrides
helm install myapp-prod ./myapp \
  -f values-production.yaml \
  --set replicaCount=5 \
  --set image.tag=v1.2.3
```

### Advanced Template Examples

**Conditional Resources (templates/ingress.yaml):**
```yaml
{{- if .Values.ingress.enabled -}}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "myapp.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
  {{- with .Values.ingress.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
spec:
  {{- if .Values.ingress.tls }}
  tls:
    {{- range .Values.ingress.tls }}
    - hosts:
        {{- range .hosts }}
        - {{ . | quote }}
        {{- end }}
      secretName: {{ .secretName }}
    {{- end }}
  {{- end }}
  rules:
    {{- range .Values.ingress.hosts }}
    - host: {{ .host | quote }}
      http:
        paths:
          {{- range .paths }}
          - path: {{ .path }}
            pathType: Prefix
            backend:
              service:
                name: {{ include "myapp.fullname" $ }}
                port:
                  number: {{ $ .Values.service.port }}
          {{- end }}
    {{- end }}
{{- end }}
```

**ConfigMap with dynamic data (templates/configmap.yaml):**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "myapp.fullname" . }}-config
data:
  app.conf: |
    environment: {{ .Values.environment }}
    log_level: {{ .Values.logLevel | default "info" }}
    database_url: {{ .Values.database.url }}
    {{- with .Values.featureFlags }}
    feature_flags:
      {{- toYaml . | nindent 6 }}
    {{- end }}
```

## 11. Best Practices for CKA

### 1. Always Use --dry-run First
```bash
helm install myapp ./myapp --dry-run --debug
```

### 2. Use Values Files for Different Environments
```bash
helm install -f values-prod.yaml myapp ./myapp
```

### 3. Version Your Charts
```bash
helm package --version 1.2.3 ./myapp
```

### 4. Use Helm Secrets for Sensitive Data
```bash
# Install helm-secrets plugin
helm plugin install https://github.com/jkroepke/helm-secrets

# Use encrypted values
helm secrets install myapp ./myapp -f secrets.yaml
```

### 5. Test Your Charts
```bash
helm test myapp
```

### 6. Cleanup
```bash
# List all releases
helm list --all

# Uninstall specific release
helm uninstall myapp

# Clean up failed releases
helm list --failed | awk '{print $1}' | tail -n +2 | xargs helm uninstall
```

## 12. Real-World Workflow Example

```bash
# 1. Develop your chart
helm create my-microservice
cd my-microservice

# 2. Customize templates and values
# Edit templates/ and values.yaml

# 3. Test locally
helm template test ./my-microservice
helm install --dry-run test ./my-microservice

# 4. Package for distribution
helm package ./my-microservice

# 5. Deploy to different environments
helm install dev ./my-microservice -f values-dev.yaml
helm install staging ./my-microservice -f values-staging.yaml
helm install prod ./my-microservice -f values-prod.yaml

# 6. Upgrade when needed
helm upgrade prod ./my-microservice -f values-prod.yaml --set image.tag=v2.0.0

# 7. Rollback if issues
helm rollback prod 1

# 8. Monitor and manage
helm list
helm status prod
helm get values prod
```

This comprehensive Helm guide covers everything you need for the CKA exam and real-world Kubernetes application management! Helm simplifies complex deployments and provides excellent tooling for application lifecycle management.