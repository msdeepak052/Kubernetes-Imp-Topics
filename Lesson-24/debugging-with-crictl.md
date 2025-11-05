# Kubernetes documentation on debugging nodes using `crictl` 
---

## 🧰 **What is `crictl`?**

`crictl` is a command-line interface for interacting with CRI-compatible container runtimes like containerd or CRI-O. It's particularly useful for debugging nodes when `kubectl` isn't available or when you need to inspect the container runtime directly.

---

## ✅ **Before You Begin**

* **Operating System**: Ensure you're using a Linux-based system with a CRI-compatible runtime.
* **Access**: You need SSH or direct access to the node you're troubleshooting.

---

## 📥 **Installing `crictl`**

1. **Download**: Obtain the appropriate version of `crictl` from the [cri-tools release page](https://github.com/kubernetes-sigs/cri-tools/releases).
2. **Extract**:

   ```bash
   tar -zxvf crictl-<version>-linux-amd64.tar.gz
   ```
3. **Install**:

   ```bash
   sudo mv crictl /usr/local/bin/
   ```

---

## ⚙️ **Configuring `crictl`**

`crictl` requires the container runtime's endpoint to function correctly.

* **Set via Flags**:

  ```bash
  crictl --runtime-endpoint unix:///var/run/containerd/containerd.sock
  ```

* **Set via Environment Variables**:

  ```bash
  export CONTAINER_RUNTIME_ENDPOINT=unix:///var/run/containerd/containerd.sock
  ```

* **Set via Configuration File** (`/etc/crictl.yaml`):

  ```yaml
  runtime-endpoint: unix:///var/run/containerd/containerd.sock
  image-endpoint: unix:///var/run/containerd/containerd.sock
  timeout: 10
  debug: true
  ```

---

## 🛠️ **Common `crictl` Commands**

* **List Containers**:

  ```bash
  crictl ps
  ```

* **List Images**:

  ```bash
  crictl images
  ```

* **View Container Logs**:

  ```bash
  crictl logs <container_id>
  ```

* **Inspect Container**:

  ```bash
  crictl inspect <container_id>
  ```

* **Pull Image**:

  ```bash
  crictl pull <image_name>
  ```

* **Run a Container**:

  ```bash
  crictl runp <pod_config_file>
  ```

---

## 🔍 **Troubleshooting with `crictl`**

### 1. **Pod Not Starting**

* **Check Pod Status**:

  ```bash
  crictl pods
  ```

* **Inspect Pod Details**:

  ```bash
  crictl inspectp <pod_id>
  ```

* **View Container Logs**:

  ```bash
  crictl logs <container_id>
  ```

### 2. **Container Crashing**

* **List Containers**:

  ```bash
  crictl ps -a
  ```

* **Inspect Container Logs**:

  ```bash
  crictl logs <container_id>
  ```

* **Check Exit Status**:

  ```bash
  crictl inspect <container_id> | jq '.status.state'
  ```

### 3. **Image Issues**

* **List Images**:

  ```bash
  crictl images
  ```

* **Pull Image**:

  ```bash
  crictl pull <image_name>
  ```

* **Remove Image**:

  ```bash
  crictl rmi <image_name>
  ```

---

## 🧪 **Example Scenario**

**Problem**: A pod is stuck in the `ContainerCreating` state.

**Steps**:

1. **Check Pod Status**:

   ```bash
   crictl pods
   ```

2. **Inspect Pod Details**:

   ```bash
   crictl inspectp <pod_id>
   ```

3. **View Container Logs**:

   ```bash
   crictl logs <container_id>
   ```

4. **Check Image Pull Errors**:

   ```bash
   crictl images
   ```

   If the image isn't listed, there might be an issue with the image pull.

5. **Pull Image Manually**:

   ```bash
   crictl pull <image_name>
   ```

---

## 🧹 **Cleaning Up**

After troubleshooting, you might want to clean up resources:

* **Remove Container**:

  ```bash
  crictl rm <container_id>
  ```

* **Remove Pod**:

  ```bash
  crictl rmp <pod_id>
  ```

* **Remove Image**:

  ```bash
  crictl rmi <image_name>
  ```

---

## 📚 **Additional Resources**

* [Kubernetes Troubleshooting Guide](https://kubernetes.io/docs/tasks/debug/debug-cluster/)
* [Debugging Kubernetes Nodes with Kubectl](https://kubernetes.io/docs/tasks/debug/debug-cluster/kubectl-node-debug/)
* [Debugging Kubernetes Nodes with crictl](https://kubernetes.io/docs/tasks/debug/debug-cluster/crictl/)

---

Feel free to ask if you need further details or examples on using `crictl` for specific troubleshooting scenarios!
