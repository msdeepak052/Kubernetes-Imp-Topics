# **Amazon EKS (Elastic Kubernetes Service)**

---

## ✅ **EKS Upgrade Checklist: Summary**

### 🔷 Step-by-Step Order (High-Level):

1. **Review the EKS release notes**
2. **Backup your cluster state and workload definitions**
3. **Upgrade the EKS Control Plane**
4. **Update `kubectl` and other CLI tools (e.g., `eksctl`, `awscli`)**
5. **Upgrade system components / add-ons (e.g., CoreDNS, kube-proxy, VPC CNI)**
6. **Upgrade Managed Node Groups (MNGs)** or **Launch Template for Self-Managed nodes**
7. **Test workloads on upgraded nodes**
8. **Drain and delete old nodes (if self-managed)**
9. **Monitor the system thoroughly**
10. **(Optional) Upgrade workloads to use new APIs and features**

---

## 📘 **Detailed Explanation of Each Step**

---

### 1. 📝 **Review the EKS Release Notes**

* Visit: [EKS Release Notes](https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html)
* Check **breaking changes**, **deprecated APIs**, **component compatibility**, and **network plugin versions**.
* Identify if there are **custom controllers or CRDs** using deprecated APIs like `apps/v1beta1`, `extensions/v1beta1`.

---

### 2. 📦 **Backup the Cluster**

* Use tools like:

  * `kubectl get all --all-namespaces -o yaml > cluster-backup.yaml`
  * `Velero` for full backup
* Backup:

  * All manifests (`deployments`, `services`, `configmaps`, etc.)
  * Custom Resource Definitions (CRDs)
  * PV/PVC if using persistent storage

---

### 3. ⬆️ **Upgrade the EKS Control Plane**

#### Options:

* **Console**:

  * Navigate to **EKS > Cluster > Update version**
* **eksctl**:

  ```bash
  eksctl upgrade cluster --name <cluster-name> --region <region>
  ```
* **AWS CLI**:

  ```bash
  aws eks update-cluster-version --name <cluster-name> --kubernetes-version 1.28
  ```

🔍 **Notes**:

* This is a **non-disruptive** operation to workloads.
* Upgrade is **minor-version only** (e.g., 1.26 → 1.27)
* Takes 15-30 minutes to complete.

---

### 4. ⚙️ **Update `kubectl`, `eksctl`, and AWS CLI**

Ensure tool versions match the target EKS version:

```bash
kubectl version --client
eksctl version
aws --version
```

Update as needed:

```bash
# For kubectl
curl -LO "https://dl.k8s.io/release/v1.27.0/bin/linux/amd64/kubectl"
```

---

### 5. 🔄 **Update Core Add-ons**

Update the following for compatibility:

#### a. **VPC CNI (aws-node)**

```bash
kubectl set image daemonset aws-node -n kube-system \
  aws-node=602401143452.dkr.ecr.<region>.amazonaws.com/amazon-k8s-cni:<version>
```

#### b. **CoreDNS**

```bash
kubectl get deployment coredns -n kube-system -o yaml > coredns.yaml
# Check and apply the correct version
```

#### c. **kube-proxy**

```bash
kubectl -n kube-system get daemonset kube-proxy -o yaml > kube-proxy.yaml
```

> You can also automate add-on upgrade with `eksctl`:

```bash
eksctl utils update-kube-proxy --cluster <name> --approve
eksctl utils update-coredns --cluster <name> --approve
eksctl utils update-aws-node --cluster <name> --approve
```

---

### 6. 🧱 **Upgrade Worker Nodes**

#### a. **Managed Node Groups**

```bash
eksctl upgrade nodegroup --name <node-group-name> --cluster <cluster-name>
```

Or via AWS Console:

* Select Node Group → Actions → Update Kubernetes version

#### b. **Self-Managed Node Groups**

* Create a **new launch template** with updated AMI ID

  ```bash
  aws ssm get-parameter \
    --name /aws/service/eks/optimized-ami/1.28/amazon-linux-2/recommended/image_id \
    --region <region> --query "Parameter.Value" --output text
  ```
* Spin up new ASG with updated AMI
* **Join nodes** to cluster (ensure IAM role is correct)
* Drain old nodes:

  ```bash
  kubectl drain <node-name> --ignore-daemonsets --delete-local-data
  kubectl delete node <node-name>
  ```

---

### 7. ✅ **Test Workloads on New Nodes**

* Ensure workloads are scheduled and working fine.
* Check:

  * `kubectl get pods -A`
  * `kubectl describe nodes`
  * Logs and performance metrics

---

### 8. 🧹 **Remove Old Nodes**

* If self-managed: Delete EC2 instances or ASGs manually
* If managed: Old versions are automatically removed during upgrade

---

### 9. 📈 **Monitor System Health**

Use:

* **CloudWatch Container Insights**
* **Prometheus/Grafana**
* **kubectl top nodes/pods**

Check:

* System logs
* Add-on performance
* Pod restarts, node pressure, etc.

---

### 10. 🆙 **(Optional) Update Workloads**

* Migrate deprecated APIs
* Rebuild and redeploy images for compatibility
* Use newer features (e.g., ephemeral containers, new scheduling options)

---

## 🚨 **Tips & Best Practices**

| Area           | Best Practice                                             |
| -------------- | --------------------------------------------------------- |
| 💡 Versioning  | Upgrade 1 minor version at a time (e.g., 1.26 → 1.27)     |
| 📋 Testing     | Have a staging/QA cluster to test the upgrade before prod |
| 🛡️ Resilience | Ensure high availability (multiple AZs, multiple nodes)   |
| 🔍 Monitoring  | Set up alerts for CPU, memory, pod crashloops             |
| 📦 Backup      | Always backup manifests and state before upgrade          |

---

### ✅ **Is etcd backed up during an EKS upgrade?**

**Short Answer: No, EKS does not automatically back up etcd for you during an upgrade.**

---

### 🧠 **What is etcd?**

`etcd` is the **key-value store** that holds all of the Kubernetes cluster state: nodes, pods, configmaps, secrets, etc.

In **Amazon EKS**, the etcd datastore is managed **by AWS as part of the control plane**, and **you do not have direct access** to it.

---

### 🔒 **etcd Backup in EKS: What You Need to Know**

| Feature                 | Description                                                                                                                       |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| **etcd control**        | EKS manages etcd internally—you don't have shell access.                                                                          |
| **AWS-managed backups** | AWS **does backup etcd internally** for its own reliability purposes, but **you can’t directly trigger or access these backups**. |
| **Manual workaround**   | You must manually export the cluster state (e.g., manifests, secrets, configs) before upgrades as a form of backup.               |
| **Disaster recovery**   | Full recovery requires re-creating the EKS cluster and reapplying the manifests or using tools like Velero.                       |

---

### ✅ Recommended Action Before Upgrade

Since you **can't access etcd directly**, use these backup strategies:

#### 1. 📥 **Backup all workloads and cluster resources**

```bash
kubectl get all --all-namespaces -o yaml > all-k8s-resources.yaml
```

#### 2. 📁 **Backup important components**

```bash
kubectl get configmaps,secrets,ingresses,networkpolicies,pv,pvc,crds --all-namespaces -o yaml > infra-resources.yaml
```

#### 3. 📦 **Use Velero (Recommended)**

[Velero](https://velero.io) allows you to back up and restore cluster state including volumes.

```bash
velero backup create pre-upgrade-backup --include-namespaces '*' --wait
```

---

### 🧩 Summary

| Backup Type                | Description                                      |
| -------------------------- | ------------------------------------------------ |
| AWS Internal etcd backup   | ✅ Happens automatically, but not user-accessible |
| User-Initiated etcd backup | ❌ Not possible directly                          |
| Recommended                | ✅ Export YAMLs or use Velero                     |

---
If you want to upgrade **Amazon EKS from 1.28 to 1.31**, you **must follow sequential minor version upgrades**, because **EKS does not support skipping Kubernetes versions**.

---

## 🔄 **Upgrade Path: 1.28 → 1.29 → 1.30 → 1.31**

Each upgrade step involves:

* Upgrading **Control Plane**
* Upgrading **Add-ons**
* Upgrading **Node Groups**

---

## ✅ **Step-by-Step: Multi-Version EKS Upgrade (1.28 → 1.31)**

---

### 🔁 Repeat the following steps **for each version** (1.28 → 1.29 → 1.30 → 1.31)

---

### 🔷 Step 0: Prep Once

* ✅ Backup resources:

  ```bash
  kubectl get all --all-namespaces -o yaml > cluster-backup.yaml
  ```
* ✅ Optional: Install and configure Velero with S3 for full backup.

---

### 🔷 Step 1: Upgrade Control Plane

**Run this for each version sequentially:**

```bash
aws eks update-cluster-version \
  --name my-cluster \
  --kubernetes-version 1.29 \
  --region <region>
```

Repeat for 1.30, then 1.31:

```bash
aws eks update-cluster-version --name my-cluster --kubernetes-version 1.30
aws eks update-cluster-version --name my-cluster --kubernetes-version 1.31
```

---

### 🔷 Step 2: Upgrade Add-ons (after each control plane upgrade)

You must upgrade the following to match the new version:

* VPC CNI (`aws-node`)
* CoreDNS
* kube-proxy

With `eksctl`:

```bash
eksctl utils update-aws-node --cluster my-cluster --approve
eksctl utils update-coredns --cluster my-cluster --approve
eksctl utils update-kube-proxy --cluster my-cluster --approve
```

> Or use `kubectl set image` / `kubectl apply` if you manage YAML manually.

---

### 🔷 Step 3: Upgrade Managed Node Groups (for each version)

```bash
eksctl upgrade nodegroup \
  --name <nodegroup-name> \
  --cluster my-cluster \
  --kubernetes-version 1.29 \
  --approve
```

Repeat for 1.30 and 1.31.

**Or** via AWS Console:

* Go to EKS > Node Group > Update Kubernetes Version

---

### 🔷 Step 4: Validate Workloads

After each upgrade:

* Check if pods are running:

  ```bash
  kubectl get pods -A
  ```
* Monitor:

  * CPU/Memory
  * Logs
  * Crash loops or scheduling issues

---

### 🔷 Step 5: Final Clean-up

* Verify everything is healthy:

  ```bash
  kubectl get nodes
  kubectl get events -A
  ```
* Remove unused node groups (if you created new ones during upgrade).

---

## 🧠 Pro Tips

| Tip                           | Why                    |
| ----------------------------- | ---------------------- |
| Upgrade in non-prod first     | Avoid surprises        |
| Use eksctl                    | Simplifies the process |
| Watch for deprecated APIs     | Check release notes    |
| Upgrade one version at a time | EKS enforces it        |

---





