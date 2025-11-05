# **What is kubeconfig?**

* `kubeconfig` is a YAML file used by `kubectl`, client SDKs, and tools to **authenticate (who you are)** and **authorize (what you can access)** against Kubernetes clusters.
* By default, this file is located at:

  * **Linux/Mac:** `~/.kube/config`
  * **Windows:** `%USERPROFILE%\.kube\config`

It contains **clusters**, **users (credentials)**, and **contexts**.

---

## **Structure of kubeconfig (YAML Example)**

```yaml
apiVersion: v1
kind: Config

clusters:
- name: dev-cluster
  cluster:
    server: https://34.120.12.34:6443
    certificate-authority: /home/user/.kube/ca.crt

- name: prod-cluster
  cluster:
    server: https://35.230.56.78:6443
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJ...

users:
- name: dev-user
  user:
    client-certificate: /home/user/.kube/dev-user.crt
    client-key: /home/user/.kube/dev-user.key

- name: prod-user
  user:
    token: eyJhbGciOiJSUzI1NiIsImtpZCI6...

contexts:
- name: dev-context
  context:
    cluster: dev-cluster
    user: dev-user
    namespace: development

- name: prod-context
  context:
    cluster: prod-cluster
    user: prod-user
    namespace: production

current-context: dev-context
```

---

## **Explanation of Terms**

### **1. apiVersion & kind**

* `apiVersion: v1` → The Kubernetes API version for kubeconfig.
* `kind: Config` → Defines the file as a kubeconfig configuration.

---

### **2. clusters**

* Defines the Kubernetes **API servers** you can connect to.
* Each cluster entry has:

  * `name`: Identifier used inside kubeconfig.
  * `cluster`: Actual details of the cluster.

    * `server`: API server endpoint (`https://<IP>:6443`).
    * `certificate-authority`: Path to CA file (verifies cluster identity).
    * `certificate-authority-data`: Inline base64-encoded CA data.

---

### **3. users**

* Defines **credentials** to access the cluster.
* Each user entry has:

  * `name`: Identifier used in contexts.
  * `user`: Authentication details:

    * `client-certificate` + `client-key` → TLS certs for authentication.
    * `token` → Bearer token (common in service accounts).
    * `username` + `password` → Basic auth (rare, not recommended).
    * `exec` → External plugin to fetch credentials dynamically (e.g., `aws-iam-authenticator`).

---

### **4. contexts**

* Contexts **bind a cluster with a user**, and optionally a namespace.
* Each context entry has:

  * `name`: Identifier for the context.
  * `context`:

    * `cluster`: Which cluster to connect.
    * `user`: Which credentials to use.
    * `namespace`: Default namespace for operations (if not specified in commands).

---

### **5. current-context**

* Specifies the **active context** that `kubectl` will use by default.
* Example:

  ```bash
  kubectl config use-context prod-context
  ```

  switches the current context to production.

---

## **Authentication vs Authorization**

* **Authentication** (who you are):

  * Handled by the `users` section (certs, tokens, IAM plugins, etc.).
* **Authorization** (what you can do):

  * Once authenticated, Kubernetes uses **RBAC (Role-Based Access Control)**, tied to your user/service account, to decide allowed actions.

---

✅ Example usage:

```bash
# View current context
kubectl config current-context

# Switch context
kubectl config use-context dev-context

# View all contexts
kubectl config get-contexts
```

---

👍 Let’s extend the **kubeconfig explanation** with **real-world examples from AWS (EKS) and Azure (AKS)**.

---

## **1. AWS EKS – kubeconfig example**

When you run:

```bash
aws eks update-kubeconfig --region ap-south-1 --name my-eks-cluster
```

It updates/creates your kubeconfig with an entry like this:

```yaml
apiVersion: v1
clusters:
- cluster:
    server: https://ABCDE12345.gr7.ap-south-1.eks.amazonaws.com
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJ...
  name: arn:aws:eks:ap-south-1:339712902352:cluster/my-eks-cluster

contexts:
- context:
    cluster: arn:aws:eks:ap-south-1:339712902352:cluster/my-eks-cluster
    user: arn:aws:eks:ap-south-1:339712902352:cluster/my-eks-cluster
  name: aws@my-eks-cluster

current-context: aws@my-eks-cluster

kind: Config
preferences: {}

users:
- name: arn:aws:eks:ap-south-1:339712902352:cluster/my-eks-cluster
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1beta1
      command: aws
      args:
        - "eks"
        - "get-token"
        - "--region"
        - "ap-south-1"
        - "--cluster-name"
        - "my-eks-cluster"
      # This dynamically fetches a short-lived authentication token
```

### Key Points:

* **Authentication:**
  Instead of a static token, it uses `exec` → `aws eks get-token`, which dynamically gets credentials from AWS IAM.
* **Authorization:**
  Once authenticated, EKS uses **IAM → RBAC mapping** (via `aws-auth` ConfigMap in kube-system) to decide permissions.

---

## **2. Azure AKS – kubeconfig example**

When you run:

```bash
az aks get-credentials --resource-group my-rg --name my-aks-cluster
```

You get kubeconfig like this:

```yaml
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJ...
    server: https://my-aks-cluster-dns-123456.hcp.eastus.azmk8s.io:443
  name: my-aks-cluster

contexts:
- context:
    cluster: my-aks-cluster
    user: clusterUser_my-rg_my-aks-cluster
  name: my-aks-cluster

current-context: my-aks-cluster

kind: Config
preferences: {}

users:
- name: clusterUser_my-rg_my-aks-cluster
  user:
    auth-provider:
      name: azure
      config:
        tenant-id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        apiserver-id: "00000002-0000-0000-c000-000000000000"
        client-id: "spn-client-id-or-user-id"
        environment: "AzurePublicCloud"
```

### Key Points:

* **Authentication:**
  Uses Azure **Entra ID (formerly AAD)**. `auth-provider: azure` → handles OAuth2 tokens.
* **Authorization:**
  After login, RBAC rules in AKS (roles + rolebindings) decide what the authenticated user/service principal can do.

---

## **Comparison Table: EKS vs AKS kubeconfig**

| Field            | AWS EKS                                 | Azure AKS                             |
| ---------------- | --------------------------------------- | ------------------------------------- |
| Auth method      | `exec → aws eks get-token` (IAM-based)  | `auth-provider: azure` (AAD/Entra ID) |
| Token lifetime   | Short-lived (\~15 min)                  | Short-lived OAuth2 tokens             |
| Authorization    | IAM → RBAC mapping (aws-auth ConfigMap) | RBAC roles bound to Entra ID users    |
| Command to fetch | `aws eks update-kubeconfig`             | `az aks get-credentials`              |

---

👉 So in short:

* **kubeconfig YAML structure** is the same everywhere.
* The difference lies in **how the `user` block fetches authentication tokens** (AWS = IAM exec plugin, Azure = AAD provider).

---

👍 Let’s walk through how **AWS (EKS) + Azure (AKS)** clusters can live inside a **single kubeconfig file**, and how you switch between them.

---

## **Merged kubeconfig with AWS & Azure**

When you run:

```bash
aws eks update-kubeconfig --region ap-south-1 --name my-eks-cluster
az aks get-credentials --resource-group my-rg --name my-aks-cluster
```

Both commands add entries to the same `~/.kube/config`. Example:

```yaml
apiVersion: v1
kind: Config

clusters:
- name: arn:aws:eks:ap-south-1:339712902352:cluster/my-eks-cluster
  cluster:
    server: https://ABCDE12345.gr7.ap-south-1.eks.amazonaws.com
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJ...

- name: my-aks-cluster
  cluster:
    server: https://my-aks-cluster-dns-123456.hcp.eastus.azmk8s.io:443
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJ...

users:
- name: arn:aws:eks:ap-south-1:339712902352:cluster/my-eks-cluster
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1beta1
      command: aws
      args:
        - eks
        - get-token
        - --region
        - ap-south-1
        - --cluster-name
        - my-eks-cluster

- name: clusterUser_my-rg_my-aks-cluster
  user:
    auth-provider:
      name: azure
      config:
        tenant-id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        apiserver-id: "00000002-0000-0000-c000-000000000000"
        client-id: "spn-client-id-or-user-id"
        environment: "AzurePublicCloud"

contexts:
- name: aws@my-eks-cluster
  context:
    cluster: arn:aws:eks:ap-south-1:339712902352:cluster/my-eks-cluster
    user: arn:aws:eks:ap-south-1:339712902352:cluster/my-eks-cluster
    namespace: dev

- name: azure@my-aks-cluster
  context:
    cluster: my-aks-cluster
    user: clusterUser_my-rg_my-aks-cluster
    namespace: app

current-context: aws@my-eks-cluster
```

---

## **Explanation**

* **clusters** → contains API server + CA data for **both AWS & Azure** clusters.
* **users** → one entry for AWS (IAM exec plugin) and one for Azure (AAD auth).
* **contexts** → map each cluster + user combo into a usable “shortcut”.
* **current-context** → whichever cluster you’re currently targeting.

---

## **Switching Between Clusters**

```bash
# View all contexts
kubectl config get-contexts

# Switch to AWS EKS
kubectl config use-context aws@my-eks-cluster

# Switch to Azure AKS
kubectl config use-context azure@my-aks-cluster

# Verify which cluster you're talking to
kubectl config current-context
kubectl cluster-info
```

---

## **Tip: Keep them separate too**

Sometimes you don’t want to merge. You can:

* Use `--kubeconfig` flag:

  ```bash
  kubectl get pods --kubeconfig ~/.kube/eks-config
  ```
* Or set `KUBECONFIG` env var for multiple files:

  ```bash
  export KUBECONFIG=~/.kube/config:~/.kube/eks-config:~/.kube/aks-config
  kubectl config view --merge --flatten
  ```

---

✅ This way you can manage **multiple cloud clusters (AWS, Azure, GCP, on-prem)** all from **one kubeconfig file**.



