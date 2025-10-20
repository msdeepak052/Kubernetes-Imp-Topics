from flask import Flask, request, jsonify
import logging
import os
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration - In production, this would come from ConfigMap
APPROVED_REGISTRIES = [
    "docker.io",
    "gcr.io",
    "k8s.gcr.io",
    "quay.io",
    "registry.k8s.io",
    "ghcr.io"
]

BLOCKED_TAGS = ["latest"]

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "status": "healthy", 
        "message": "Image Validator Webhook is running",
        "version": "1.0.0"
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

@app.route('/validate', methods=['POST'])
def validate():
    try:
        req = request.get_json()
        logger.info("Received pod validation request")
        
        if not req or "request" not in req:
            return jsonify({
                "apiVersion": "admission.k8s.io/v1",
                "kind": "AdmissionReview",
                "response": {
                    "uid": "",
                    "allowed": False,
                    "status": {"message": "Invalid request"}
                }
            })
        
        uid = req["request"]["uid"]
        
        # Get pod metadata
        pod_metadata = req["request"]["object"].get("metadata", {})
        pod_namespace = pod_metadata.get("namespace", "")
        pod_name = pod_metadata.get("name", "")
        
        logger.info(f"Validating pod: {pod_name} in namespace: {pod_namespace}")
        
        # Skip validation for webhook's own namespace
        if pod_namespace == "image-validator-demo":
            logger.info("Skipping validation for image-validator-demo namespace")
            return jsonify({
                "apiVersion": "admission.k8s.io/v1",
                "kind": "AdmissionReview",
                "response": {
                    "uid": uid,
                    "allowed": True,
                    "status": {"message": "Skipped validation in image-validator-demo namespace"}
                }
            })
        
        pod_spec = req["request"]["object"]["spec"]
        containers = pod_spec.get("containers", [])
        init_containers = pod_spec.get("initContainers", [])
        
        all_containers = containers + init_containers
        
        # Validate each container
        validation_errors = []
        
        for container in all_containers:
            container_name = container.get("name", "unknown")
            image = container.get("image", "")
            
            # Check 1: Image registry validation
            registry_approved, registry_msg = validate_image_registry(image, container_name)
            if not registry_approved:
                validation_errors.append(registry_msg)
            
            # Check 2: Block latest tags
            tag_blocked, tag_msg = validate_image_tag(image, container_name)
            if tag_blocked:
                validation_errors.append(tag_msg)
            
            # Check 3: Resource limits
            resources_valid, resources_msg = validate_resources(container, container_name)
            if not resources_valid:
                validation_errors.append(resources_msg)
            
            # Check 4: Security context
            security_valid, security_msg = validate_security_context(container, container_name)
            if not security_valid:
                validation_errors.append(security_msg)
        
        if validation_errors:
            allowed = False
            msg = " | ".join(validation_errors)
            logger.warning(f"Pod validation failed: {msg}")
        else:
            allowed = True
            msg = "All validations passed"
            logger.info(f"Pod validation passed: {pod_name}")
        
        response = {
            "apiVersion": "admission.k8s.io/v1",
            "kind": "AdmissionReview",
            "response": {
                "uid": uid, 
                "allowed": allowed, 
                "status": {"message": msg}
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error in validation: {str(e)}")
        return jsonify({
            "apiVersion": "admission.k8s.io/v1",
            "kind": "AdmissionReview",
            "response": {
                "uid": req.get("request", {}).get("uid", ""),
                "allowed": False,
                "status": {"message": f"Validation error: {str(e)}"}
            }
        })

def validate_image_registry(image, container_name):
    """Validate that image comes from approved registry"""
    if not image:
        return False, f"Container '{container_name}': Image is required"
    
    # Extract registry
    parts = image.split('/')
    if len(parts) > 1:
        registry = parts[0]
        if '.' in registry or ':' in registry:  # It's a registry with domain/port
            if registry not in APPROVED_REGISTRIES:
                return False, f"Container '{container_name}': Registry '{registry}' not in approved list: {APPROVED_REGISTRIES}"
    
    return True, ""

def validate_image_tag(image, container_name):
    """Validate that image doesn't use blocked tags"""
    if not image:
        return False, f"Container '{container_name}': Image is required"
    
    # Extract tag
    tag = "latest"  # default
    if ':' in image:
        tag = image.split(':')[-1]
    
    if tag in BLOCKED_TAGS:
        return True, f"Container '{container_name}': Tag '{tag}' is blocked. Use specific version tags."
    
    return False, ""

def validate_resources(container, container_name):
    """Validate that container has resource limits and requests"""
    resources = container.get("resources", {})
    
    errors = []
    
    # Check limits
    limits = resources.get("limits", {})
    if not limits.get("cpu"):
        errors.append("CPU limits")
    if not limits.get("memory"):
        errors.append("memory limits")
    
    # Check requests
    requests = resources.get("requests", {})
    if not requests.get("cpu"):
        errors.append("CPU requests")
    if not requests.get("memory"):
        errors.append("memory requests")
    
    if errors:
        return False, f"Container '{container_name}': Missing {', '.join(errors)}"
    
    return True, ""

def validate_security_context(container, container_name):
    """Validate security context settings"""
    security_context = container.get("securityContext", {})
    
    errors = []
    
    # Check for runAsNonRoot
    if not security_context.get("runAsNonRoot", False):
        errors.append("runAsNonRoot=true")
    
    # Check for allowPrivilegeEscalation
    if security_context.get("allowPrivilegeEscalation", True):
        errors.append("allowPrivilegeEscalation=false")
    
    # Check for readOnlyRootFilesystem
    if not security_context.get("readOnlyRootFilesystem", False):
        errors.append("readOnlyRootFilesystem=true")
    
    if errors:
        return False, f"Container '{container_name}': Required {', '.join(errors)}"
    
    return True, ""

if __name__ == '__main__':
    logger.info("Starting Image Validator Webhook on port 8443")
    logger.info(f"Approved registries: {APPROVED_REGISTRIES}")
    logger.info(f"Blocked tags: {BLOCKED_TAGS}")
    app.run(host='0.0.0.0', port=8443, ssl_context=('/certs/tls.crt', '/certs/tls.key'))