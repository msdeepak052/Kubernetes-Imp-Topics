

### 🧾 Command

```bash
eksctl create cluster \
  --name deepak-private-eks \
  --region ap-south-1 \
  --nodegroup-name private-ng \
  --node-type t2.medium \
  --nodes 2 \
  --nodes-min 2 \
  --nodes-max 4 \
  --managed \
  --node-private-networking \
  --with-oidc \
  --alb-ingress-access \
  --asg-access \
  --full-ecr-access
```

---

### ⚙️ What This Does

| Option                        | Description                                                  |
| ----------------------------- | ------------------------------------------------------------ |
| `--name deepak-private-eks`   | Name of your EKS cluster                                     |
| `--region ap-south-1`         | Region for deployment                                        |
| `--nodegroup-name private-ng` | Node group name                                              |
| `--node-type t2.medium`       | EC2 instance type for nodes                                  |
| `--nodes 2`                   | Desired number of nodes                                      |
| `--managed`                   | Uses managed nodegroups                                      |
| `--node-private-networking`   | Ensures worker nodes have **no public IPs**                  |
| `--with-oidc`                 | Enables OIDC provider (needed for ALB controller)            |
| `--alb-ingress-access`        | Grants permissions required for AWS Load Balancer Controller |
| `--asg-access`                | Gives Auto Scaling Group permissions                         |
| `--full-ecr-access`           | Grants full ECR access (push/pull images)                    |

---

### 🌐 Networking Behavior

* `eksctl` automatically creates a **new VPC** with **2 public and 2 private subnets**.
* Since you added `--node-private-networking`, worker nodes will **launch only in private subnets**.
* The cluster control plane will also be **private** (you’ll connect via an EC2 in the same VPC).

---

### 🧩 To Connect From EC2

After the cluster is ready:

```bash
aws eks update-kubeconfig --name deepak-private-eks --region ap-south-1
kubectl get nodes
```

---

### ✅ Step-by-step `eksctl` command



### ⚙️ Explanation

| Option                      | Purpose                                                                   |
| --------------------------- | ------------------------------------------------------------------------- |
| `--name`                    | Cluster name                                                              |
| `--region`                  | AWS region (`ap-south-1` as per your setup)                               |
| `--node-type t2.medium`     | Node instance type                                                        |
| `--nodes 2`                 | Start with 2 worker nodes                                                 |
| `--vpc-private-subnets`     | Specify your existing private subnet IDs (so cluster is private)          |
| `--without-nodegroup`       | Creates cluster control plane first — helps ensure it’s private           |
| `--node-private-networking` | Ensures worker nodes have **no public IPs**                               |
| `--with-oidc`               | Enables IAM OIDC provider (needed for AWS Load Balancer Controller, etc.) |
| `--alb-ingress-access`      | Grants permissions for **AWS Load Balancer Controller**                   |
| `--asg-access`              | Grants nodegroup scaling permissions                                      |
| `--external-dns-access`     | Optional, for ExternalDNS integration                                     |
| `--full-ecr-access`         | Optional, allows pulling/pushing to ECR                                   |
| `--appmesh-access`          | Optional, enables AWS App Mesh (if needed)                                |

---

### 🧠 Notes

* The **Load Balancer Controller** is not installed automatically, but the above IAM setup (`--alb-ingress-access` + `--with-oidc`) ensures your cluster is **ready** for it.
* You can install the controller later using Helm:

  ```bash
  helm repo add eks https://aws.github.io/eks-charts
  helm repo update
  helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
    -n kube-system \
    --set clusterName=deepak-private-eks \
    --set region=ap-south-1 \
    --set vpcId=<your-vpc-id>

  ```
> After either fix, recheck:

kubectl get pods -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller


✅ Expect STATUS to show Running.

---

You can confirm whether the **AWS Load Balancer Controller** is successfully installed in your EKS cluster using the following steps 👇

---

### 🧩 Step 1: Check Helm Release

```bash
helm list -n kube-system
```

✅ You should see an entry like:

```
NAME                            NAMESPACE    REVISION    STATUS     CHART                            APP VERSION
aws-load-balancer-controller    kube-system  1            deployed   aws-load-balancer-controller-x.y.z  v2.x.x
```

If the `STATUS` is `deployed`, Helm installed it successfully.

---

### 🧩 Step 2: Verify Deployment in Kubernetes

```bash
kubectl get deployment -n kube-system aws-load-balancer-controller
```

✅ Expected output:

```
NAME                           READY   UP-TO-DATE   AVAILABLE   AGE
aws-load-balancer-controller   2/2     2            2           3m
```

Both replicas should be **READY**.

---

### 🧩 Step 3: Check Pods

```bash
kubectl get pods -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller
```

✅ You should see something like:

```
NAME                                                READY   STATUS    RESTARTS   AGE
aws-load-balancer-controller-7d9c96b4df-5pghx       1/1     Running   0          2m
aws-load-balancer-controller-7d9c96b4df-tz8lw       1/1     Running   0          2m
```

---

### 🧩 Step 4: (Optional) Check Logs for Confirmation

```bash
kubectl logs -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller
```

✅ Look for a message like:

```
Successfully started AWS Load Balancer Controller
```

---

### ✅ Bonus Check (verify CRDs are installed)

```bash
kubectl get crds | grep ingress
```

You should see CRDs such as:

```
ingressclassparams.elbv2.k8s.aws
targetgroupbindings.elbv2.k8s.aws
```

---




