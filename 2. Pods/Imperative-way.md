# Imperative Way of Launching Pods

The **imperative way** allows you to create and manage Kubernetes pods directly using `kubectl` commands, without writing YAML manifests.

## Create a Pod

```sh
kubectl run my-pod --image=nginx
```

- `my-pod`: Name of the pod.
- `--image=nginx`: Container image to use.

## List Pods

```sh
kubectl get pods
```

## Delete a Pod

```sh
kubectl delete pod my-pod
```

## Key Points

- Fast for testing and simple tasks.
- Not recommended for production (use declarative YAML for complex configs).
- Changes are not saved as files.

---
**Tip:** Use `kubectl run --dry-run=client -o yaml ...` to generate YAML from imperative commands.