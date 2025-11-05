# ⏰ CronJobs in Kubernetes

## 🔹 What is a CronJob?

* A **CronJob** is a Kubernetes resource that runs **Jobs on a scheduled time** (like Linux `cron`).
* It’s built on top of **Jobs**, which ensure tasks run to completion.
* CronJobs are used when you want **periodic or scheduled tasks** inside your cluster.

---

## 🔹 Why use CronJobs?

Real-world use cases:

1. **Database Backups**

   * Run a job every night at 2 AM to dump DB data to S3.
2. **Log Rotation / Cleanup**

   * Clean temporary files or logs from nodes.
3. **Batch Data Processing**

   * Run a script to aggregate data hourly/daily.
4. **Email / Notifications**

   * Send periodic system reports.
5. **Health Check Scripts**

   * Run diagnostics and alert jobs regularly.

---

## 🔹 Important Fields in CronJob YAML

* `schedule`: cron expression (`"*/5 * * * *"` = every 5 minutes).
* `jobTemplate`: defines the Job spec to run.
* `concurrencyPolicy`:

  * `Allow` (default) → multiple jobs can run in parallel.
  * `Forbid` → skips if previous job is still running.
  * `Replace` → cancels running job and replaces with new one.
* `successfulJobsHistoryLimit` → how many completed jobs to keep.
* `failedJobsHistoryLimit` → how many failed jobs to keep.
* `startingDeadlineSeconds` → if job missed schedule, how long to start late.

---
> Let’s **monitor your CronJob (`date-printer`) step by step**. I’ll show you how to confirm it’s working, how to check its Jobs/Pods, and how to debug if needed.

---

# 🔍 Steps to Check & Monitor CronJob

## ✅ 1. Verify CronJob is Created

```bash
kubectl get cronjob
```

Expected output:

```
NAME           SCHEDULE      SUSPEND   ACTIVE   LAST SCHEDULE   AGE
date-printer   */1 * * * *   False     0        <timestamp>     1m
```

👉 Look at:

* **SCHEDULE** → `"*/1 * * * *"` (every 1 min ✅)
* **LAST SCHEDULE** → shows when it last triggered a job.

---

## ✅ 2. Check Details of the CronJob

```bash
kubectl describe cronjob date-printer
```

Things to look at:

* `Schedule`
* `Concurrency Policy`
* `Last Schedule Time`
* Any events (e.g., scheduling failures).

---

## ✅ 3. List Jobs Created by the CronJob

Every run creates a **Job**:

```bash
kubectl get jobs --watch
```

You’ll see jobs like:

```
NAME                     COMPLETIONS   DURATION   AGE
date-printer-28272643    1/1           5s         1m
date-printer-28272644    1/1           4s         2m
```

👉 `1/1` completions = job finished successfully.

---

## ✅ 4. Check Pods Spawned by Jobs

Each Job creates one or more Pods:

```bash
kubectl get pods --selector=job-name=<job-name>
```

Example:

```
NAME                           READY   STATUS      RESTARTS   AGE
date-printer-28272643-xyz12    0/1     Completed   0          1m
```

---

## ✅ 5. Check Pod Logs (Output of CronJob)

```bash
kubectl logs <pod-name>
```

Example output:

```
Mon Sep 19 15:41:12 UTC 2025
Hello from Kubernetes CronJob!
```

👉 This confirms your CronJob executed successfully.

---

## ✅ 6. Monitor in Real Time

* Watch Jobs:

  ```bash
  kubectl get jobs --watch
  ```
* Watch Pods:

  ```bash
  kubectl get pods --watch
  ```
* Stream logs (if multiple jobs are running):

  ```bash
  kubectl logs -f job/<job-name>
  ```

---

## ✅ 7. Trigger Manually (Optional for Testing)

Instead of waiting for 1 min, you can manually trigger:

```bash
kubectl create job --from=cronjob/date-printer manual-test
kubectl logs -f job/manual-test
```

---

## ✅ 8. Clean Up Old Jobs/Pods

By default, CronJobs keep history. You can remove old runs:

```bash
kubectl delete job --selector=job-name=date-printer
kubectl delete pod --selector=job-name=date-printer
```

Or set limits in YAML:

```yaml
successfulJobsHistoryLimit: 3
failedJobsHistoryLimit: 1
```

---

# ⚡ Quick Checklist for Monitoring

1. `kubectl get cronjob` → check schedule + last schedule time
2. `kubectl get jobs` → see Jobs created
3. `kubectl get pods` → see Pods spawned
4. `kubectl logs <pod>` → check output
5. `kubectl describe cronjob` → check events if it’s not running

---



## 🔹 Example 1: Simple CronJob (prints date every minute)

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: date-printer
spec:
  schedule: "*/1 * * * *"   # every 1 minute
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: date
            image: busybox
            args:
            - /bin/sh
            - -c
            - date; echo "Hello from Kubernetes CronJob!"
          restartPolicy: OnFailure
```

👉 Run this, and every minute a Pod will run, print date, then exit.

<img width="1163" height="847" alt="image" src="https://github.com/user-attachments/assets/26dfc870-fde9-4801-b7ed-786443bf9bd5" />

<img width="700" height="179" alt="image" src="https://github.com/user-attachments/assets/50285401-48b2-4a40-8515-e6ac56144d56" />

<img width="1265" height="224" alt="image" src="https://github.com/user-attachments/assets/3666b75b-a7c6-4e1d-acbd-d9d4bf0cb6c7" />

<img width="1162" height="208" alt="image" src="https://github.com/user-attachments/assets/8d64ec7a-1d90-4d2e-aef0-dc282c85a7b7" />

<img width="1163" height="209" alt="image" src="https://github.com/user-attachments/assets/88705551-e1dd-4dbe-a554-64fa214343a7" />


---

## 🔹 Example 2: Real-Life CronJob (Database Backup to S3)

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: db-backup
  namespace: prod
spec:
  schedule: "0 2 * * *"   # Run at 2 AM daily
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: bitnami/kubectl:latest
            command: ["/bin/sh", "-c"]
            args:
              - >
                pg_dump -h mydb -U admin mydb > /backup/db-$(date +%F).sql &&
                aws s3 cp /backup/db-$(date +%F).sql s3://mybucket/backups/
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-secret
                  key: password
            volumeMounts:
            - name: backup-vol
              mountPath: /backup
          restartPolicy: OnFailure
          volumes:
          - name: backup-vol
            emptyDir: {}
```

👉 Runs at **2 AM**, dumps DB, and uploads backup to S3.

---

## 🔹 Example 3: Cleanup Old Logs

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: log-cleaner
spec:
  schedule: "0 */6 * * *"   # every 6 hours
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: cleaner
            image: busybox
            command: ["/bin/sh", "-c"]
            args:
              - "find /var/log -type f -mtime +7 -delete"
          restartPolicy: OnFailure
```

👉 Cleans logs older than **7 days** every **6 hours**.

---

## 🔹 Useful Commands

```bash
# List CronJobs
kubectl get cronjob

# Describe a CronJob
kubectl describe cronjob date-printer

# See Jobs created by CronJob
kubectl get jobs

# See Pods created by those Jobs
kubectl get pods --selector=job-name=<job-name>

# Manually trigger CronJob (v1.29+)
kubectl create job --from=cronjob/date-printer manual-test
```

---

✅ Summary:

* **CronJob = Scheduled Job**
* Useful for **backups, cleanups, automation**
* Key configs = `schedule`, `concurrencyPolicy`, `successfulJobsHistoryLimit`, `failedJobsHistoryLimit`

---


# 🔍 Debugging CronJobs in Kubernetes

## ✅ 1. Check if the CronJob is created properly

```bash
kubectl get cronjob
kubectl describe cronjob <cronjob-name>
```

* Verify **`schedule`** field (cron expression is valid).
* Look at **`Last Schedule Time`** in the describe output.

  * If it’s blank → CronJob is not being scheduled at all.
  * If it shows but no Job is created → check controller logs.

---

## ✅ 2. Check Jobs created by the CronJob

```bash
kubectl get jobs --watch
kubectl describe job <job-name>
```

* If Jobs are not created → CronJob controller may not be working (check kube-controller-manager).
* If Jobs are created but not completing → problem is inside the Pod.

---

## ✅ 3. Check Pods spawned by Jobs

```bash
kubectl get pods --selector=job-name=<job-name>
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

* Look for **ImagePullBackOff, CrashLoopBackOff, Pending** states.
* Logs will tell you if script/command failed.

---

## ✅ 4. Check for Common Issues

### ❌ Wrong schedule expression

* Kubernetes uses **standard cron format**:

  ```
  ┌───────────── minute (0 - 59)
  │ ┌───────────── hour (0 - 23)
  │ │ ┌───────────── day of month (1 - 31)
  │ │ │ ┌───────────── month (1 - 12)
  │ │ │ │ ┌───────────── day of week (0 - 6) (Sunday=0)
  │ │ │ │ │
  * * * * *
  ```

Example: `"*/5 * * * *"` = every 5 minutes.

---

### ❌ Concurrency policy blocking jobs

If a job is still running and `concurrencyPolicy: Forbid` is set, the next one will **not start**.
Check in `kubectl describe cronjob <name>` under `Concurrency Policy`.

---

### ❌ Missed schedule

* If the controller was down or job was delayed, it may miss the run.
* You can allow late starts with:

  ```yaml
  startingDeadlineSeconds: 200
  ```

---

### ❌ Image or command failures

* If container exits too quickly or command is invalid → Pod fails.
* Always set `restartPolicy: OnFailure` for jobs.

---

## ✅ 5. Manually Trigger CronJob for Testing

```bash
kubectl create job --from=cronjob/<cronjob-name> test-run
kubectl logs -f job/test-run
```

👉 This helps you debug without waiting for schedule.

---

## ✅ 6. Check Controller Logs (Advanced)

If CronJob itself is not creating Jobs, check the **controller logs**:

```bash
kubectl -n kube-system logs <kube-controller-manager-pod>
```

Look for errors like scheduling failures or RBAC permission issues.

---

## ✅ 7. Best Practices for Reliability

* Always set:

  ```yaml
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  restartPolicy: OnFailure
  ```
* Test your command in a standalone Pod **before** putting into CronJob.
* Use **ConfigMaps/Secrets** for environment variables.
* Use **monitoring (Prometheus/Grafana)** to track CronJob runs.

---

⚡ Example Debugging Flow (Real Life):

1. CronJob didn’t run → `kubectl describe cronjob` → schedule is correct.
2. Job was created → but Pod in `CrashLoopBackOff`.
3. `kubectl logs <pod>` → shows script error → fixed shell command.
4. Retested with `kubectl create job --from=cronjob/db-backup manual-run`.
5. Worked ✅ → Now wait for real schedule.

---
