package controller

import (
    "context"
    "fmt"

    "k8s.io/apimachinery/pkg/api/errors"
    "k8s.io/apimachinery/pkg/runtime"
    ctrl "sigs.k8s.io/controller-runtime"
    "sigs.k8s.io/controller-runtime/pkg/client"
    "sigs.k8s.io/controller-runtime/pkg/log"

    corev1 "k8s.io/api/core/v1"
    appsv1 "k8s.io/api/apps/v1"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/apimachinery/pkg/util/intstr"

    mysqlv1alpha1 "mysqloperator/api/v1alpha1"
)

type MySQLReconciler struct {
    client.Client
    Scheme *runtime.Scheme
}

func (r *MySQLReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    log := log.FromContext(ctx)

    // Fetch the MySQL instance
    mysql := &mysqlv1alpha1.MySQL{}
    if err := r.Get(ctx, req.NamespacedName, mysql); err != nil {
        if errors.IsNotFound(err) {
            log.Info("MySQL resource not found. Ignoring since object must be deleted")
            return ctrl.Result{}, nil
        }
        log.Error(err, "Failed to get MySQL")
        return ctrl.Result{}, err
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

    // Update status
    mysql.Status.Phase = "Ready"
    mysql.Status.Message = "MySQL instance is running"
    if err := r.Status().Update(ctx, mysql); err != nil {
        log.Error(err, "Failed to update MySQL status")
        return ctrl.Result{}, err
    }

    return ctrl.Result{}, nil
}

func (r *MySQLReconciler) reconcileDeployment(ctx context.Context, mysql *mysqlv1alpha1.MySQL) error {
    log := log.FromContext(ctx)
    
    deployment := &appsv1.Deployment{
        ObjectMeta: metav1.ObjectMeta{
            Name:      fmt.Sprintf("mysql-%s", mysql.Name),
            Namespace: mysql.Namespace,
        },
    }

    _, err := ctrl.CreateOrUpdate(ctx, r.Client, deployment, func() error {
        if deployment.Labels == nil {
            deployment.Labels = make(map[string]string)
        }
        deployment.Labels["app"] = "mysql"
        deployment.Labels["mysql-instance"] = mysql.Name
        
        replicas := int32(1)
        deployment.Spec = appsv1.DeploymentSpec{
            Replicas: &replicas,
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
                                    Name: "MYSQL_ROOT_PASSWORD",
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
    
    log.Info("Deployment successfully reconciled")
    return nil
}

func (r *MySQLReconciler) reconcileService(ctx context.Context, mysql *mysqlv1alpha1.MySQL) error {
    log := log.FromContext(ctx)
    
    service := &corev1.Service{
        ObjectMeta: metav1.ObjectMeta{
            Name:      fmt.Sprintf("mysql-%s", mysql.Name),
            Namespace: mysql.Namespace,
        },
    }

    _, err := ctrl.CreateOrUpdate(ctx, r.Client, service, func() error {
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
        log.Error(err, "Failed to create/update Service")
        return err
    }
    
    log.Info("Service successfully reconciled")
    return nil
}

func (r *MySQLReconciler) reconcileSecret(ctx context.Context, mysql *mysqlv1alpha1.MySQL) error {
    log := log.FromContext(ctx)
    
    secret := &corev1.Secret{
        ObjectMeta: metav1.ObjectMeta{
            Name:      fmt.Sprintf("mysql-secret-%s", mysql.Name),
            Namespace: mysql.Namespace,
        },
    }

    _, err := ctrl.CreateOrUpdate(ctx, r.Client, secret, func() error {
        if secret.Data == nil {
            secret.Data = make(map[string][]byte)
        }
        if _, exists := secret.Data["password"]; !exists {
            secret.Data["password"] = []byte("mysql-operator-password-123")
        }
        return ctrl.SetControllerReference(mysql, secret, r.Scheme)
    })

    if err != nil {
        log.Error(err, "Failed to create/update Secret")
        return err
    }
    
    log.Info("Secret successfully reconciled")
    return nil
}

func (r *MySQLReconciler) SetupWithManager(mgr ctrl.Manager) error {
    return ctrl.NewControllerManagedBy(mgr).
        For(&mysqlv1alpha1.MySQL{}).
        Owns(&appsv1.Deployment{}).
        Owns(&corev1.Service{}).
        Owns(&corev1.Secret{}).
        Complete(r)
}