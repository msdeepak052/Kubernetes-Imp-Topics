## Kubernetes Operators: Detailed Explanation

### What Problem Do Operators Solve?

**Traditional Kubernetes Limitations:**
- Kubernetes natively manages stateless applications well
- Built-in resources (Deployments, Services, etc.) work great for simple applications
- However, stateful applications and complex systems require human operational knowledge

**Specific Problems:**

1. **Stateful Application Complexity**
   - Databases, message queues, caching systems need special handling
   - Backup/restore procedures
   - Scaling up/down with data safety
   - Version upgrades with migration strategies

2. **Application-Specific Operational Knowledge**
   - How to safely scale a database cluster
   - How to perform zero-downtime upgrades
   - How to recover from failures
   - How to configure replicas with proper initialization order

3. **Manual Operations**
   - Human operators needed for day-to-day management
   - Error-prone manual procedures
   - Inconsistent operations across teams

### What Are Kubernetes Operators?

**Operator Pattern:**
- Custom controllers that extend Kubernetes API
- Embed operational knowledge into software
- Use Custom Resource Definitions (CRDs) to define custom resources
- Automate complex application management

**Key Components:**
1. **Custom Resource Definition (CRD)** - Extends Kubernetes API
2. **Custom Resource (CR)** - Instance of the custom resource
3. **Custom Controller** - Control loop that watches and reconciles resources

### Why Operators Are Needed?

1. **Automate Human Operational Tasks**
   - Backup and restore procedures
   - Scaling operations
   - Version upgrades
   - Failure recovery

2. **Platform Engineering**
   - Standardize application management
   - Enable self-service for development teams
   - Enforce best practices

3. **Day 2 Operations**
   - Ongoing maintenance and management
   - Monitoring and alerting
   - Performance optimization

---
<img width="1540" height="644" alt="image" src="https://github.com/user-attachments/assets/89e4dbd2-622f-4dc6-8ea8-93b9420639eb" />


---

## Demo: Creating a Simple MySQL Operator

Let's create a basic MySQL operator that manages MySQL instances with automated backups.

### Step 1: Project Structure

Create the following directory structure:

```
mysql-operator/
├── Dockerfile
├── deploy/
│   ├── crd.yaml
│   ├── operator.yaml
│   ├── rbac.yaml
│   └── mysql-instance.yaml
├── main.go
├── go.mod
└── pkg/
    └── controller/
        └── mysql_controller.go
```

### Step 2: Custom Resource Definition (CRD)

**deploy/crd.yaml**
```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: mysqls.operators.example.com
spec:
  group: operators.example.com
  versions:
    - name: v1alpha1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                databaseName:
                  type: string
                databaseUser:
                  type: string
                storageSize:
                  type: string
                backupSchedule:
                  type: string
                mysqlVersion:
                  type: string
                  default: "8.0"
            status:
              type: object
              properties:
                phase:
                  type: string
                message:
                  type: string
                lastBackup:
                  type: string
  scope: Namespaced
  names:
    plural: mysqls
    singular: mysql
    kind: MySQL
    shortNames:
    - mysql
```

### Step 3: RBAC Permissions

**deploy/rbac.yaml**
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: mysql-operator
  namespace: mysql-operator-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: mysql-operator
rules:
- apiGroups: [""]
  resources: ["pods", "services", "persistentvolumeclaims", "secrets", "configmaps"]
  verbs: ["*"]
- apiGroups: ["apps"]
  resources: ["deployments", "statefulsets"]
  verbs: ["*"]
- apiGroups: ["batch"]
  resources: ["cronjobs", "jobs"]
  verbs: ["*"]
- apiGroups: ["operators.example.com"]
  resources: ["mysqls"]
  verbs: ["*"]
- apiGroups: ["operators.example.com"]
  resources: ["mysqls/status", "mysqls/finalizers"]
  verbs: ["update"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: mysql-operator
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: mysql-operator
subjects:
- kind: ServiceAccount
  name: mysql-operator
  namespace: mysql-operator-system
```

### Step 4: Operator Deployment

**deploy/operator.yaml**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql-operator
  namespace: mysql-operator-system
  labels:
    app: mysql-operator
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mysql-operator
  template:
    metadata:
      labels:
        app: mysql-operator
    spec:
      serviceAccountName: mysql-operator
      containers:
      - name: operator
        image: mysql-operator:latest
        imagePullPolicy: IfNotPresent
        env:
        - name: WATCH_NAMESPACE
          value: ""
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: OPERATOR_NAME
          value: "mysql-operator"
```

### Step 5: Go Module File

**go.mod**
```go
module mysql-operator

go 1.19

require (
    k8s.io/apimachinery v0.26.0
    k8s.io/client-go v0.26.0
    sigs.k8s.io/controller-runtime v0.14.1
)
```

### Step 6: Main Operator Code

**main.go**
```go
package main

import (
    "flag"
    "os"
    "time"

    "k8s.io/apimachinery/pkg/runtime"
    utilruntime "k8s.io/apimachinery/pkg/util/runtime"
    clientgoscheme "k8s.io/client-go/kubernetes/scheme"
    _ "k8s.io/client-go/plugin/pkg/client/auth"
    ctrl "sigs.k8s.io/controller-runtime"
    "sigs.k8s.io/controller-runtime/pkg/healthz"
    "sigs.k8s.io/controller-runtime/pkg/log/zap"

    operatorsv1alpha1 "mysql-operator/pkg/apis/operators/v1alpha1"
    "mysql-operator/pkg/controller"
)

var (
    scheme   = runtime.NewScheme()
    setupLog = ctrl.Log.WithName("setup")
)

func init() {
    utilruntime.Must(clientgoscheme.AddToScheme(scheme))
    utilruntime.Must(operatorsv1alpha1.AddToScheme(scheme))
}

func main() {
    var metricsAddr string
    var enableLeaderElection bool
    var probeAddr string
    flag.StringVar(&metricsAddr, "metrics-bind-address", ":8080", "The address the metric endpoint binds to.")
    flag.StringVar(&probeAddr, "health-probe-bind-address", ":8081", "The address the probe endpoint binds to.")
    flag.BoolVar(&enableLeaderElection, "leader-elect", false,
        "Enable leader election for controller manager. "+
            "Enabling this will ensure there is only one active controller manager.")
    opts := zap.Options{
        Development: true,
    }
    opts.BindFlags(flag.CommandLine)
    flag.Parse()

    ctrl.SetLogger(zap.New(zap.UseFlagOptions(&opts)))

    mgr, err := ctrl.NewManager(ctrl.GetConfigOrDie(), ctrl.Options{
        Scheme:                 scheme,
        MetricsBindAddress:     metricsAddr,
        Port:                   9443,
        HealthProbeBindAddress: probeAddr,
        LeaderElection:         enableLeaderElection,
        LeaderElectionID:       "mysql-operator-lock",
    })
    if err != nil {
        setupLog.Error(err, "unable to start manager")
        os.Exit(1)
    }

    if err = (&controller.MySQLReconciler{
        Client: mgr.GetClient(),
        Scheme: mgr.GetScheme(),
    }).SetupWithManager(mgr); err != nil {
        setupLog.Error(err, "unable to create controller", "controller", "MySQL")
        os.Exit(1)
    }

    if err := mgr.AddHealthzCheck("healthz", healthz.Ping); err != nil {
        setupLog.Error(err, "unable to set up health check")
        os.Exit(1)
    }
    if err := mgr.AddReadyzCheck("readyz", healthz.Ping); err != nil {
        setupLog.Error(err, "unable to set up ready check")
        os.Exit(1)
    }

    setupLog.Info("starting manager")
    if err := mgr.Start(ctrl.SetupSignalHandler()); err != nil {
        setupLog.Error(err, "problem running manager")
        os.Exit(1)
    }
}
```

### Step 7: Controller Implementation

**pkg/controller/mysql_controller.go**
```go
package controller

import (
    "context"
    "fmt"
    "time"

    "k8s.io/apimachinery/pkg/api/errors"
    "k8s.io/apimachinery/pkg/runtime"
    ctrl "sigs.k8s.io/controller-runtime"
    "sigs.k8s.io/controller-runtime/pkg/client"
    "sigs.k8s.io/controller-runtime/pkg/log"

    corev1 "k8s.io/api/core/v1"
    appsv1 "k8s.io/api/apps/v1"
    batchv1 "k8s.io/api/batch/v1"
    batchv1beta1 "k8s.io/api/batch/v1beta1"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"

    operatorsv1alpha1 "mysql-operator/pkg/apis/operators/v1alpha1"
)

type MySQLReconciler struct {
    client.Client
    Scheme *runtime.Scheme
}

func (r *MySQLReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    log := log.FromContext(ctx)

    // Fetch the MySQL instance
    mysql := &operatorsv1alpha1.MySQL{}
    if err := r.Get(ctx, req.NamespacedName, mysql); err != nil {
        if errors.IsNotFound(err) {
            log.Info("MySQL resource not found. Ignoring since object must be deleted")
            return ctrl.Result{}, nil
        }
        log.Error(err, "Failed to get MySQL")
        return ctrl.Result{}, err
    }

    // Check if the MySQL instance is being deleted
    if mysql.DeletionTimestamp != nil {
        return r.handleDeletion(ctx, mysql)
    }

    // Add finalizer if not present
    if !containsString(mysql.Finalizers, "mysql.operators.example.com/finalizer") {
        mysql.Finalizers = append(mysql.Finalizers, "mysql.operators.example.com/finalizer")
        if err := r.Update(ctx, mysql); err != nil {
            return ctrl.Result{}, err
        }
    }

    // Reconcile MySQL deployment
    if err := r.reconcileDeployment(ctx, mysql); err != nil {
        return ctrl.Result{}, err
    }

    // Reconcile MySQL service
    if err := r.reconcileService(ctx, mysql); err != nil {
        return ctrl.Result{}, err
    }

    // Reconcile MySQL secret
    if err := r.reconcileSecret(ctx, mysql); err != nil {
        return ctrl.Result{}, err
    }

    // Reconcile backup CronJob if schedule is specified
    if mysql.Spec.BackupSchedule != "" {
        if err := r.reconcileBackupCronJob(ctx, mysql); err != nil {
            return ctrl.Result{}, err
        }
    }

    // Update status
    mysql.Status.Phase = "Ready"
    mysql.Status.Message = "MySQL instance is running"
    mysql.Status.LastBackup = time.Now().Format(time.RFC3339)
    if err := r.Status().Update(ctx, mysql); err != nil {
        log.Error(err, "Failed to update MySQL status")
        return ctrl.Result{}, err
    }

    return ctrl.Result{}, nil
}

func (r *MySQLReconciler) reconcileDeployment(ctx context.Context, mysql *operatorsv1alpha1.MySQL) error {
    log := log.FromContext(ctx)
    
    deployment := &appsv1.Deployment{
        ObjectMeta: metav1.ObjectMeta{
            Name:      fmt.Sprintf("mysql-%s", mysql.Name),
            Namespace: mysql.Namespace,
        },
    }

    op, err := ctrl.CreateOrUpdate(ctx, r.Client, deployment, func() error {
        deployment.Labels = map[string]string{
            "app": "mysql",
            "mysql-instance": mysql.Name,
        }
        
        deployment.Spec = appsv1.DeploymentSpec{
            Replicas: func() *int32 { i := int32(1); return &i }(),
            Selector: &metav1.LabelSelector{
                MatchLabels: map[string]string{
                    "app": "mysql",
                    "mysql-instance": mysql.Name,
                },
            },
            Template: corev1.PodTemplateSpec{
                ObjectMeta: metav1.ObjectMeta{
                    Labels: map[string]string{
                        "app": "mysql",
                        "mysql-instance": mysql.Name,
                    },
                },
                Spec: corev1.PodSpec{
                    Containers: []corev1.Container{
                        {
                            Name:  "mysql",
                            Image: fmt.Sprintf("mysql:%s", mysql.Spec.MysqlVersion),
                            Env: []corev1.EnvVar{
                                {
                                    Name:  "MYSQL_ROOT_PASSWORD",
                                    ValueFrom: &corev1.EnvVarSource{
                                        SecretKeyRef: &corev1.SecretKeySelector{
                                            LocalObjectReference: corev1.LocalObjectReference{
                                                Name: fmt.Sprintf("mysql-secret-%s", mysql.Name),
                                            },
                                            Key: "password",
                                        },
                                    },
                                },
                                {
                                    Name:  "MYSQL_DATABASE",
                                    Value: mysql.Spec.DatabaseName,
                                },
                                {
                                    Name:  "MYSQL_USER",
                                    Value: mysql.Spec.DatabaseUser,
                                },
                            },
                            Ports: []corev1.ContainerPort{
                                {
                                    ContainerPort: 3306,
                                },
                            },
                            VolumeMounts: []corev1.VolumeMount{
                                {
                                    Name:      "mysql-data",
                                    MountPath: "/var/lib/mysql",
                                },
                            },
                        },
                    },
                    Volumes: []corev1.Volume{
                        {
                            Name: "mysql-data",
                            VolumeSource: corev1.VolumeSource{
                                PersistentVolumeClaim: &corev1.PersistentVolumeClaimVolumeSource{
                                    ClaimName: fmt.Sprintf("mysql-pvc-%s", mysql.Name),
                                },
                            },
                        },
                    },
                },
            },
        }
        return ctrl.SetControllerReference(mysql, deployment, r.Scheme)
    })

    if err != nil {
        log.Error(err, "Failed to create/update Deployment")
        return err
    }
    
    if op != ctrl.OperationResultNone {
        log.Info("Deployment successfully reconciled", "operation", op)
    }
    
    return nil
}

func (r *MySQLReconciler) reconcileService(ctx context.Context, mysql *operatorsv1alpha1.MySQL) error {
    service := &corev1.Service{
        ObjectMeta: metav1.ObjectMeta{
            Name:      fmt.Sprintf("mysql-%s", mysql.Name),
            Namespace: mysql.Namespace,
        },
    }

    op, err := ctrl.CreateOrUpdate(ctx, r.Client, service, func() error {
        service.Spec = corev1.ServiceSpec{
            Selector: map[string]string{
                "app": "mysql",
                "mysql-instance": mysql.Name,
            },
            Ports: []corev1.ServicePort{
                {
                    Port: 3306,
                    TargetPort: intstr.FromInt(3306),
                },
            },
        }
        return ctrl.SetControllerReference(mysql, service, r.Scheme)
    })

    if err != nil {
        return err
    }
    
    log.FromContext(ctx).Info("Service reconciled", "operation", op)
    return nil
}

func (r *MySQLReconciler) reconcileSecret(ctx context.Context, mysql *operatorsv1alpha1.MySQL) error {
    secret := &corev1.Secret{
        ObjectMeta: metav1.ObjectMeta{
            Name:      fmt.Sprintf("mysql-secret-%s", mysql.Name),
            Namespace: mysql.Namespace,
        },
    }

    op, err := ctrl.CreateOrUpdate(ctx, r.Client, secret, func() error {
        if secret.Data == nil {
            secret.Data = make(map[string][]byte)
        }
        if _, exists := secret.Data["password"]; !exists {
            secret.Data["password"] = []byte(generateRandomPassword(16))
        }
        return ctrl.SetControllerReference(mysql, secret, r.Scheme)
    })

    if err != nil {
        return err
    }
    
    log.FromContext(ctx).Info("Secret reconciled", "operation", op)
    return nil
}

func (r *MySQLReconciler) reconcileBackupCronJob(ctx context.Context, mysql *operatorsv1alpha1.MySQL) error {
    cronJob := &batchv1beta1.CronJob{
        ObjectMeta: metav1.ObjectMeta{
            Name:      fmt.Sprintf("mysql-backup-%s", mysql.Name),
            Namespace: mysql.Namespace,
        },
    }

    op, err := ctrl.CreateOrUpdate(ctx, r.Client, cronJob, func() error {
        cronJob.Spec = batchv1beta1.CronJobSpec{
            Schedule: mysql.Spec.BackupSchedule,
            JobTemplate: batchv1beta1.JobTemplateSpec{
                Spec: batchv1.JobSpec{
                    Template: corev1.PodTemplateSpec{
                        Spec: corev1.PodSpec{
                            Containers: []corev1.Container{
                                {
                                    Name:  "backup",
                                    Image: "mysql:8.0",
                                    Command: []string{
                                        "/bin/sh",
                                        "-c",
                                        fmt.Sprintf(
                                            "mysqldump -h mysql-%s -u %s -p${MYSQL_PASSWORD} %s > /backup/backup-$(date +%%Y%%m%%d-%%H%%M%%S).sql",
                                            mysql.Name, mysql.Spec.DatabaseUser, mysql.Spec.DatabaseName,
                                        ),
                                    },
                                    Env: []corev1.EnvVar{
                                        {
                                            Name: "MYSQL_PASSWORD",
                                            ValueFrom: &corev1.EnvVarSource{
                                                SecretKeyRef: &corev1.SecretKeySelector{
                                                    LocalObjectReference: corev1.LocalObjectReference{
                                                        Name: fmt.Sprintf("mysql-secret-%s", mysql.Name),
                                                    },
                                                    Key: "password",
                                                },
                                            },
                                        },
                                    },
                                    VolumeMounts: []corev1.VolumeMount{
                                        {
                                            Name:      "backup-storage",
                                            MountPath: "/backup",
                                        },
                                    },
                                },
                            },
                            RestartPolicy: corev1.RestartPolicyOnFailure,
                            Volumes: []corev1.Volume{
                                {
                                    Name: "backup-storage",
                                    VolumeSource: corev1.VolumeSource{
                                        PersistentVolumeClaim: &corev1.PersistentVolumeClaimVolumeSource{
                                            ClaimName: fmt.Sprintf("backup-pvc-%s", mysql.Name),
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        }
        return ctrl.SetControllerReference(mysql, cronJob, r.Scheme)
    })

    if err != nil {
        return err
    }
    
    log.FromContext(ctx).Info("Backup CronJob reconciled", "operation", op)
    return nil
}

// Helper functions
func containsString(slice []string, s string) bool {
    for _, item := range slice {
        if item == s {
            return true
        }
    }
    return false
}

func generateRandomPassword(length int) string {
    // Simple random password generation
    return "mysql-operator-password"
}

func (r *MySQLReconciler) SetupWithManager(mgr ctrl.Manager) error {
    return ctrl.NewControllerManagedBy(mgr).
        For(&operatorsv1alpha1.MySQL{}).
        Owns(&appsv1.Deployment{}).
        Owns(&corev1.Service{}).
        Owns(&corev1.Secret{}).
        Owns(&batchv1beta1.CronJob{}).
        Complete(r)
}
```

### Step 8: API Types

Create **pkg/apis/operators/v1alpha1/mysql_types.go**:
```go
package v1alpha1

import (
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// MySQLSpec defines the desired state of MySQL
type MySQLSpec struct {
    DatabaseName   string `json:"databaseName"`
    DatabaseUser   string `json:"databaseUser"`
    StorageSize    string `json:"storageSize,omitempty"`
    BackupSchedule string `json:"backupSchedule,omitempty"`
    MysqlVersion   string `json:"mysqlVersion,omitempty"`
}

// MySQLStatus defines the observed state of MySQL
type MySQLStatus struct {
    Phase      string `json:"phase,omitempty"`
    Message    string `json:"message,omitempty"`
    LastBackup string `json:"lastBackup,omitempty"`
}

//+kubebuilder:object:root=true
//+kubebuilder:subresource:status

// MySQL is the Schema for the mysqls API
type MySQL struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`

    Spec   MySQLSpec   `json:"spec,omitempty"`
    Status MySQLStatus `json:"status,omitempty"`
}

//+kubebuilder:object:root=true

// MySQLList contains a list of MySQL
type MySQLList struct {
    metav1.TypeMeta `json:",inline"`
    metav1.ListMeta `json:"metadata,omitempty"`
    Items           []MySQL `json:"items"`
}

func init() {
    SchemeBuilder.Register(&MySQL{}, &MySQLList{})
}
```

### Step 9: Dockerfile

**Dockerfile**
```dockerfile
FROM golang:1.19 as builder

WORKDIR /workspace
COPY go.mod go.mod
COPY go.sum go.sum
RUN go mod download

COPY main.go main.go
COPY pkg/ pkg/

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -o manager main.go

FROM gcr.io/distroless/static:nonroot
WORKDIR /
COPY --from=builder /workspace/manager .
USER 65532:65532

ENTRYPOINT ["/manager"]
```

### Step 10: MySQL Instance Custom Resource

**deploy/mysql-instance.yaml**
```yaml
apiVersion: operators.example.com/v1alpha1
kind: MySQL
metadata:
  name: my-mysql-instance
  namespace: default
spec:
  databaseName: myapp
  databaseUser: myuser
  storageSize: "10Gi"
  backupSchedule: "0 2 * * *"
  mysqlVersion: "8.0"
```

## Demo Execution Steps

### Prerequisites
- Kubernetes cluster (Minikube, Kind, or cloud)
- kubectl configured
- Docker installed
- Go 1.19+

### Step 1: Build and Deploy the Operator

```bash
# Create namespace
kubectl create namespace mysql-operator-system

# Build the operator image
docker build -t mysql-operator:latest .

# Load image into cluster (if using Minikube/Kind)
minikube image load mysql-operator:latest

# Deploy CRD
kubectl apply -f deploy/crd.yaml

# Deploy RBAC
kubectl apply -f deploy/rbac.yaml

# Deploy Operator
kubectl apply -f deploy/operator.yaml
```

### Step 2: Verify Operator Deployment

```bash
# Check operator pod
kubectl get pods -n mysql-operator-system

# Check CRD
kubectl get crd | grep mysql
```

### Step 3: Create MySQL Instance

```bash
# Create MySQL custom resource
kubectl apply -f deploy/mysql-instance.yaml

# Check MySQL instance
kubectl get mysqls

# Check created resources
kubectl get deployments
kubectl get services
kubectl get secrets
kubectl get cronjobs
```

### Step 4: Test the MySQL Instance

```bash
# Get the MySQL service
kubectl get svc mysql-my-mysql-instance

# Port forward to access MySQL
kubectl port-forward svc/mysql-my-mysql-instance 3306:3306

# In another terminal, connect to MySQL
mysql -h 127.0.0.1 -P 3306 -u myuser -p
# Use the generated password from the secret
```

### Step 5: Test Backup Functionality

```bash
# Manually trigger a backup job
kubectl create job --from=cronjob/mysql-backup-my-mysql-instance manual-backup

# Check backup job status
kubectl get jobs
kubectl logs job/manual-backup
```

### Step 6: Monitor Operator Logs

```bash
# Check operator logs
kubectl logs -f deployment/mysql-operator -n mysql-operator-system
```

### Step 7: Scale and Update Operations

```bash
# Update the MySQL instance
kubectl patch mysql my-mysql-instance --type='json' -p='[{"op": "replace", "path": "/spec/mysqlVersion", "value":"5.7"}]'

# Watch the operator handle the update
kubectl get pods -w
```

## Key Learning Points

1. **Operator Pattern**: Extends Kubernetes API with custom resources
2. **Declarative Management**: Users declare desired state, operator ensures actual state matches
3. **Automated Operations**: Backup, scaling, upgrades handled automatically
4. **Custom Controllers**: Watch resources and reconcile state
5. **RBAC**: Secure access to Kubernetes resources
6. **Finalizers**: Handle resource cleanup properly

This operator demonstrates how complex operational knowledge (backup strategies, safe scaling, version upgrades) can be encoded into software, making it easier to manage stateful applications in Kubernetes.

