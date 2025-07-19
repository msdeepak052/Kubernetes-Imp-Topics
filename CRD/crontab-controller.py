from kubernetes import client, config, watch
import time
import os

def create_cronjob(cron_name, cron_expr, msg):
    batch_v1 = client.BatchV1beta1Api()
    body = client.V1beta1CronJob(
        metadata=client.V1ObjectMeta(name=f"{cron_name}-job"),
        spec=client.V1beta1CronJobSpec(
            schedule=cron_expr,
            job_template=client.V1JobTemplateSpec(
                spec=client.V1JobSpec(
                    template=client.V1PodTemplateSpec(
                        spec=client.V1PodSpec(
                            restart_policy="OnFailure",
                            containers=[
                                client.V1Container(
                                    name="echo",
                                    image="busybox",
                                    args=["/bin/sh", "-c", f"echo {msg}"]
                                )
                            ]
                        )
                    )
                )
            )
        )
    )

    try:
        batch_v1.create_namespaced_cron_job(namespace="default", body=body)
        print(f"✅ Created CronJob: {cron_name}-job")
    except Exception as e:
        print(f"⚠️ Failed to create job: {e}")

def main():
    config.load_incluster_config() if os.getenv("KUBERNETES_SERVICE_HOST") else config.load_kube_config()
    api = client.CustomObjectsApi()

    w = watch.Watch()
    print("🚀 Watching CronTab custom resources...")
    for event in w.stream(api.list_namespaced_custom_object,
                          group="stable.deepak.com",
                          version="v1",
                          namespace="default",
                          plural="crontabs"):
        cr = event['object']
        etype = event['type']
        name = cr['metadata']['name']
        cronSpec = cr['spec']['cronSpec']
        message = cr['spec']['message']

        if etype == 'ADDED':
            print(f"📥 Detected new CronTab: {name}")
            create_cronjob(name, cronSpec, message)

if __name__ == "__main__":
    main()
