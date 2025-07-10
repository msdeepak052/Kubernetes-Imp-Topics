# **Kubernetes Container Log Retention & Rotation (via Kubelet Configuration)**

By default, Kubernetes does not automatically clean up container logs, which can fill up disk space. You can configure log rotation and retention using **Kubelet settings** to manage log files efficiently.

---

## **1. Log Retention & Rotation in Kubernetes**
Kubelet manages container logs via **CRI (Container Runtime Interface)**. The two key parameters for log management are:
- **`containerLogMaxSize`** → Maximum size of a log file before rotation.
- **`containerLogMaxFiles`** → Maximum number of log files per container.

### **Default Behavior (If Not Configured)**
- Logs grow indefinitely (no rotation).
- Risk of disk exhaustion.

---

## **2. Configuring Log Rotation via Kubelet**
### **Option 1: Modify Kubelet Configuration File (`kubelet-config.yaml`)**
Edit the Kubelet config file (usually at `/var/lib/kubelet/config.yaml` or `/etc/kubernetes/kubelet.conf`):

```yaml
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
containerLogMaxSize: "10Mi"  # Rotate logs when they reach 10MB
containerLogMaxFiles: 5      # Keep up to 5 rotated log files per container
```

### **Option 2: Start Kubelet with Command-Line Flags**
If using `systemd`, modify `/etc/systemd/system/kubelet.service.d/10-kubeadm.conf`:

```ini
[Service]
Environment="KUBELET_CONFIG_ARGS=--config=/var/lib/kubelet/config.yaml"
ExecStart=
ExecStart=/usr/bin/kubelet $KUBELET_KUBECONFIG_ARGS $KUBELET_CONFIG_ARGS \
  --container-log-max-size=10Mi \
  --container-log-max-files=5
```

### **Option 3: Using Kubelet ConfigMap (Dynamic Update)**
If your cluster supports dynamic Kubelet configuration:
```sh
kubectl edit cm -n kube-system kubelet-config
```
Add:
```yaml
containerLogMaxSize: "10Mi"
containerLogMaxFiles: 5
```
Then restart Kubelet:
```sh
systemctl restart kubelet
```

---

## **3. Verifying Log Rotation**
Check if logs are being rotated:
```sh
# Check Kubelet logs
journalctl -u kubelet -f

# Inspect container logs (should see rotated files like `*.log.1`, `*.log.2`)
ls -lh /var/log/pods/<namespace>_<pod>_<uid>/<container>/
```

---

## **4. Additional Log Management Strategies**
### **a) Cluster-Level Logging with Fluentd/Logrotate**
If Kubelet log rotation is insufficient, use:
- **Fluentd + Elasticsearch** (for centralized logging).
- **Logrotate** (for manual log rotation on Nodes).

Example `/etc/logrotate.d/docker`:
```
/var/log/containers/*.log {
  rotate 7
  daily
  compress
  delaycompress
  missingok
  copytruncate
}
```

### **b) Using DaemonSet for Log Cleanup**
Deploy a `CronJob` or `DaemonSet` to clean up old logs:
```yaml
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: log-cleanup
spec:
  schedule: "0 0 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: log-cleaner
            image: alpine
            command: ["find", "/var/log/pods", "-type", "f", "-mtime", "+7", "-delete"]
          restartPolicy: OnFailure
          hostPID: true
          volumes:
          - name: varlog
            hostPath:
              path: /var/log
```

---

## **5. Best Practices**
✅ **Set `containerLogMaxSize` (e.g., `10Mi`-`100Mi`)** → Prevents huge log files.  
✅ **Keep `containerLogMaxFiles` (e.g., `3`-`5`)** → Avoids too many archived logs.  
✅ **Use centralized logging (EFK stack)** for long-term storage.  
✅ **Monitor disk usage** with Prometheus/Grafana.  

---

## **Summary**
| Method | Use Case | Example |
|--------|----------|---------|
| **Kubelet Config** | Default log rotation | `containerLogMaxSize: "10Mi"` |
| **Logrotate** | Manual log management | `/etc/logrotate.d/docker` |
| **CronJob Cleanup** | Scheduled log deletion | `find /var/log/pods -mtime +7 -delete` |

Would you like help with **debugging log rotation issues** or **setting up Fluentd**?
