# Demo-11 — Helm Builtin Objects (Full Practical Demo)

**Goal:**
Learn and experiment with Helm’s built-in objects (`.Release`, `.Chart`, `.Values`, `.Capabilities`, `.Files`, `.Template`, etc.) by building a sample chart that demonstrates each object and shows practical uses (conditionals, hooks, file embedding, capability checks, lifecycle awareness).

---

## 1) Quick overview of built-in objects used in this demo

* `.Release` — info about the release: `.Release.Name`, `.Release.Namespace`, `.Release.IsInstall`, `.Release.IsUpgrade`, `.Release.Revision`.
* `.Chart` — chart metadata: `.Chart.Name`, `.Chart.Version`, `.Chart.AppVersion`.
* `.Values` — user-configurable values from `values.yaml` and `-f`/`--set`.
* `.Capabilities` — cluster capabilities and Kube version: `.Capabilities.KubeVersion`, `.Capabilities.APIVersions.Has`.
* `.Files` — access chart local files under `files/` (e.g., `Files.Get`).
* `.Template` — template helpers like `include`, `tpl`.
* Flow-control: `if`, `with`, `range`.
* Hook example uses `helm` lifecycle hooks (pre-install / post-install) and shows `helm get hooks`.

---

## 2) Create demo project layout

Create directory `demo-11-builtins` and files exactly as below.

```
demo-11-builtins/
├── README.md
├── commands.sh
├── mychart/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── files/
│   │   └── welcome-message.txt
│   ├── templates/
│   │   ├── _helpers.tpl
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap-from-file.yaml
│   │   ├── capability-check.yaml
│   │   ├── hook-job.yaml
│   │   └── NOTES.txt
│   └── .helmignore
```

---

## 3) File contents (copy exactly)

### `demo-11-builtins/mychart/Chart.yaml`

```yaml
apiVersion: v2
name: mychart-builtins
description: Demo chart to illustrate Helm built-in objects
type: application
version: 0.1.0
appVersion: "1.0.0"
```

### `demo-11-builtins/mychart/values.yaml`

```yaml
replicaCount: 1

image:
  repository: nginx
  tag: "latest"
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80

enableHPA: false

# A value used to demonstrate tpl() usage
welcomeTemplate: |
  Welcome to {{ .Release.Name }} running in namespace {{ .Release.Namespace }}!
```

### `demo-11-builtins/mychart/files/welcome-message.txt`

```
Hello, this message was loaded from the chart files/ directory.
You can use .Files.Get to embed this into a ConfigMap.
```

### `demo-11-builtins/mychart/templates/_helpers.tpl`

```gotemplate
{{/* helpers for naming and labels */}}
{{- define "builtins.name" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name -}}
{{- end -}}

{{- define "builtins.labels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
{{- end -}}
```

### `demo-11-builtins/mychart/templates/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "builtins.name" . }}
  labels:
{{ include "builtins.labels" . | indent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app.kubernetes.io/instance: {{ .Release.Name }}
  template:
    metadata:
      labels:
        app.kubernetes.io/instance: {{ .Release.Name }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          env:
            - name: RELEASE_NAME
              value: "{{ .Release.Name }}"
            - name: RELEASE_NAMESPACE
              value: "{{ .Release.Namespace }}"
            - name: CHART_VERSION
              value: "{{ .Chart.Version }}"
            - name: WELCOME_MSG
              value: {{ tpl .Values.welcomeTemplate . | quote }}
```

**Explanation:** demonstrates `.Release`, `.Chart`, `.Values`, and `tpl()` which evaluates a string template with the chart context.

---

### `demo-11-builtins/mychart/templates/service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "builtins.name" . }}-svc
  labels:
{{ include "builtins.labels" . | indent 4 }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: 80
  selector:
    app.kubernetes.io/instance: {{ .Release.Name }}
```

**Explanation:** standard service using `.Values`.

---

### `demo-11-builtins/mychart/templates/configmap-from-file.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "builtins.name" . }}-files
data:
  welcome.txt: |-
{{ .Files.Get "files/welcome-message.txt" | indent 4 }}
  release-info: |-
    release.name: {{ .Release.Name }}
    release.namespace: {{ .Release.Namespace }}
    chart.name: {{ .Chart.Name }}
    chart.version: {{ .Chart.Version }}
```

**Explanation:** Uses `.Files.Get` to embed chart-local static file content into a ConfigMap.

---

### `demo-11-builtins/mychart/templates/capability-check.yaml`

```yaml
{{- /*
This manifest is rendered only if the cluster supports the apps/v1 API (practical example).
*/ -}}
{{- if .Capabilities.APIVersions.Has "apps/v1" }}
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "builtins.name" . }}-capabilities
data:
  kube_version: "{{ .Capabilities.KubeVersion.Version }}"
  has_apps_v1: "true"
{{- else }}
# cluster does not have apps/v1
{{- end }}
```

**Explanation:** `.Capabilities.APIVersions.Has` checks cluster API availability; `.Capabilities.KubeVersion` gives the server version.

---

### `demo-11-builtins/mychart/templates/hook-job.yaml`

```yaml
{{- /*
A simple Job that runs during post-install as a hook.
It demonstrates .Release.IsInstall and hook annotations.
*/ -}}
{{- if .Release.IsInstall }}
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "builtins.name" . }}-postinstall
  annotations:
    "helm.sh/hook": post-install
    "helm.sh/hook-weight": "5"
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: postinstall
          image: busybox
          command: ["sh","-c","echo Post-install hook for {{ .Release.Name }}; sleep 2"]
{{- end }}
```

**Explanation:** Hook runs only during install (`.Release.IsInstall`). After install you can inspect via `helm get hooks`.

---

### `demo-11-builtins/mychart/templates/NOTES.txt`

```
Thank you for installing {{ .Chart.Name }}!

Release: {{ .Release.Name }}
Namespace: {{ .Release.Namespace }}
Chart Version: {{ .Chart.Version }}

To view the welcome message stored in the ConfigMap:
  kubectl get cm {{ include "builtins.name" . }}-files -o yaml -n {{ .Release.Namespace }}

To see rendered manifest:
  helm get manifest {{ .Release.Name }} -n {{ .Release.Namespace }}

To see hooks:
  helm get hooks {{ .Release.Name }} -n {{ .Release.Namespace }}
```

**Explanation:** Uses `.Release` and `.Chart` for post-install notes.

---

### `demo-11-builtins/mychart/.helmignore`

```
# Patterns to ignore when packaging
.git/
*.tgz
.DS_Store
```

---

## 4) `README.md` for the demo (high-level instructions)

### `demo-11-builtins/README.md`

```markdown
# Demo-11: Helm Builtin Objects

This demo shows usage of Helm built-in objects:
- `.Release`, `.Chart`, `.Values`, `.Capabilities`, `.Files`, `tpl`, `include`, and hook examples.

Files of interest:
- templates/deployment.yaml -> uses .Release, .Chart, tpl(.Values.welcomeTemplate)
- templates/configmap-from-file.yaml -> uses .Files.Get
- templates/capability-check.yaml -> uses .Capabilities.APIVersions.Has and .Capabilities.KubeVersion
- templates/hook-job.yaml -> hook which runs on install (.Release.IsInstall)
- templates/NOTES.txt -> shows release info after install

Follow `commands.sh` to run the demo step-by-step.
```

---

## 5) `commands.sh` — run this to execute the demo

### `demo-11-builtins/commands.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

CHART_DIR="./mychart"
RELEASE="builtins-demo"
NAMESPACE="demo11-ns"

echo "1) Lint the chart"
helm lint "${CHART_DIR}"

echo "2) Render templates (dry-run) showing built-in objects rendered"
helm template "${RELEASE}" "${CHART_DIR}" --namespace "${NAMESPACE}" --debug > rendered-manifests.yaml
echo " -> rendered-manifests.yaml created (inspect it)"

echo "3) Create namespace"
kubectl create namespace "${NAMESPACE}" || true

echo "4) Install chart (this will execute post-install hook defined for install)"
helm install "${RELEASE}" "${CHART_DIR}" --namespace "${NAMESPACE}" --wait

echo "5) Show Helm release values (merged)"
helm get values "${RELEASE}" -n "${NAMESPACE}" --all

echo "6) Show full manifest that Helm applied"
helm get manifest "${RELEASE}" -n "${NAMESPACE}"

echo "7) Show hooks (should show the post-install job run)"
helm get hooks "${RELEASE}" -n "${NAMESPACE}"

echo "8) Inspect the ConfigMap with embedded file"
kubectl get configmap "${RELEASE}-mychart-builtins-files" -n "${NAMESPACE}" -o yaml || kubectl get configmap "${RELEASE}-files" -n "${NAMESPACE}" -o yaml

echo "9) Check capabilities ConfigMap (if created)"
kubectl get configmap "${RELEASE}-mychart-builtins-capabilities" -n "${NAMESPACE}" -o yaml || true

echo "10) Cleanup"
# Uncomment to uninstall automatically
# helm uninstall "${RELEASE}" -n "${NAMESPACE}"
# kubectl delete namespace "${NAMESPACE}"
echo "Demo complete. Manifests saved to rendered-manifests.yaml"
```

> Note: the `kubectl get configmap` name used in step 8 is robust — if you named the chart differently it will show available names; you can list `kubectl get cm -n demo11-ns`.

Make `commands.sh` executable:

```bash
chmod +x demo-11-builtins/commands.sh
```

---

## 6) Step-by-step run & what to observe

1. **Lint**
   `helm lint mychart` — ensures templates & chart structure are OK.

2. **Render templates (dry-run)**
   `helm template builtins-demo ./mychart --namespace demo11-ns --debug > rendered-manifests.yaml`
   Inspect `rendered-manifests.yaml` to see:

   * `.Release.Name` and `.Release.Namespace` values replaced.
   * `WELCOME_MSG` env contains the evaluated `tpl()` string (the `welcomeTemplate` string is evaluated with release context).
   * `ConfigMap` contains content from `files/welcome-message.txt` via `.Files.Get`.
   * `capability` configmap created only if `apps/v1` exists (almost always true for modern clusters).
   * Hook Job YAML present in rendered manifest but hooks run only during install.

3. **Create namespace**
   `kubectl create namespace demo11-ns` (or `helm install --create-namespace`).

4. **Install**
   `helm install builtins-demo ./mychart -n demo11-ns --wait`
   Observe:

   * Helm runs pre/post install lifecycle — the Job with `helm.sh/hook: post-install` will run after resources are created.
   * `helm get hooks builtins-demo -n demo11-ns` will show hook status and results.

5. **Inspect release info**

   * `helm get values builtins-demo -n demo11-ns --all` shows values.
   * `helm get manifest builtins-demo -n demo11-ns` shows final applied YAML.

6. **Check embedded file**
   `kubectl get cm <cm-name> -n demo11-ns -o yaml` — confirm `welcome.txt` equals the `files/welcome-message.txt` contents.

7. **Capability check**
   `kubectl get cm <capabilities-cm> -n demo11-ns -o yaml` — shows `.Capabilities.KubeVersion.Version`.

8. **Hooks**
   `helm get hooks builtins-demo -n demo11-ns` — view hook details and whether they succeeded.

9. **Cleanup**
   `helm uninstall builtins-demo -n demo11-ns` and `kubectl delete namespace demo11-ns`.

---

## 7) Explanations & practical tips (why each built-in matters)

* `.Release` — use it to label resources with the release name, craft readable resource names, and to detect install vs upgrade (`.Release.IsInstall` is handy in hooks).
* `.Chart` — used for naming/version info and for logic that depends on chart/app version.
* `.Values` — everything configurable belongs here; prefer values over templating logic for environment differences.
* `.Capabilities` — essential when you need chart templates compatible with multiple Kubernetes versions or to conditionally render resources only if the cluster supports an API. Example: older clusters may not have certain APIs. Use `Capabilities.APIVersions.Has "apiextensions.k8s.io/v1"` etc.
* `.Files` — embed small static assets (config files, SQL, scripts) into ConfigMaps or templates. Files must live under chart `files/` or `templates/`.
* `tpl` — evaluate a value as a template with current context. Very useful for values that should contain templated text (we used `welcomeTemplate`). Be careful — `tpl` runs templates inside values with same context, so it's powerful but increases complexity.
* `include` & helpers — keep templates DRY and consistent. Helpers `_helpers.tpl` house name/label logic.
* Hooks + `.Release.IsInstall` — useful for tasks you want to run only once on install (DB migration jobs, setup tasks) but be cautious: hooks add complexity; prefer Kubernetes-native patterns where possible.

---

## 8) Common gotchas

* **Names**: Helm release + chart name used together produce resource names to avoid collisions, but watch Kubernetes resource name length limits when using long release names. Use `trunc` helpers if needed.
* **.Files.Get**: only reads files packaged inside the chart (files/), not arbitrary file system paths.
* **tpl**: if user-supplied values include templates, `tpl` will evaluate them — validate and sanitize if required.
* **Hooks**: hooks are not managed like normal resources — their lifecycle is special (they run on condition and may leave jobs/pods around); check `helm.sh/hook-delete-policy` to auto-clean.
* **Capabilities**: always test `helm template` against your target clusters to ensure conditional rendering works as expected.

---

## 9) Ready-to-run summary commands

```bash
cd demo-11-builtins
chmod +x commands.sh
./commands.sh
# inspect rendered-manifests.yaml, kubectl get all -n demo11-ns, helm get hooks builtins-demo -n demo11-ns
# cleanup (if not done inside script):
helm uninstall builtins-demo -n demo11-ns
kubectl delete namespace demo11-ns
```

---

