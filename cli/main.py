from core.discovery import list_ec2_instances, list_s3_buckets
from core.compliance import check_mfa
from core.war_mapper import generate_autofilled_answers
from core.architecture_export import export_architecture_json
from cost.cloudwatch_analyzer import get_data_transfer_cost
from cost.vpc_log_parser import analyze_vpc_transfer_cost

def run_all():
    print("EC2 Instances:", list_ec2_instances())
    print("S3 Buckets:", list_s3_buckets())
    print("Users Without MFA:", check_mfa())
    print("WAR Answers:", generate_autofilled_answers())
    export_architecture_json({"EC2": "details"})
    print("CloudWatch Transfer Costs:", get_data_transfer_cost())
    print("VPC Flow Log Transfer Costs:", analyze_vpc_transfer_cost("flowlog.gz"))

if __name__ == '__main__':
    run_all()
