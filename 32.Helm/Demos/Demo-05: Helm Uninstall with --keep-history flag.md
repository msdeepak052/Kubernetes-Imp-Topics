# **Demo-05: Helm Uninstall with `--keep-history` flag** 

## 🎯 **Objective**

Learn how to:

* Uninstall a Helm release from the cluster
* Preserve the release’s **history** using the `--keep-history` flag
* Verify that historical data remains after uninstall

---

## 🧱 **Prerequisites**

| Requirement           | Command to Verify   |
| --------------------- | ------------------- |
| Helm installed        | `helm version`      |
| Kubernetes running    | `kubectl get nodes` |
| Existing Helm release | `helm list`         |

👉 If you don’t have one, reinstall a test release:

```bash
helm install my-nginx bitnami/nginx
```

---

## 🧩 **Standard Helm Uninstall Syntax**

```bash
helm uninstall <release-name> [flags]
```

### With history preservation:

```bash
helm uninstall <release-name> --keep-history
```

---

## 📘 **Syntax Explanation**

| Component        | Description                            | Example          |
| ---------------- | -------------------------------------- | ---------------- |
| `helm`           | Helm CLI command                       | —                |
| `uninstall`      | Subcommand to remove a release         | —                |
| `<release-name>` | Name of the deployed release to remove | `my-nginx`       |
| `[flags]`        | Optional parameters                    | `--keep-history` |

---

## 🧪 **Demo Steps**

### **Step 1: Verify the Installed Release**

Check the current deployment:

```bash
helm list
```

✅ Example Output:

```
NAME      	NAMESPACE	REVISION	UPDATED                                	STATUS  	CHART       	APP VERSION
my-nginx  	default  	1       	2025-10-31 20:10:30.532 +0530 IST	deployed	nginx-15.9.2	1.25.3
```

---

### **Step 2: Uninstall the Release but Keep History**

```bash
helm uninstall my-nginx --keep-history
```

✅ **Expected Output:**

```
release "my-nginx" uninstalled
```

---

### **Step 3: Verify History is Still Retained**

Even though it’s uninstalled, the release metadata remains.

```bash
helm list --all
```

✅ **Expected Output:**

```
NAME      	NAMESPACE	REVISION	UPDATED                                	STATUS    	CHART       	APP VERSION
my-nginx  	default  	1       	2025-10-31 20:10:30.532 +0530 IST	uninstalled	nginx-15.9.2	1.25.3
```

👉 Notice the **STATUS** is `uninstalled`, but it still appears because we used `--keep-history`.

---

### **Step 4: Verify in Kubernetes**

Helm removes all Kubernetes objects (pods, services, deployments), but retains metadata inside Helm’s storage (ConfigMap or Secret).

```bash
kubectl get all
```

✅ The nginx-related resources should be gone.

However, Helm’s internal data remains:

```bash
kubectl get secrets -n default | grep my-nginx
```

You’ll still see Helm release metadata (depending on your storage driver).

---

### **Step 5: Reinstall Using the Same Release Name**

If you reinstall the same release, Helm reuses and increments the revision:

```bash
helm install my-nginx bitnami/nginx
```

✅ **Check History:**

```bash
helm history my-nginx
```

**Expected Output:**

```
REVISION	UPDATED                 	STATUS      	CHART       	APP VERSION	DESCRIPTION
1       	Fri Oct 31 20:10:30 2025	uninstalled	nginx-15.9.2	1.25.3     	Uninstall complete
2       	Fri Oct 31 20:18:14 2025	deployed   	nginx-15.9.2	1.25.3     	Install complete
```

Helm remembers that Revision 1 was previously uninstalled!

---

## 📋 **Quick Syntax Reference**

| Command                                   | Description                                   |
| ----------------------------------------- | --------------------------------------------- |
| `helm uninstall <release>`                | Remove a release and its resources            |
| `helm uninstall <release> --keep-history` | Remove resources but preserve release history |
| `helm list --all`                         | Show both active and uninstalled releases     |
| `helm history <release>`                  | View release revisions                        |
| `helm install <release> <chart>`          | Reinstall a previously removed release        |

---

## 🧹 **Optional Full Cleanup**

If you want to **completely delete history** as well:

```bash
helm uninstall my-nginx
helm list --all
```

✅ The release will **no longer appear**.

---

## 📂 **Files / Resources Involved**

| File / Location                    | Purpose                                   |
| ---------------------------------- | ----------------------------------------- |
| `~/.config/helm/repositories.yaml` | Stores repo details                       |
| `Secret` in cluster                | Stores Helm release metadata (history)    |
| `values.yaml`                      | Default configuration (not modified here) |
| Kubernetes resources               | Deleted during uninstall                  |

---

## 🧠 **Summary**

| Operation                    | Command                                  | Description                 |
| ---------------------------- | ---------------------------------------- | --------------------------- |
| Uninstall normally           | `helm uninstall my-nginx`                | Deletes release and history |
| Uninstall but keep history   | `helm uninstall my-nginx --keep-history` | Keeps metadata              |
| List all (including deleted) | `helm list --all`                        | Shows uninstalled releases  |
| View history                 | `helm history my-nginx`                  | Displays previous revisions |
| Reinstall same release       | `helm install my-nginx bitnami/nginx`    | Creates new revision        |

---
