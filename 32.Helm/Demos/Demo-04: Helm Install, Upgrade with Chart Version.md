# **Demo-04: Helm Install and Upgrade with Chart Version** 

## 🎯 **Objective**

Learn how to:

* Install a specific version of a Helm chart
* Upgrade to a newer (or older) version using the `--version` flag
* Verify version history in Helm

---

## 🧱 **Prerequisites**

| Requirement        | Command to Verify   |
| ------------------ | ------------------- |
| Helm installed     | `helm version`      |
| Kubernetes running | `kubectl get nodes` |
| Bitnami repo added | `helm repo list`    |

If not already added:

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

---

## 🧩 **Standard Syntax for Versioned Install / Upgrade**

### **Install a specific chart version**

```bash
helm install <release-name> <chart> --version <chart-version>
```

### **Upgrade to a specific chart version**

```bash
helm upgrade <release-name> <chart> --version <chart-version>
```

---

## 📘 **Syntax Explanation**

| Component                   | Description                                 | Example               |
| --------------------------- | ------------------------------------------- | --------------------- |
| `helm`                      | Helm CLI command                            | —                     |
| `install / upgrade`         | Subcommand to deploy or modify chart        | `install` / `upgrade` |
| `<release-name>`            | The name of the release                     | `my-nginx`            |
| `<chart>`                   | The chart name or path                      | `bitnami/nginx`       |
| `--version <chart-version>` | Specifies which version of the chart to use | `--version 15.9.2`    |

---

## 🧪 **Demo Steps**

### **Step 1: Search for Available Chart Versions**

Check which versions of the NGINX chart are available in the Bitnami repo:

```bash
helm search repo bitnami/nginx --versions
```

✅ **Example Output:**

```
NAME            	CHART VERSION	APP VERSION	DESCRIPTION
bitnami/nginx   	15.9.2       	1.25.3     	NGINX Open Source...
bitnami/nginx   	15.8.0       	1.25.2     	NGINX Open Source...
bitnami/nginx   	15.7.0       	1.25.1     	NGINX Open Source...
```

---

### **Step 2: Install a Specific Chart Version**

Let’s install **version 15.8.0** of the NGINX chart.

```bash
helm install my-nginx bitnami/nginx --version 15.8.0
```

✅ **Expected Output:**

```
NAME: my-nginx
LAST DEPLOYED: Fri Oct 31 19:50:43 2025
NAMESPACE: default
STATUS: deployed
REVISION: 1
CHART: nginx-15.8.0
```

Verify installed release:

```bash
helm list
```

✅ Output should show:

```
NAME      	NAMESPACE	REVISION	CHART       	APP VERSION	STATUS
my-nginx  	default  	1       	nginx-15.8.0	1.25.2     	deployed
```

---

### **Step 3: Upgrade to a New Chart Version**

Now upgrade to the latest version (for example **15.9.2**):

```bash
helm upgrade my-nginx bitnami/nginx --version 15.9.2
```

✅ **Expected Output:**

```
Release "my-nginx" has been upgraded. Happy Helming!
NAME: my-nginx
LAST DEPLOYED: Fri Oct 31 20:00:10 2025
NAMESPACE: default
STATUS: deployed
REVISION: 2
CHART: nginx-15.9.2
```

---

### **Step 4: Verify Upgrade and Versions**

Check release history:

```bash
helm history my-nginx
```

✅ **Expected Output:**

```
REVISION	UPDATED                 	STATUS    	CHART       	APP VERSION	DESCRIPTION
1       	Fri Oct 31 19:50:43 2025	deployed  	nginx-15.8.0	1.25.2     	Install complete
2       	Fri Oct 31 20:00:10 2025	deployed  	nginx-15.9.2	1.25.3     	Upgrade complete
```

Check Kubernetes objects:

```bash
kubectl get pods
kubectl get svc
```

---

### **Step 5: (Optional) Roll Back to Previous Version**

If you want to revert:

```bash
helm rollback my-nginx 1
```

✅ Output:

```
Rollback was a success! Happy Helming!
```

Confirm rollback:

```bash
helm history my-nginx
```

---

## 📋 **Quick Syntax Reference**

| Command                                          | Purpose                          |
| ------------------------------------------------ | -------------------------------- |
| `helm search repo <chart> --versions`            | List available chart versions    |
| `helm install <release> <chart> --version <ver>` | Install a specific version       |
| `helm upgrade <release> <chart> --version <ver>` | Upgrade to a specific version    |
| `helm history <release>`                         | Show past revisions              |
| `helm rollback <release> <rev>`                  | Roll back to a previous revision |

---

## 🧹 **Cleanup**

After testing:

```bash
helm uninstall my-nginx
```

---

## 📂 **Files Involved**

| File / Location      | Purpose                                 |
| -------------------- | --------------------------------------- |
| `values.yaml`        | Default configuration per chart version |
| `.tgz` chart package | Downloaded from repo (version-specific) |
| Helm release secret  | Stores revision history in cluster      |
| `repositories.yaml`  | Maintains repo info                     |

---

## 🧠 **Summary**

| Operation                      | Command Example                                        | Description                |
| ------------------------------ | ------------------------------------------------------ | -------------------------- |
| Install specific chart version | `helm install my-nginx bitnami/nginx --version 15.8.0` | Installs desired version   |
| Upgrade chart version          | `helm upgrade my-nginx bitnami/nginx --version 15.9.2` | Moves to newer version     |
| View release history           | `helm history my-nginx`                                | Shows all revisions        |
| Rollback                       | `helm rollback my-nginx 1`                             | Reverts to earlier version |

---
