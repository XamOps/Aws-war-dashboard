# backend/app.py
import sys
import os
import json
import time 
import boto3 # Import boto3 here
from datetime import datetime
from flask import Flask
from flask_cors import CORS

# Add the current directory to the Python path to find modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import all necessary functions
from core.compliance import check_mfa
from core.discovery import list_ec2_instances, list_s3_buckets
from core.enhanced_discovery import get_rds_instance_status, check_secrets_rotation, get_ec2_rightsizing_recommendations, get_unattached_volumes
from core.additional_checks import check_public_s3_buckets, check_unrestricted_security_groups, check_cloudtrail_status, check_ebs_backup_status, check_ec2_detailed_monitoring, check_s3_lifecycle_policies
from core.advanced_checks import check_vpc_flow_logs, check_cloudformation_stack_drift, check_iam_access_key_age
from cost.cloudwatch_analyzer import get_api_throttle_events

def custom_serializer(obj):
    if isinstance(obj, (datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

app = Flask(__name__)

# --- FIX for CORS Error ---
# This explicitly allows requests from your React frontend's origin for all routes under /api/.
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})


@app.route("/")
def index():
    return "<h1>AWS Well-Architected Dashboard API</h1>"

@app.route("/api/scan/all", methods=['GET'])
def get_all_scans():
    scan_start_time = time.time()
    
    # Each function creates its own boto3 client and runs the scan
    all_findings = {
        "security": {
            "users_without_mfa": check_mfa(),
            "public_s3_buckets": check_public_s3_buckets(),
            "unrestricted_security_groups": check_unrestricted_security_groups(),
            "aged_iam_keys": check_iam_access_key_age(),
            "cloudtrail_status": check_cloudtrail_status(),
            "vpcs_without_flow_logs": check_vpc_flow_logs(),
        },
        "reliability": {
            "rds_multi_az_status": get_rds_instance_status(),
            "ebs_volumes_without_backup": check_ebs_backup_status(),
        },
        "cost_optimization": {
            "s3_buckets_without_lifecycle": check_s3_lifecycle_policies(),
            "compute_optimizer_status": get_ec2_rightsizing_recommendations(),
            "unattached_volumes": get_unattached_volumes(),
        },
        "performance_efficiency": {
            "ec2_without_detailed_monitoring": check_ec2_detailed_monitoring(),
        },
        "operational_excellence": {
            "cloudformation_drift_status": check_cloudformation_stack_drift(),
        }
    }
    
    # --- FIX for TypeError ---
    # Create a boto3 client and pass it to the function
    cloudwatch_client = boto3.client('cloudwatch')
    throttled_requests = get_api_throttle_events(cloudwatch_client)
    
    scan_end_time = time.time()
    
    all_findings["scan_metadata"] = {
        "status": "Throttled" if throttled_requests > 0 else "Healthy",
        "throttled_requests": throttled_requests,
        "successful_requests": 14, 
        "last_scan_duration_sec": round(scan_end_time - scan_start_time)
    }
    
    return json.dumps(all_findings, default=custom_serializer), 200, {'Content-Type': 'application/json'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
