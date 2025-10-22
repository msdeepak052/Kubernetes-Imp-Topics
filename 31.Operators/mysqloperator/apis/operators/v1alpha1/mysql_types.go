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

// +kubebuilder:object:root=true
// +kubebuilder:subresource:status

// MySQL is the Schema for the mysqls API
type MySQL struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`

    Spec   MySQLSpec   `json:"spec,omitempty"`
    Status MySQLStatus `json:"status,omitempty"`
}

// +kubebuilder:object:root=true

// MySQLList contains a list of MySQL
type MySQLList struct {
    metav1.TypeMeta `json:",inline"`
    metav1.ListMeta `json:"metadata,omitempty"`
    Items           []MySQL `json:"items"`
}