# Declarative Way of Launching Resources

The **declarative** way in Kubernetes is all about **describing the desired state** of your resource in a manifest (usually YAML or JSON) and letting Kubernetes make it happen.
Instead of saying *“do this now”* (imperative), you say *“this is what I want it to look like”*.

---

## **When to use Declarative approach**

* Production environments
* Resources that need to be **version-controlled** (GitOps)
* Complex configurations
* Consistent deployments across multiple clusters
* Easy rollback and tracking of changes

---

## **1. Steps in declarative approach**

### **Step 1: Write a manifest file**

Example: **Deployment**

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deploy
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
        - name: nginx
          image: nginx:1.25
          ports:
            - containerPort: 80
```

---

### **Step 2: Apply it**

```bash
kubectl apply -f deployment.yaml
```

* `apply` → creates the resource if it doesn’t exist, or updates it if it does.
* Kubernetes figures out the difference between the current state and your desired state.

---

### **Step 3: Verify**

```bash
kubectl get deployments
kubectl describe deployment my-deploy
```

---

## **2. Example: Service**

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  type: NodePort
  selector:
    app: nginx
  ports:
    - port: 80
      targetPort: 80
      nodePort: 30007
```

Apply it:

```bash
kubectl apply -f service.yaml
```

---

## **3. Updating resources declaratively**

Just change the YAML file and re-apply:

```bash
# Change replicas from 3 → 5 in deployment.yaml
kubectl apply -f deployment.yaml
```

Kubernetes updates only what’s necessary.

---

## **4. Deleting declaratively**

```bash
kubectl delete -f deployment.yaml
```

---

## **5. Advantages over Imperative**

* **Repeatable** → same file can be applied to any cluster.
* **Trackable** → store YAML in Git for version control.
* **Safe updates** → Kubernetes only changes the differences.
* **Team-friendly** → everyone works from the same definition.

---

## **Quick Comparison Table**

| Feature             | Imperative Command     | Declarative YAML          |
| ------------------- | ---------------------- | ------------------------- |
| **Speed**           | Fast for one-off tasks | Slower (write YAML first) |
| **Reproducibility** | Low                    | High                      |
| **Version Control** | Not practical          | Easy                      |
| **Best for**        | Testing, quick fixes   | Production, CI/CD, GitOps |

---

If you want, I can give you a **single real-world example** where we create a Pod, Deployment, and Service **in both imperative and declarative ways side-by-side**, so you see the exact commands and YAML for the same setup.
That would make it even more practical for interviews.
