from flask import Flask, jsonify, request
from flask_cors import CORS
import boto3
import time
import traceback

# Import your check modules
from core import discovery, compliance, war_mapper, advanced_checks

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# In-memory cache to store scan results
scan_cache = {}
CACHE_TTL = 3600  # 1 hour

def get_aws_session():
    """Creates and returns a Boto3 session."""
    return boto3.Session()

def run_pillar_checks(check_function, *args):
    """Safely runs a check function and handles exceptions."""
    try:
        return check_function(*args)
    except Exception as e:
        print(f"Error running check {check_function.__name__}: {e}")
        print(traceback.format_exc())
        return {"error": f"Failed to run check: {check_function.__name__}", "details": str(e)}

@app.route('/api/scan/all', methods=['GET'])
def get_all_findings():
    """
    Main endpoint to trigger a comprehensive scan of the AWS account.
    It combines findings from all pillars with enhanced error handling.
    """
    cache_key = 'all_findings'
    current_time = time.time()

    if cache_key in scan_cache and (current_time - scan_cache[cache_key]['timestamp']) < CACHE_TTL:
        print("Returning cached data for /api/scan/all")
        return jsonify(scan_cache[cache_key]['data'])

    print("No valid cache found, performing a new scan...")
    start_time = time.time()
    
    try:
        session = get_aws_session()
        
        # --- Basic Discovery (Run these first as they are dependencies) ---
        iam_users = discovery.list_iam_users()
        s3_buckets = discovery.list_s3_buckets()
        ec2_instances = discovery.list_ec2_instances()
        rds_instances = discovery.list_rds_instances()
        vpcs = discovery.list_vpcs()
        cloudtrails = discovery.list_cloudtrails()
        security_groups = discovery.list_security_groups()
        ebs_volumes = discovery.list_ebs_volumes()
        cfn_stacks = discovery.list_cloudformation_stacks()

        # --- Compliance and Pillar-Specific Checks (with individual error handling) ---
        security_findings = {
            "users_without_mfa": run_pillar_checks(compliance.check_mfa, iam_users),
            "public_s3_buckets": run_pillar_checks(compliance.check_public_s3_buckets, s3_buckets, session),
            "aged_iam_keys": run_pillar_checks(compliance.check_iam_key_age, iam_users, session),
            "unrestricted_security_groups": run_pillar_checks(compliance.check_unrestricted_security_groups, security_groups),
            "vpcs_without_flow_logs": run_pillar_checks(compliance.check_vpc_flow_logs, vpcs, session),
            "cloudtrail_status": run_pillar_checks(compliance.check_cloudtrail_status, cloudtrails)
        }

        cost_optimization_findings = {
            "s3_buckets_without_lifecycle": run_pillar_checks(compliance.check_s3_lifecycle, s3_buckets, session),
            "compute_optimizer_status": run_pillar_checks(compliance.check_compute_optimizer, session),
            **run_pillar_checks(advanced_checks.run_all_advanced_checks, session).get('cost_optimization', {})
        }
        
        reliability_findings = {
            "rds_multi_az_status": run_pillar_checks(compliance.check_rds_multi_az, rds_instances),
            "ebs_volumes_without_backup": run_pillar_checks(compliance.check_ebs_backups, ebs_volumes, session)
        }
        
        performance_efficiency_findings = {
             "ec2_without_detailed_monitoring": run_pillar_checks(compliance.check_ec2_detailed_monitoring, ec2_instances)
        }

        operational_excellence_findings = {
            "cloudformation_drift_status": run_pillar_checks(compliance.check_cloudformation_drift, cfn_stacks, session)
        }
        
        end_time = time.time()
        scan_duration = round(end_time - start_time, 2)
        print(f"Scan completed in {scan_duration} seconds.")

        # --- Assemble Final Response ---
        response_data = {
            "scan_metadata": {
                "status": "Healthy",
                "last_scan_duration_sec": scan_duration,
                "throttled_requests": 0
            },
            "security": security_findings,
            "cost_optimization": cost_optimization_findings,
            "reliability": reliability_findings,
            "performance_efficiency": performance_efficiency_findings,
            "operational_excellence": operational_excellence_findings
        }
        
        # Cache the new results
        scan_cache[cache_key] = {
            'timestamp': current_time,
            'data': response_data
        }

        return jsonify(response_data)

    except Exception as e:
        print(f"A critical error occurred during the discovery phase: {e}")
        print(traceback.format_exc())
        return jsonify({"error": "Failed to complete the scan due to a critical error.", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)

