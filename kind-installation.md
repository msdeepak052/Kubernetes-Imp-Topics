# KIND Cluster Setup with NodePort & Metrics Server

## Overview

This document describes how to:

* Install **KIND (Kubernetes in Docker)**
* Create a **2-node cluster**
* Expose applications using **NodePort**
* Install and configure **Metrics Server** for resource metrics and autoscaling

This setup is suitable for **local development, demos, and learning Kubernetes**.

---

## Prerequisites

* Ubuntu (WSL2 or native)
* Docker installed and running
* Internet access

---

## Install Docker

```bash
sudo apt update
sudo apt install -y docker.io
sudo usermod -aG docker $USER
newgrp docker
```

Verify:

```bash
docker run hello-world
```

---

## Install KIND

```bash
curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

Verify:

```bash
kind version
```

---

## Install kubectl

```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```

Verify:

```bash
kubectl version --client
```

---

## Create KIND Cluster (2 Nodes + NodePort Enabled)

### KIND Configuration

Create file:

```bash
nano kind-nodeport.yaml
```

```yaml

kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4

# Specify the Kubernetes version by using a specific node image
# Visit https://hub.docker.com/r/kindest/node/tags and https://github.com/kubernetes-sigs/kind/releases for available images

nodes:
  - role: worker
  - role: control-plane
    image: kindest/node:v1.35.0
    extraPortMappings:
      - containerPort: 31000 # Port inside the KIND container
        hostPort: 31000 # Port on your local machine (host system).
        # If this were set to 9090, you would access the service at localhost:9090,
        # and traffic would be forwarded to containerPort 31000 inside the KIND cluster

```

### Create Cluster

```bash
 kind create cluster --name=deepak-kind-cluster --config=kind-2node.yaml
```

Verify:

```bash
kubectl get nodes
```

Expected:

```
control-plane   Ready
worker          Ready
```

---

## Deploy Sample Application (NGINX)

```bash
kubectl create deployment nginx --image=nginx
```

Expose using NodePort:

```bash
kubectl expose deployment nginx \
  --type=NodePort \
  --port=80 \
  --target-port=80 \
  --name=nginx-service
```

Edit service to fix NodePort:

```bash
kubectl edit svc nginx-service
```

```yaml
spec:
  type: NodePort
  ports:
  - port: 80
    targetPort: 80
    nodePort: 31000
```

Verify:

```bash
kubectl get svc nginx-service
```

Access in browser:

```
http://localhost:31000
```

---

## Install Metrics Server (Addon)

Metrics Server provides CPU and memory metrics for:

* `kubectl top`
* Horizontal Pod Autoscaler (HPA)

### Install Metrics Server

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

### Patch for KIND (Required)

```bash
kubectl patch deployment metrics-server -n kube-system \
  --type='json' \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
```

### Verify Installation

```bash
kubectl get pods -n kube-system | grep metrics
```

Expected:

```
metrics-server   1/1   Running
```

---

## Verify Metrics

```bash
kubectl top nodes
kubectl top pods
```

If metrics appear, Metrics Server is working correctly.

---

## Optional: Horizontal Pod Autoscaler (HPA)

### Create HPA

```bash
kubectl autoscale deployment nginx \
  --cpu-percent=50 \
  --min=1 \
  --max=5
```

Verify:

```bash
kubectl get hpa
```

---

## Useful Commands

### List KIND clusters

```bash
kind get clusters
```

### Delete cluster

```bash
kind delete cluster --name kind-2node
```

### View all pods

```bash
kubectl get pods -A
```

---

## Notes / Best Practices

* KIND NodePort requires `extraPortMappings`
* Metrics Server requires `--kubelet-insecure-tls` in KIND
* NodePort range: `30000–32767`
* For production-like access, prefer **Ingress + NGINX**

---

## Next Enhancements (Optional)

* NGINX Ingress Controller
* MetalLB LoadBalancer
* TLS / HTTPS
* Harbor Registry
* HPA with load testing
* Prometheus + Grafana

---
