# cli/main.py (Updated)

import json
from core.discovery import list_ec2_instances, list_s3_buckets
from core.compliance import check_mfa
from core.war_mapper import generate_autofilled_answers
from core.architecture_export import export_architecture_json
from cost.cloudwatch_analyzer import get_data_transfer_cost
from cost.vpc_log_parser import analyze_vpc_transfer_cost

# --- Add this new import ---
from core.enhanced_discovery import (
    get_cost_by_service,
    get_ec2_rightsizing_recommendations,
    get_unattached_volumes,
    get_rds_instance_status,
    check_secrets_rotation
)

def run_all():
    print("--- Basic Discovery ---")
    print("EC2 Instances:", list_ec2_instances())
    print("S3 Buckets:", list_s3_buckets())
    print("Users Without MFA:", check_mfa())
    print("WAR Answers:", generate_autofilled_answers())
    export_architecture_json({"EC2": "details"})
    
    print("\n--- Initial Cost Analysis ---")
    print("CloudWatch Transfer Costs:", get_data_transfer_cost())
    # print("VPC Flow Log Transfer Costs:", analyze_vpc_transfer_cost("flowlog.gz")) # Commenting out as it requires a file

    # --- Add calls to new functions ---
    print("\n--- Enhanced AWS WAR Data Discovery ---")
    
    print("\n[Cost] Monthly Cost by Service:")
    print(json.dumps(get_cost_by_service(), indent=2))
    
    print("\n[Cost] EC2 Rightsizing Recommendations:")
    print(json.dumps(get_ec2_rightsizing_recommendations(), indent=2))

    print("\n[Cost] Unattached EBS Volumes:")
    print(json.dumps(get_unattached_volumes(), indent=2))

    print("\n[Reliability] RDS Multi-AZ Status:")
    print(json.dumps(get_rds_instance_status(), indent=2))
    
    print("\n[Security] Secrets Manager Rotation Status:")
    print(json.dumps(check_secrets_rotation(), indent=2))


if __name__ == '__main__':
    run_all()