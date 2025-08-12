# Imperative Way of Launching Resources

The **imperative way** allows you to create and manage Kubernetes pods directly using `kubectl` commands, without writing YAML manifests.

In Kubernetes, **imperative** creation of resources means you directly tell Kubernetes *what to do right now*, usually through a single command, without relying on a pre-written YAML manifest.

It’s the “just do it” approach, compared to **declarative** (`kubectl apply -f file.yaml`), which is “this is the desired state, make it happen.”

---

## **When to use the Imperative approach**

* Quick testing / prototyping
* One-off tasks (e.g., creating a pod for debugging)
* Learning commands without worrying about YAML syntax
* Situations where you don’t need version control of manifests

---

## **1. Creating resources imperatively**

### **Pod**

```bash
kubectl run nginx-pod --image=nginx --restart=Never
```

* `--restart=Never` ensures this is a **Pod**, not a Deployment.
* This will create a pod named `nginx-pod` running the `nginx` image.

<img width="745" height="458" alt="image" src="https://github.com/user-attachments/assets/80021e5e-ce27-4ed1-80ec-b4042a2f7b3d" />

---

### **Deployment**

```bash
kubectl create deployment my-deploy --image=nginx --replicas=3
```

* Creates a deployment `my-deploy` with 3 replicas of nginx.
* You can later scale:

```bash
kubectl scale deployment my-deploy --replicas=5
```

---

### **Service**

```bash
kubectl expose deployment my-deploy --port=80 --target-port=80 --type=NodePort
```

* Exposes your deployment with a service on port 80, accessible via NodePort.
```bash
kubectl port-forward svc/my-deploy 8080:80
```

<img width="1920" height="817" alt="image" src="https://github.com/user-attachments/assets/12efe78d-e035-4e1c-8913-c12606173898" />

---

## **2. Editing and generating YAML from imperative commands**

Even though you start imperatively, you can get YAML output for reuse:

```bash
kubectl create deployment my-deploy --image=nginx --dry-run=client -o yaml > deployment.yaml
```

* `--dry-run=client` → doesn’t actually create it, just shows the manifest.
* `-o yaml` → outputs YAML.
* Useful to switch from imperative to declarative.

---

## **3. Updating resources imperatively**

### **Changing image**

```bash
kubectl set image deployment/my-deploy nginx=nginx:1.25
```

### **Port-forwarding**

```bash
kubectl port-forward pod/nginx-pod 8080:80
```

---

## **4. Deleting resources imperatively**

```bash
kubectl delete pod nginx-pod
kubectl delete deployment my-deploy
```

---

## **Example workflow (Imperative style)**

```bash
# Create pod
kubectl run mypod --image=nginx --restart=Never

# Create service for pod
kubectl expose pod mypod --port=80 --type=NodePort

# Update image
kubectl set image pod/mypod nginx=nginx:1.25 --record

# Delete pod
kubectl delete pod mypod
```

---

✅ **Key takeaway:**
Imperative commands are faster for quick changes but not ideal for production because:

* They don’t track history in Git.
* Harder to reproduce environment later.
* Risk of drift between clusters.

---
