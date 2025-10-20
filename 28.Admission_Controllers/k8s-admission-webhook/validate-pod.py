from flask import Flask, request, jsonify
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def root():
    return jsonify({"status": "healthy", "message": "Pod Validator Webhook is running"})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

@app.route('/validate', methods=['POST'])
def validate():
    try:
        req = request.get_json()
        logger.info(f"Received validation request")
        
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
        if pod_namespace == "webhook-demo":
            logger.info("Skipping validation for webhook-demo namespace")
            return jsonify({
                "apiVersion": "admission.k8s.io/v1",
                "kind": "AdmissionReview",
                "response": {
                    "uid": uid,
                    "allowed": True,
                    "status": {"message": "Skipped validation in webhook-demo namespace"}
                }
            })
        
        allowed = True
        msg = "Pod is valid"

        pod_spec = req["request"]["object"]["spec"]
        containers = pod_spec.get("containers", [])

        for c in containers:
            sc = c.get("securityContext", {})
            if not sc.get("runAsNonRoot", False):
                allowed = False
                msg = f"Container '{c['name']}' must set runAsNonRoot=true"
                break

        logger.info(f"Validation result: allowed={allowed}, message={msg}")
        
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

if __name__ == '__main__':
    logger.info("Starting webhook server on port 8443")
    app.run(host='0.0.0.0', port=8443, ssl_context=('/certs/tls.crt', '/certs/tls.key'))