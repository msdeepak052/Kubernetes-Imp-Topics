# EKS creation using eksctl

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

> here’s the exact command to **delete an EKS cluster** using `eksctl`:

---

### 🧾 Command

```bash
eksctl delete cluster --name deepak-private-eks --region ap-south-1
```

---

### ⚙️ Explanation

| Option                      | Description                                  |
| --------------------------- | -------------------------------------------- |
| `--name deepak-private-eks` | The name of your EKS cluster                 |
| `--region ap-south-1`       | The AWS region where the cluster was created |

---

### 🧹 What This Does

* Deletes the **EKS control plane**
* Deletes **nodegroups** and **EC2 instances**
* Deletes the **VPC** and all **subnets, route tables, security groups**, etc. (if `eksctl` created them)
* Cleans up all **CloudFormation stacks** associated with that cluster

---

### ⚠️ Important Notes

* If you created the **VPC manually** (not by `eksctl`), it won’t be deleted automatically.
* You can check progress via CloudFormation:

  ```
  aws cloudformation list-stacks --region ap-south-1
  ```
* If you want to delete **only the nodegroup** (keep cluster), you can use:

  ```bash
  eksctl delete nodegroup --cluster deepak-private-eks --name private-ng --region ap-south-1
  ```

---

✅ **Summary:**
For full cleanup:

```bash
eksctl delete cluster --name deepak-private-eks --region ap-south-1
```




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
## EBS Installation steps

Excellent — you captured the **key part of the error** 👇

```
AccessDenied: Not authorized to perform sts:AssumeRoleWithWebIdentity
```

---

## ⚠️ Root Cause

Your **EBS CSI controller pods** are crashing because the **IAM Role for Service Account (IRSA)** is **not properly configured or missing required permissions**.

The controller tries to assume its IAM role via the OIDC identity provider (for web identity), but the IAM role either:

* ❌ Doesn’t trust your EKS cluster’s OIDC provider, or
* ❌ Lacks the correct IAM policy (`AmazonEBSCSIDriverPolicy`), or
* ❌ The ServiceAccount is not linked to that role.

---

## ✅ Fix (AWS Official Method)

Let’s fix this step-by-step 👇

---

### **Step 1️⃣ — Get your cluster name and region**

Make sure you replace these in commands:

```bash
CLUSTER_NAME=deepak-private-eks
REGION=ap-south-1
```

---

### **Step 2️⃣ — Create IAM policy (if not already)**

Download and create the official EBS CSI policy:

```bash
curl -o ebs-policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-ebs-csi-driver/master/docs/example-iam-policy.json
aws iam create-policy \
  --policy-name AmazonEBSCSIDriverPolicy \
  --policy-document file://ebs-policy.json
```

👉 Note: If the policy already exists, you’ll get an error — that’s okay.

---

### **Step 3️⃣ — Create the IAM Service Account**

This links Kubernetes service account to the IAM role via IRSA.

```bash
eksctl create iamserviceaccount \
  --name ebs-csi-controller-sa \
  --namespace kube-system \
  --cluster $CLUSTER_NAME \
  --attach-policy-arn arn:aws:iam::<your-account-id>:policy/AmazonEBSCSIDriverPolicy \
  --approve \
  --role-name AmazonEKS_EBS_CSI_DriverRole
```

> Replace `<your-account-id>` with your AWS account ID (e.g., `339712902352`).

---

### **Step 4️⃣ — Reinstall the EBS CSI driver with that ServiceAccount**

Reinstall or upgrade the Helm release:

```bash
helm upgrade --install aws-ebs-csi-driver \
  aws-ebs-csi-driver/aws-ebs-csi-driver \
  -n kube-system \
  --set controller.serviceAccount.create=false \
  --set controller.serviceAccount.name=ebs-csi-controller-sa \
  --set enableVolumeResizing=true \
  --set enableVolumeSnapshot=true \
  --set region=$REGION \
  --set kubeletRootDir=/var/lib/kubelet
```

---

### **Step 5️⃣ — Verify**

```bash
kubectl get pods -n kube-system | grep ebs
```

✅ Expected:

```
ebs-csi-controller-xxxxx     6/6   Running   0   1m
ebs-csi-node-xxxxx           3/3   Running   0   1m
```

You can also check logs:

```bash
kubectl logs -n kube-system -l app.kubernetes.io/name=aws-ebs-csi-driver
```

✅ You should now see:

```
Successfully started AWS EBS CSI Driver
```
kubectl get storageclass
kubectl patch storageclass gp2 -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'


---
## Troubleshooting steps


### 🧩 **Option 1: Check using AWS CLI**

Run this command (replace with your cluster name and region):

```bash
aws eks describe-addon \
  --cluster-name deepak-private-eks \
  --addon-name aws-ebs-csi-driver \
  --region ap-south-1
```

✅ You should see output like:

```json
{
    "addon": {
        "addonName": "aws-ebs-csi-driver",
        "status": "ACTIVE",
        "addonVersion": "v1.x.x-eksbuild.x",
        ...
    }
}
```

If `status` is `ACTIVE`, it’s successfully installed and running.

---

### 🧩 **Option 2: Check using `kubectl`**

Run:

```bash
kubectl get pods -n kube-system | grep ebs
```

✅ You should see something like:

```
ebs-csi-controller-xxxxxx-xxxxx   2/2     Running   0   5m
ebs-csi-node-xxxxx                3/3     Running   0   5m
```

If all pods are **Running**, the driver is functioning properly.

---

### 🧩 **Option 3: Check the DaemonSet and Deployment**

```bash
kubectl get daemonset ebs-csi-node -n kube-system
kubectl get deployment ebs-csi-controller -n kube-system
```

✅ Both should show **DESIRED = AVAILABLE**.

---
Excellent check, Deepak ✅

From what you’ve shared, here’s the detailed breakdown of what’s happening:

---

### 🔍 **Findings**

#### 1️⃣ Add-on status from AWS CLI

```
status: CREATING
```

⛔ This means the **AWS EBS CSI driver add-on** has **not yet finished installing** on the cluster.
It’s still in the “creating” phase, which is why the controller pods are failing.

---

#### 2️⃣ Controller Pods

```
ebs-csi-controller-*   1/6   CrashLoopBackOff
```

That confirms the **controller pods are crashing** because the installation hasn’t completed correctly — likely due to:

* IAM role or permissions not being ready
* Incomplete service account association
* Add-on still being provisioned

---

### 🧭 **Next Steps (Fix)**

#### ✅ Step 1. Wait a bit and recheck the add-on status

Run this:

```bash
aws eks describe-addon \
  --cluster-name deepak-private-eks \
  --addon-name aws-ebs-csi-driver \
  --region ap-south-1 \
  --query "addon.status"
```

If it changes to:

```
"ACTIVE"
```

then the installation is done — and the CrashLoopBackOff issue usually resolves automatically within a minute or two.

---

#### ✅ Step 2. If it remains stuck in `CREATING` for more than 5–10 minutes:

You can **recreate it cleanly** from CLI with the correct IAM role.

🧩 Run:

```bash
aws eks delete-addon \
  --cluster-name deepak-private-eks \
  --addon-name aws-ebs-csi-driver \
  --region ap-south-1
```

Then re-add it:

```bash
aws eks create-addon \
  --cluster-name deepak-private-eks \
  --addon-name aws-ebs-csi-driver \
  --region ap-south-1 \
  --service-account-role-arn arn:aws:iam::339712902352:role/AmazonEKS_EBS_CSI_DriverRole
```

*(Replace the role ARN with the correct IAM role that has the policy `AmazonEBSCSIDriverPolicy` attached.)*

---

#### ✅ Step 3. Confirm fix

Once `status: ACTIVE` is seen:

```bash
kubectl get pods -n kube-system | grep ebs
```

✅ Expect:

```
ebs-csi-controller-xxxx   6/6   Running
ebs-csi-node-xxxx         3/3   Running
```

---



