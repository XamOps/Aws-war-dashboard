# core/enhanced_discovery.py
import boto3
import datetime

def get_ec2_rightsizing_recommendations():
    co = boto3.client('compute-optimizer')
    try:
        response = co.get_ec2_instance_recommendations()
        recommendations = []
        for rec in response.get('instanceRecommendations', []):
            if rec.get('finding') == 'OVER_PROVISIONED':
                recommendations.append({
                    "instanceArn": rec['instanceArn'],
                    "current_instance_type": rec['currentInstanceType'],
                    "recommended_instance_type": rec['recommendationOptions'][0]['instanceType'],
                })
        return recommendations
    except Exception as e:
        return {"error": f"Could not retrieve Compute Optimizer data. Error: {e}"}

def get_unattached_volumes():
    ec2 = boto3.client('ec2')
    try:
        response = ec2.describe_volumes(Filters=[{'Name': 'status', 'Values': ['available']}])
        unattached = []
        for volume in response.get('Volumes', []):
            unattached.append({
                "VolumeId": volume['VolumeId'], "SizeGiB": volume['Size'],
                "CreateTime": volume['CreateTime'].isoformat()
            })
        return unattached
    except Exception as e:
        return {"error": f"Could not retrieve EBS Volume data. Error: {e}"}

def get_rds_instance_status():
    rds = boto3.client('rds')
    try:
        response = rds.describe_db_instances()
        status = []
        for db in response.get('DBInstances', []):
            status.append({
                "DBInstanceIdentifier": db['DBInstanceIdentifier'], "Engine": db['Engine'],
                "IsMultiAZ": db['MultiAZ']
            })
        return status
    except Exception as e:
        return {"error": f"Could not retrieve RDS data. Error: {e}"}

def check_secrets_rotation():
    sm = boto3.client('secretsmanager')
    try:
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
