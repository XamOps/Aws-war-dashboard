# core/additional_checks.py
import boto3
from datetime import datetime, timedelta, timezone

def check_public_s3_buckets():
    s3 = boto3.client('s3')
    public_buckets = []
    try:
        buckets = s3.list_buckets().get('Buckets', [])
        for bucket in buckets:
            bucket_name = bucket['Name']
            try:
                policy_status = s3.get_bucket_policy_status(Bucket=bucket_name)
                if policy_status['PolicyStatus']['IsPublic']:
                    public_buckets.append({"Bucket": bucket_name, "Reason": "Bucket Policy"})
                    continue 
            except s3.exceptions.ClientError as e:
                if e.response['Error']['Code'] != 'NoSuchBucketPolicy':
                    pass
            try:
                acl = s3.get_bucket_acl(Bucket=bucket_name)
                for grant in acl['Grants']:
                    if 'URI' in grant.get('Grantee', {}) and 'AllUsers' in grant['Grantee']['URI']:
                        public_buckets.append({"Bucket": bucket_name, "Reason": "ACL Grant"})
                        break
            except Exception:
                continue
    except Exception as e:
        return {"error": f"Could not check S3 buckets. Error: {e}"}
    return public_buckets

def check_unrestricted_security_groups():
    ec2 = boto3.client('ec2')
    risky_rules = []
    try:
        sgs = ec2.describe_security_groups().get('SecurityGroups', [])
        for sg in sgs:
            for rule in sg.get('IpPermissions', []):
                for ip_range in rule.get('IpRanges', []):
                    if ip_range.get('CidrIp') == '0.0.0.0/0':
                        risky_rules.append({
                            "GroupId": sg['GroupId'], "GroupName": sg['GroupName'],
                            "PortRange": rule.get('FromPort', 'All'), "Protocol": rule.get('IpProtocol', 'All')
                        })
    except Exception as e:
        return {"error": f"Could not check security groups. Error: {e}"}
    return risky_rules

def check_cloudtrail_status():
    ct = boto3.client('cloudtrail')
    trails_status = []
    try:
        trails = ct.describe_trails().get('trailList', [])
        for trail in trails:
            status = ct.get_trail_status(Name=trail['TrailARN'])
            trails_status.append({
                "Name": trail['Name'], "IsMultiRegion": trail['IsMultiRegionTrail'], "IsLogging": status['IsLogging']
            })
    except Exception as e:
        return {"error": f"Could not check CloudTrail status. Error: {e}"}
    return trails_status

def check_ebs_backup_status():
    ec2 = boto3.client('ec2')
    volumes_without_backup = []
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    try:
        volumes = ec2.describe_volumes(Filters=[{'Name': 'status', 'Values': ['in-use']}]).get('Volumes', [])
        for vol in volumes:
            snapshots = ec2.describe_snapshots(Filters=[{'Name': 'volume-id', 'Values': [vol['VolumeId']]}]).get('Snapshots', [])
            if not snapshots or max(snap['StartTime'] for snap in snapshots) < seven_days_ago:
                volumes_without_backup.append({
                    "VolumeId": vol['VolumeId'], "SizeGiB": vol['Size'],
                    "LastSnapshot": max(snap['StartTime'] for snap in snapshots).isoformat() if snapshots else "None"
                })
    except Exception as e:
        return {"error": f"Could not check EBS backups. Error: {e}"}
    return volumes_without_backup

def check_ec2_detailed_monitoring():
    ec2 = boto3.client('ec2')
    instances_without_detailed_monitoring = []
    try:
        reservations = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]).get('Reservations', [])
        for res in reservations:
            for instance in res.get('Instances', []):
                if instance.get('Monitoring', {}).get('State') != 'enabled':
                    instances_without_detailed_monitoring.append({
                        "InstanceId": instance['InstanceId'],
                        "Name": next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'N/A')
                    })
    except Exception as e:
        return {"error": f"Could not check EC2 monitoring. Error: {e}"}
    return instances_without_detailed_monitoring

def check_s3_lifecycle_policies():
    s3 = boto3.client('s3')
    buckets_without_lifecycle = []
    try:
        buckets = s3.list_buckets().get('Buckets', [])
        for bucket in buckets:
            bucket_name = bucket['Name']
            try:
                s3.get_bucket_lifecycle_configuration(Bucket=bucket_name)
            except s3.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchLifecycleConfiguration':
                    buckets_without_lifecycle.append(bucket_name)
    except Exception as e:
        return {"error": f"Could not list S3 buckets. Error: {e}"}
    return buckets_without_lifecycle
