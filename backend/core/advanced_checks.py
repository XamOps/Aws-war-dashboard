# core/advanced_checks.py
import boto3
from datetime import datetime, timezone, timedelta

def check_vpc_flow_logs():
    ec2 = boto3.client('ec2')
    vpcs_without_flow_logs = []
    try:
        vpcs = ec2.describe_vpcs().get('Vpcs', [])
        flow_logs = ec2.describe_flow_logs().get('FlowLogs', [])
        vpcs_with_logs = {log['ResourceId'] for log in flow_logs}
        
        for vpc in vpcs:
            if vpc['VpcId'] not in vpcs_with_logs:
                vpcs_without_flow_logs.append(vpc['VpcId'])
                
    except Exception as e:
        return {"error": f"Could not check VPC Flow Logs. Error: {e}"}
    return vpcs_without_flow_logs

def check_cloudformation_stack_drift():
    cfn = boto3.client('cloudformation')
    drifted_stacks = []
    try:
        stacks = cfn.list_stacks(StackStatusFilter=[
            'CREATE_COMPLETE', 'UPDATE_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE'
        ]).get('StackSummaries', [])
        
        for stack in stacks:
            stack_name = stack['StackName']
            try:
                drift_detection_id = cfn.detect_stack_drift(StackName=stack_name)['StackDriftDetectionId']
                waiter = cfn.get_waiter('stack_drift_detection_complete')
                waiter.wait(StackDriftDetectionId=drift_detection_id)
                result = cfn.describe_stack_drift_detection_status(StackDriftDetectionId=drift_detection_id)
                if result['StackDriftStatus'] == 'DRIFTED':
                    drifted_stacks.append({
                        "StackName": stack_name, "DriftStatus": result['StackDriftStatus'],
                        "DetectionStatusReason": result.get('DetectionStatusReason', '')
                    })
            except Exception:
                continue
    except Exception as e:
        return {"error": f"Could not check CloudFormation drift. Error: {e}"}
    return drifted_stacks

def check_iam_access_key_age():
    iam = boto3.client('iam')
    old_keys = []
    ninety_days_ago = datetime.now(timezone.utc) - timedelta(days=90)
    try:
        users = iam.list_users().get('Users', [])
        for user in users:
            username = user['UserName']
            keys = iam.list_access_keys(UserName=username).get('AccessKeyMetadata', [])
            for key in keys:
                if key['Status'] == 'Active' and key['CreateDate'] < ninety_days_ago:
                    old_keys.append({
                        "UserName": username, "AccessKeyId": key['AccessKeyId'],
                        "CreateDate": key['CreateDate'].isoformat()
                    })
    except Exception as e:
        return {"error": f"Could not check IAM key age. Error: {e}"}
    return old_keys
