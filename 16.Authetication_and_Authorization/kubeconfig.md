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

Do you want me to also show **how AWS EKS or Azure AKS generate kubeconfig** (with `aws eks update-kubeconfig` / `az aks get-credentials`) as practical cloud examples?
