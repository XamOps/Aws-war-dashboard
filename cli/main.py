# cli/main.py (Updated)

import json
from core.discovery import list_ec2_instances, list_s3_buckets
from core.compliance import check_mfa
from core.war_mapper import generate_autofilled_answers
from core.architecture_export import export_architecture_json
from cost.cloudwatch_analyzer import get_data_transfer_cost

# --- Import from enhanced_discovery.py ---
from core.enhanced_discovery import (
    get_cost_by_service,
    get_ec2_rightsizing_recommendations,
    get_unattached_volumes,
    get_rds_instance_status,
    check_secrets_rotation
)

# --- Add this new import for the additional checks ---
from core.additional_checks import (
    check_public_s3_buckets,
    check_unrestricted_security_groups,
    check_cloudtrail_status,
    check_ebs_backup_status,
    check_ec2_detailed_monitoring
)

def run_all():
    print("--- Basic Discovery ---")
    print("EC2 Instances:", list_ec2_instances())
    print("S3 Buckets:", list_s3_buckets())
    print("Users Without MFA:", check_mfa())
    print("WAR Answers:", generate_autofilled_answers())
    
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

    # --- Add calls to new additional checks ---
    print("\n--- Additional Well-Architected Checks ---")
    
    print("\n[Security] Public S3 Buckets:")
    print(json.dumps(check_public_s3_buckets(), indent=2))
    
    print("\n[Security] Unrestricted Security Groups (0.0.0.0/0):")
    print(json.dumps(check_unrestricted_security_groups(), indent=2))

    print("\n[Security] CloudTrail Status:")
    print(json.dumps(check_cloudtrail_status(), indent=2))

    print("\n[Reliability] EBS Volumes without Recent Backups:")
    print(json.dumps(check_ebs_backup_status(), indent=2))

    print("\n[Performance] EC2 without Detailed Monitoring:")
    print(json.dumps(check_ec2_detailed_monitoring(), indent=2))


if __name__ == '__main__':
    run_all()