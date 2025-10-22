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

curl -sL https://github.com/operator-framework/operator-lifecycle-manager/releases/download/v0.32.0/install.sh | bash -s v0.32.0

```

<img width="1143" height="690" alt="image" src="https://github.com/user-attachments/assets/5ff93577-06cc-4dba-baf4-89eadcb1bf67" />


Verify OLM pods:

```bash
kubectl get pods -n olm
```

<img width="605" height="192" alt="image" src="https://github.com/user-attachments/assets/2c3da6fe-f6d5-4c7e-bdd9-ba3db5bc1411" />

You should see pods like `olm-operator`, `catalog-operator`, etc.

---
## **Step 3: Deploy cert-manager**
1. Install cert-manager
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.19.1/cert-manager.yaml
```

<img width="1014" height="415" alt="image" src="https://github.com/user-attachments/assets/b1aa550c-7244-499b-b108-8306dfc84121" />


2. Verify

```bash

$ kubectl get pods -n cert-manager

NAME                                       READY   STATUS    RESTARTS   AGE
cert-manager-5c6866597-zw7kh               1/1     Running   0          2m
cert-manager-cainjector-577f6d9fd7-tr77l   1/1     Running   0          2m
cert-manager-webhook-787858fcdb-nlzsq      1/1     Running   0          2m

```

<img width="718" height="185" alt="image" src="https://github.com/user-attachments/assets/907ae965-3105-4ce1-9071-64d8f30cad14" />


## **Step 4: Deploy kube-green Operator**

1. Deploy kube-green Operator using its official manifest:

```bash
kubectl create -f https://operatorhub.io/install/kube-green.yaml
```

Verify:

```bash
kubectl get operators

kubectl get csv

kubectl api-resources --api-group='kube-green.com' -o wide
```

<img width="349" height="95" alt="image" src="https://github.com/user-attachments/assets/fe97a4c8-2cf9-4b42-97a7-7cd82320897b" />

<img width="570" height="78" alt="image" src="https://github.com/user-attachments/assets/76eb627d-619e-46fb-808c-d266aea895e3" />

<img width="1074" height="85" alt="image" src="https://github.com/user-attachments/assets/831d47b7-400a-4c37-94d2-9d2b3d9258b3" />

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
# sleepinfo.yaml
apiVersion: kube-green.com/v1alpha1
kind: SleepInfo
metadata:
  labels:
    app: kube-green
  name: sleepinfo-sample
spec:
  excludeRef:
    - apiVersion: apps/v1
      kind: Deployment
      name: critical-app
  sleepAt: '17:55'
  wakeUpAt: '08:00'
  weekdays: 0-6
  suspendCronJobs: true
  timeZone: Asia/Kolkata
```

Apply it:

```bash
kubectl apply -f sleepinfo.yaml
```
<img width="620" height="178" alt="image" src="https://github.com/user-attachments/assets/4d8db562-d641-4977-aa6b-7f8d5d50d536" />

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

