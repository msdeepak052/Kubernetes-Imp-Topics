## What are Static Pods?

Static Pods are pods that are managed **directly by the `kubelet` agent** on a specific node, rather than by the Kubernetes API server (e.g., via a Deployment, DaemonSet). The `kubelet` watches a directory on the node's filesystem (`/etc/kubernetes/manifests/` by default) and automatically creates, deletes, and restarts the pods defined by the YAML/JSON files it finds there.

## Why Are They Used? The Critical Use Case

The primary and most important use case for Static Pods is **bootstrapping the Kubernetes control plane itself.**

Think about the chicken-and-egg problem:
*   To have a cluster, you need the API server running.
*   But the API server is what's supposed to manage pods (like the API server pod!).

Static Pods solve this:
1.  You install `kubelet` on a node.
2.  You place a Pod manifest for `kube-apiserver`, `kube-controller-manager`, `kube-scheduler`, and `etcd` in the Static Pod directory.
3.  The `kubelet` reads this directory and starts these pods.
4.  **Now your control plane is running.** Once the API server is up, the `kubelet` can then register the node with the API server and report the status of the Static Pods it's running.

**Other use cases include:**
*   Running a cluster-level component that must be running before the API server is available.
*   Running a custom node-level agent that is too critical to be managed by the cluster's scheduler (which depends on the API server being healthy).

---

## How are They Controlled?

Static Pods are controlled in a very simple way: **by directly managing files on the node's filesystem.**

*   **To create a Static Pod:** Place a valid Pod manifest file (`.yaml` or `.json`) in the designated directory (e.g., `/etc/kubernetes/manifests/`).
*   **To update a Static Pod:** Edit the manifest file in place. The `kubelet` will detect the change and restart the pod with the new configuration.
*   **To delete a Static Pod:** Remove the manifest file from the directory. The `kubelet` will terminate the pod.

This is very different from "normal" pods, which are controlled by sending commands to the API server (`kubectl apply/delete`).

### The "Mirror Pod" Concept

There's a clever trick that makes Static Pods visible in the Kubernetes API. For each Static Pod it creates, the `kubelet` automatically creates a **Mirror Pod** in the Kubernetes API server.

*   The **Mirror Pod** is a read-only representation of the Static Pod.
*   You can see it with `kubectl get pods`.
*   **You cannot manage the Mirror Pod with `kubectl`.** If you try to `kubectl delete` a Mirror Pod, it will be recreated moments later by the `kubelet` because the static manifest file still exists on the node.
*   The Mirror Pod's name is typically prefixed with the node name (e.g., `kube-apiserver-my-master-node`).

This allows cluster administrators to use `kubectl` to check the status of the critical control plane components running as Static Pods.

---

## Where Do They Reside?

Static Pod manifests reside on the **local filesystem of the node** where they are meant to run. The specific directory is defined by the `kubelet`'s configuration.

*   **The default location is `/etc/kubernetes/manifests/`.** This is the path used by most installation tools like `kubeadm`.
*   The exact path can be set by the `--pod-manifest-path` argument passed to the `kubelet` process.

You can find the exact path on a node by checking the `kubelet` process:

```bash
# SSH into a node (especially a control-plane node)
ssh master-node

# Check the kubelet process to see the configured manifest path
ps aux | grep kubelet | grep manifest-path
# You will often see: ... /usr/bin/kubelet ... --pod-manifest-path=/etc/kubernetes/manifests ...
```

---

## Practical Example: Let's Look at a Real Control Plane

This is the best way to understand. If you set up a cluster with `kubeadm`, your control plane components are Static Pods.

**1. Let's see the pods. Notice the node names in the pod names:**
```bash
kubectl get pods -n kube-system -o wide
```
You will see pods like this (note the `control-plane` node name in each pod name):
```
NAME                               READY   STATUS    RESTARTS   AGE
etcd-control-plane                 1/1     Running   0          10d
kube-apiserver-control-plane       1/1     Running   0          10d
kube-controller-manager-control-plane  1/1     Running   0          10d
kube-scheduler-control-plane       1/1     Running   0          10d
coredns-xxxxxx-yyy                 1/1     Running   0          10d
...other pods...
```
The ones with the node name prefix are the Mirror Pods for the Static Pods.

**2. Now, let's SSH into the control-plane node and look at the manifest directory:**
```bash
# SSH into your master node (named 'control-plane' in this example)
ssh control-plane

# List the contents of the static pod manifest directory
ls -la /etc/kubernetes/manifests/
```
You will see the actual YAML files that define the control plane:
```
total 32
-rw------- 1 root root 2290 Feb 19 12:34 etcd.yaml
-rw------- 1 root root 3983 Feb 19 12:34 kube-apiserver.yaml
-rw------- 1 root root 3411 Feb 19 12:34 kube-controller-manager.yaml
-rw------- 1 root root 1425 Feb 19 12:34 kube-scheduler.yaml
```

**3. Let's examine one of these files (e.g., the API server):**
```bash
cat /etc/kubernetes/manifests/kube-apiserver.yaml
```
You will see a perfectly normal Pod manifest! It defines a pod with the `kube-apiserver` container, its command arguments, liveness probes, and volumes (like TLS certificates for secure communication).

**4. Try to delete it via kubectl (it will restart!):**
```bash
# From your local machine, not the node, try to delete the API server pod
kubectl delete pod -n kube-system kube-apiserver-control-plane

# Watch it get deleted and then almost immediately recreated.
kubectl get pods -n kube-system -w | grep apiserver

# The pod will have a new age and restarted count, but it's back.
# This proves you can't manage it via the API; you must manage the file on the node.
```

## Summary

| Feature | Static Pods | Normal Pods (via API) |
| :--- | :--- | :--- |
| **Managed by** | The `kubelet` on a specific node | The Kubernetes API Server & Controllers |
| **Configuration** | YAML/JSON files on the node's filesystem | API objects (e.g., `kubectl apply`, Deployments) |
| **Deletion** | Remove the manifest file | `kubectl delete pod <name>` |
| **Primary Use** | Bootstrapping control plane components | All regular application workloads |
| **Visibility** | Visible as read-only **Mirror Pods** in the API | Fully manageable API objects |

In short, **Static Pods are the foundation upon which a self-hosted Kubernetes control plane is built.** They provide a simple, reliable mechanism to get the cluster's management services running before the cluster itself fully exists.
