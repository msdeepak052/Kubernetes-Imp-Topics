{{- define "bookstore.name" -}}
{{ .Chart.Name }}
{{- end }}

{{- define "bookstore.fullname" -}}
{{ printf "%s-%s" .Release.Name .Chart.Name }}
{{- end }}
