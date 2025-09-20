# 🔹 **1. ConfigMaps in Kubernetes**

✅ **Definition**:

* A **ConfigMap** is used to store **non-confidential configuration data** in key-value pairs.
* Example: app settings, environment variables, file contents, command-line arguments.

✅ **Why Used?**

* Keeps config **separate from images** → don’t rebuild Docker images just to change config.
* Makes apps portable across environments (Dev, QA, Prod).

---

# 🔹 **2. Secrets in Kubernetes**

✅ **Definition**:

* A **Secret** is like a ConfigMap but used for **sensitive data** (passwords, tokens, certs).
* Data is **base64-encoded** (not fully secure by default, but better than plaintext in manifests).

✅ **Why Used?**

* Avoid storing passwords, API keys, certs inside code or images.
* Provides a controlled, safer way to pass sensitive data into Pods.

---

# 🔹 **3. How They Are Consumed in Pods**

Both **ConfigMaps** and **Secrets** can be injected into Pods in 3 ways:

1. **Environment variables**
2. **Mounted as files in volumes**
3. **Used in command-line args**

---

# 🔹 **4. Example: ConfigMap + Secret + Deployment**


```bash
echo -n "admin" | base64
echo -n "password" | base64
```
🚀 Let’s build a **full working example** so you can test **ConfigMap + Secret integration** in your local Kubernetes cluster.

---

# 🔹 **1. ConfigMap**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  APP_ENV: "production"
  APP_COLOR: "blue"
  config.json: |
    {
      "feature": "enabled",
      "version": "1.0"
    }
```

---

# 🔹 **2. Secret**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: YWRtaW4=     # base64 for "admin"
  password: cGFzc3dvcmQ= # base64 for "password"
```

---

# 🔹 **3. Deployment Using ConfigMap & Secret**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: demo
  template:
    metadata:
      labels:
        app: demo
    spec:
      containers:
      - name: demo-app
        image: nginx
        ports:
        - containerPort: 80

        # Env vars from ConfigMap
        env:
        - name: APP_ENV
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: APP_ENV
        - name: APP_COLOR
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: APP_COLOR

        # Env vars from Secret
        - name: DB_USER
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: username
        - name: DB_PASS
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password

        # Mount files from ConfigMap & Secret
        volumeMounts:
        - name: config-volume
          mountPath: /etc/config
        - name: secret-volume
          mountPath: /etc/secret

      volumes:
      - name: config-volume
        configMap:
          name: app-config
      - name: secret-volume
        secret:
          secretName: db-secret
```

---

# 🔹 **4. Service**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: demo-service
spec:
  selector:
    app: demo
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: ClusterIP
```

---

# 🔹 **5. Busybox Test Pod (to verify config/secret values)**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: busybox-test
spec:
  containers:
  - name: busybox
    image: busybox
    command: ['sh', '-c', 'sleep 3600']
```

---

# 🔹 **6. Apply Everything**

```bash
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f busybox.yaml
```

---

# 🔹 **7. Verification**

### (A) Check env variables inside Pod:

```bash
kubectl exec -it busybox-test -- sh
echo $APP_ENV     # production
echo $APP_COLOR   # blue
echo $DB_USER     # admin
echo $DB_PASS     # password
```

### (B) Check mounted files:

```sh
cat /etc/config/config.json
cat /etc/secret/username
cat /etc/secret/password
```

---

✅ This way you can **see live how ConfigMaps and Secrets are injected** into a Pod both as env vars and files.

---


# 🔹 **6. Real-Life Uses**

* ConfigMaps → app tuning (feature flags, API URLs, log levels).
* Secrets → database credentials, TLS certs, Docker registry credentials.
* Deployments → combine both to inject runtime configs securely.

---

✅ **Summary:**

* **ConfigMaps** = plain configs (non-sensitive).
* **Secrets** = sensitive configs (base64-encoded).
* **Deployment** consumes them as **env vars** or **mounted files**.

---
