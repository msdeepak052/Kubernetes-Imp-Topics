# 🔹 What is RBAC in Kubernetes?

**Role-Based Access Control (RBAC)** in Kubernetes is a method to regulate access to cluster resources based on **roles** and **permissions**.
It decides:

* **Who** (user/service account/group) can
* **Do What** (verbs: get, list, create, delete, etc.)
* **On Which Resources** (pods, deployments, secrets, etc.)
* **In Which Scope** (namespace-specific or cluster-wide)

---

# 🔹 RBAC Components

RBAC in Kubernetes has **four main components**:

1. **Role** – Defines permissions **within a namespace**.
2. **ClusterRole** – Defines permissions **across the entire cluster** (all namespaces).
3. **RoleBinding** – Assigns a Role to a user or ServiceAccount in a namespace.
4. **ClusterRoleBinding** – Assigns a ClusterRole to a user or ServiceAccount cluster-wide.

👉 Additionally, **ServiceAccount** is the identity that pods use to interact with the API server.

---

# 🔹 Example 1: Role + RoleBinding (Namespace Scope)

```yaml
# Role - namespace level permission
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: dev
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
```

```yaml
# RoleBinding - binding Role to a ServiceAccount
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods-binding
  namespace: dev
subjects:
- kind: ServiceAccount
  name: dev-sa   # ServiceAccount name
  namespace: dev # must match
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

✅ **Usage:**
This allows `ServiceAccount: dev-sa` in `dev` namespace to only **read pods** in `dev`.

---

# 🔹 Example 2: ClusterRole + ClusterRoleBinding (Cluster Scope)

```yaml
# ClusterRole - cluster-wide permission
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: pod-reader-all
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
```

```yaml
# ClusterRoleBinding - binding ClusterRole to ServiceAccount
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: read-pods-all-binding
subjects:
- kind: ServiceAccount
  name: dev-sa
  namespace: dev
roleRef:
  kind: ClusterRole
  name: pod-reader-all
  apiGroup: rbac.authorization.k8s.io
```

✅ **Usage:**
This allows the same `dev-sa` service account to **read pods in all namespaces**, not just `dev`.

---

# 🔹 Example 3: ServiceAccount

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: dev-sa
  namespace: dev
```

✅ **Usage:**

* Pods running with `serviceAccountName: dev-sa` will use this identity.
* Permissions are given via **Role/ClusterRole + Binding**.

---

# 🔹 Why use each?

* **Role** → For namespace-scoped apps (e.g., developers working only in `dev` namespace).
* **ClusterRole** → For cluster-wide resources (nodes, PVs) or when permissions must apply across namespaces.
* **ServiceAccount** → For pods/applications that need controlled access to the API server instead of giving them cluster-admin rights.

👉 Best practice: **Use ServiceAccounts with the least privilege needed**, instead of binding ClusterRole to users directly.

---

# 🔹 Important Terms in YAML

When configuring RBAC, always remember these:

1. **apiGroups** – Defines which API group the resource belongs to.

   * `""` = core group (pods, services, configmaps, secrets)
   * `apps` = deployments, replicasets
   * `rbac.authorization.k8s.io` = RBAC resources

2. **resources** – The Kubernetes objects (pods, deployments, secrets, etc.).

3. **verbs** – Actions allowed:

   * `get`, `list`, `watch` → Read operations
   * `create`, `update`, `patch`, `delete` → Write operations
   * `*` → All actions

4. **subjects** – Who is getting the access (User, Group, or ServiceAccount).

5. **roleRef** – Which Role/ClusterRole is being assigned.

   * Must match exactly (`kind`, `name`, `apiGroup`).

6. **namespace** – Very important!

   * Roles and RoleBindings are **namespace-bound**.
   * ClusterRole and ClusterRoleBinding are **not namespace-bound**.

---

✅ Summary:

* Use **Role + RoleBinding** for namespace-specific permissions.
* Use **ClusterRole + ClusterRoleBinding** for cluster-wide or non-namespace resources.
* Use **ServiceAccounts** instead of giving apps `kubeconfig` access.
* Always configure `apiGroups`, `resources`, `verbs`, `subjects`, and `roleRef` carefully.

---

# 🔹 Step 1: Create a ServiceAccount

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: dev-sa
  namespace: dev
```

---

# 🔹 Step 2: Create a Role (namespace-level)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: dev
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]
```

---

# 🔹 Step 3: Bind Role to ServiceAccount

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods-binding
  namespace: dev
subjects:
- kind: ServiceAccount
  name: dev-sa
  namespace: dev
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

---

# 🔹 Step 4: Create a Pod that Uses This ServiceAccount

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-rbac
  namespace: dev
spec:
  serviceAccountName: dev-sa   # 👈 This pod runs as dev-sa
  containers:
  - name: curl
    image: curlimages/curl:latest
    command: ["sleep", "3600"]
```

---

# 🔹 Step 5: Test Access from Inside Pod

Once pod is running:

```bash
kubectl exec -it -n dev pod-with-rbac -- sh
```

Inside pod, try:

```bash
# Allowed by Role
curl -k -H "Authorization: Bearer $(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" \
https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_SERVICE_PORT/api/v1/namespaces/dev/pods

# Not allowed (denied if Role doesn’t permit)
curl -k -H "Authorization: Bearer $(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" \
https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_SERVICE_PORT/api/v1/namespaces/dev/secrets
```

✅ You’ll see pods listing works but secrets access is **forbidden**, since our Role only allows `pods get,list`.

---

# 🔹 Flow Recap

1. **Pod** runs as → `ServiceAccount`
2. **ServiceAccount** is linked via → `RoleBinding`
3. **Role** defines → permissions in that namespace

---
> There is a *new feature* in Kubernetes **v1.34**, where **ServiceAccount tokens** are integrated with kubelet credential providers for **image pulling**, reducing the need for `imagePullSecrets`. ([Kubernetes][1])

Let me explain the concept, then show a sample YAML, and highlight what changes vs the old way.

---

## 🔍 What’s Changing in Kubernetes 1.34

* In previous Kubernetes versions, if you wanted to pull images from a **private registry**, you needed to create a **docker-registry Secret** and reference it via `imagePullSecrets` in Pod spec, or attach it to a ServiceAccount so pods using that ServiceAccount can use it.
* In v1.34, an enhancement (KEP-4412: *Projected service account tokens for Kubelet image credential providers*) allows the kubelet to request **short-lived, pod-scoped ServiceAccount tokens** which are used to authenticate to registries. This can replace long-lived `imagePullSecrets`. ([Kubernetes][2])
* This feature is in **beta** and is expected to be enabled by default in v1.34. ([Kubernetes][2])
* As a result, you may no longer explicitly set `imagePullSecrets` in pods—your ServiceAccount + kubelet’s credential provider logic can do the pull for you.

---

## 🧩 Sample YAML (v1.34) Using ServiceAccount Token for Image Pull (without imagePullSecrets)

Here’s a simplified example:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: sa-puller
  namespace: dev

---

apiVersion: v1
kind: Pod
metadata:
  name: app-using-sa-pull
  namespace: dev
spec:
  serviceAccountName: sa-puller
  containers:
  - name: app
    # private registry image
    image: myprivateregistry.example.com/myorg/myapp:latest
    # **no** imagePullSecrets specified here
```

**Key points / what happens:**

* The Pod references `serviceAccountName: sa-puller`.
* You do **not** list `imagePullSecrets` in the Pod spec.
* The kubelet, via the new credential provider integration, will use the **projected ServiceAccount token** for registry authentication.
* The token is **short-lived**, automatically rotated, and scoped to that Pod.

You might also need to configure the kubelet / credential provider settings so that it knows how to exchange the token for the registry credentials. (That configuration is outside the YAML above.)

---

## ⚖️ Comparison: Old vs New

| Aspect                  | Old Way (pre-1.34)                                               | New Way (v1.34 with SA token integration)                  |
| ----------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------- |
| imagePullSecrets in Pod | Required (or inherited via ServiceAccount) for private registry  | Not needed in Pod spec                                     |
| Secret lifetime         | Often long-lived                                                 | Token is short-lived, rotated automatically                |
| Management overhead     | You must manage secrets, update them, patch pods/ServiceAccounts | Less secret sprawl, fewer manual patch operations          |
| Security                | Risk of secret leakage                                           | Tighter, per-pod credential scoping                        |
| Compatibility           | Works in all stable releases                                     | Requires Kubernetes ≥ 1.34 with the feature enabled (beta) |

---

## ✅ Why This Is Better (and Caveats)

* **Safer credentials**: Since tokens are short-lived and scoped per pod, the blast radius if compromised is smaller.
* **Less manual config**: You don’t have to manage and propagate `imagePullSecrets` everywhere.
* **Cleaner manifests**: Pod specs become simpler—no image pull secret clutter.
* **Feature maturity**: It’s still in beta, so there might be caveats or implementation requirements (e.g. setting up the kubelet credential provider).

---

If you like, I can also show a *full working example including how the kubelet credential provider is configured*, or show a fallback if the feature is not enabled in your cluster. Do you want me to share that?

[1]: https://kubernetes.io/blog/2025/09/03/kubernetes-v1-34-sa-tokens-image-pulls-beta/?utm_source=chatgpt.com "Kubernetes v1.34: Service Account Token Integration for ..."
[2]: https://kubernetes.io/blog/2025/07/28/kubernetes-v1-34-sneak-peek/?utm_source=chatgpt.com "Kubernetes v1.34 Sneak Peek"
