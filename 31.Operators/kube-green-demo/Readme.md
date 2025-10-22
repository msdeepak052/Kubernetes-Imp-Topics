# Step-by-step demo of the kube-green Operator

---

## **Step 1: Pre-requisites**

Make sure you have:

* A Kubernetes cluster (minikube, kind, or any managed cluster)
* `kubectl` configured
* `helm` installed (optional for some OLM installs)
* `oc` CLI if you’re using OpenShift (optional)

Check cluster status:

```bash
kubectl get nodes
```

---

## **Step 2: Install the Operator Lifecycle Manager (OLM)**

OLM is used to install and manage Operators on Kubernetes.

```bash
# Apply the OLM manifests 
kubectl create -f https://github.com/operator-framework/operator-lifecycle-manager/releases/latest/download/crds.yaml
kubectl create -f https://github.com/operator-framework/operator-lifecycle-manager/releases/latest/download/olm.yaml

or

curl -sL https://github.com/operator-framework/operator-lifecycle-manager/releases/download/v0.35.0/install.sh | bash -s v0.32.0

```

Verify OLM pods:

```bash
kubectl get pods -n olm
```

You should see pods like `olm-operator`, `catalog-operator`, etc.

---

## **Step 3: Deploy kube-green Operator**

1. Create a namespace for operators:

```bash
kubectl create namespace operators
```

2. Deploy kube-green Operator using its official manifest:

```bash
kubectl apply -f https://raw.githubusercontent.com/liqotech/kube-green/main/deploy/operator.yaml -n operators
```

Check the operator pod:

```bash
kubectl get pods -n operators
```

You should see something like:

```
NAME                            READY   STATUS    RESTARTS   AGE
kube-green-operator-xxxxx       1/1     Running   0          1m
```

---

## **Step 4: Create a sample Deployment**

We’ll create a simple Nginx deployment that kube-green will manage.

Create `nginx-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  namespace: default
  labels:
    app: nginx
spec:
  replicas: 2
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
          image: nginx:stable
          ports:
            - containerPort: 80
```

Apply it:

```bash
kubectl apply -f nginx-deployment.yaml
```

Check pods:

```bash
kubectl get pods -l app=nginx
```

---

## **Step 5: Apply a SleepInfo custom resource**

kube-green uses the **SleepInfo CRD** to decide when to scale down/up workloads.

Create `sleepinfo.yaml`:

```yaml
apiVersion: kube-green.liqo.io/v1alpha1
kind: SleepInfo
metadata:
  name: nginx-sleep
  namespace: default
spec:
  selector:
    matchLabels:
      app: nginx
  schedule:
    - day: Mon-Fri
      startTime: "20:00"
      endTime: "08:00"
  behavior:
    scaleDownReplicas: 0
    scaleUpReplicas: 2
```

Apply it:

```bash
kubectl apply -f sleepinfo.yaml
```

---

## **Step 6: Watch the Operator in action**

Check deployment replicas:

```bash
kubectl get deployment nginx-deployment
```

If your current time is within the `startTime` to `endTime` window, kube-green will scale the deployment down:

```bash
kubectl get pods -l app=nginx
```

You’ll see pods reduced to `0`. When the off-hours end, kube-green will scale the deployment back to `2`.

You can also watch the operator logs:

```bash
kubectl logs -l name=kube-green-operator -n operators -f
```

It will show messages like:

```
Scaling down deployment default/nginx-deployment from 2 to 0
Scaling up deployment default/nginx-deployment from 0 to 2
```

---

✅ **Demo Complete**

You’ve successfully:

1. Installed OLM
2. Deployed kube-green Operator
3. Created a sample deployment
4. Applied a SleepInfo CRD
5. Observed kube-green scaling the deployment automatically

---

