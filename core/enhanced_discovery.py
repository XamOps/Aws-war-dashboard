import boto3
import datetime
import json

def get_cost_by_service():
    """
    Retrieves the unblended cost for the last 30 days, grouped by AWS service.
    This replaces the mock financial data in the cost breakdown chart.
    
    Required IAM Permissions: ce:GetCostAndUsage
    """
    try:
        ce = boto3.client('ce')
        end = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        start = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')

        response = ce.get_cost_and_usage(
            TimePeriod={'Start': start, 'End': end},
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
        )
        
        costs = {}
        for item in response['ResultsByTime'][0]['Groups']:
            service_name = item['Keys'][0]
            amount = float(item['Metrics']['UnblendedCost']['Amount'])
            if amount > 0.1: # Only include costs over 10 cents
                costs[service_name] = round(amount, 2)
        return costs
    except Exception as e:
        return {"error": f"Could not retrieve Cost Explorer data. Make sure you have permissions. Error: {e}"}

def get_ec2_rightsizing_recommendations():
    """
    Fetches EC2 instance rightsizing recommendations from AWS Compute Optimizer.
    This provides specific, actionable savings opportunities.

    Required IAM Permissions: compute-optimizer:GetEC2InstanceRecommendations
    """
    try:
        co = boto3.client('compute-optimizer')
        response = co.get_ec2_instance_recommendations()
        
        recommendations = []
        for rec in response.get('instanceRecommendations', []):
            if rec.get('finding') == 'OVER_PROVISIONED':
                recommendations.append({
                    "instanceArn": rec['instanceArn'],
                    "current_instance_type": rec['currentInstanceType'],
                    "finding": rec['finding'],
                    "recommended_instance_type": rec['recommendationOptions'][0]['instanceType'],
                    "estimated_monthly_savings": float(rec['recommendationOptions'][0]['estimatedMonthlySavings']['value'])
                })
        return recommendations
    except Exception as e:
        return {"error": f"Could not retrieve Compute Optimizer data. Ensure the service is enabled. Error: {e}"}

def get_unattached_volumes():
    """
    Finds all EBS volumes in the 'available' state (unattached).
    These are often a source of unnecessary cost.

    Required IAM Permissions: ec2:DescribeVolumes
    """
    try:
        ec2 = boto3.client('ec2')
        response = ec2.describe_volumes(Filters=[{'Name': 'status', 'Values': ['available']}])
        
        unattached = []
        for volume in response.get('Volumes', []):
            unattached.append({
                "VolumeId": volume['VolumeId'],
                "SizeGiB": volume['Size'],
                "CreateTime": volume['CreateTime'].isoformat()
            })
        return unattached
    except Exception as e:
        return {"error": f"Could not retrieve EBS Volume data. Error: {e}"}

def get_rds_instance_status():
    """
    Checks all RDS database instances and reports on their Multi-AZ status.
    This is a critical check for the Reliability pillar.

    Required IAM Permissions: rds:DescribeDBInstances
    """
    try:
        rds = boto3.client('rds')
        response = rds.describe_db_instances()
        
        status = []
        for db in response.get('DBInstances', []):
            status.append({
                "DBInstanceIdentifier": db['DBInstanceIdentifier'],
                "Engine": db['Engine'],
                "IsMultiAZ": db['MultiAZ']
            })
        return status
    except Exception as e:
        return {"error": f"Could not retrieve RDS data. Error: {e}"}

def check_secrets_rotation():
    """
    Lists secrets in AWS Secrets Manager and checks if automatic rotation is enabled.
    This validates a key security best practice.

    Required IAM Permissions: secretsmanager:ListSecrets
    """
    try:
        sm = boto3.client('secretsmanager')
        response = sm.list_secrets()

        secrets_status = []
        for secret in response.get('SecretList', []):
            secrets_status.append({
                "Name": secret['Name'],
                "RotationEnabled": secret.get('RotationEnabled', False)
            })
        return secrets_status
    except Exception as e:
        return {"error": f"Could not retrieve Secrets Manager data. Error: {e}"}

if __name__ == '__main__':
    print("--- Enhanced AWS WAR Data Discovery ---")
    
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