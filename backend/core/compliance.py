import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta, timezone
import time

def check_mfa(users):
    """
    Checks for IAM users without MFA enabled from a given list of users.

    Args:
        users: A list of user dictionaries from the boto3.client('iam').list_users() call.

    Returns:
        A list of usernames that do not have MFA enabled.
    """
    iam = boto3.client('iam')
    non_compliant = []
    for user in users:
        try:
            mfa_devices = iam.list_mfa_devices(UserName=user['UserName'])
            if not mfa_devices['MFADevices']:
                non_compliant.append(user['UserName'])
        except ClientError as e:
            print(f"Could not check MFA for user {user['UserName']}: {e}")
    return non_compliant

def check_public_s3_buckets(buckets, session):
    """
    Checks for S3 buckets that are publicly accessible.
    
    Args:
        buckets: A list of bucket dictionaries from list_buckets().
        session: A boto3 session object.
    
    Returns:
        A list of dictionaries for each public bucket with its name and reason.
    """
    s3 = session.client('s3')
    public_buckets = []
    for bucket in buckets:
        bucket_name = bucket['Name']
        try:
            # Check bucket ACLs
            acl = s3.get_bucket_acl(Bucket=bucket_name)
            for grant in acl['Grants']:
                if 'URI' in grant['Grantee'] and 'AllUsers' in grant['Grantee']['URI']:
                     public_buckets.append({'Bucket': bucket_name, 'Reason': 'Public via ACL'})
                     continue

            # Check bucket policies
            try:
                policy_status = s3.get_bucket_policy_status(Bucket=bucket_name)
                if policy_status.get('PolicyStatus', {}).get('IsPublic'):
                    public_buckets.append({'Bucket': bucket_name, 'Reason': 'Public via Bucket Policy'})
            except ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
                    pass # No policy means not public via policy
                else:
                    raise
        except ClientError as e:
            print(f"Could not check S3 bucket {bucket_name}: {e}")
    
    # Remove duplicates
    return [dict(t) for t in {tuple(d.items()) for d in public_buckets}]


def check_iam_key_age(users, session, max_age_days=90):
    """
    Checks for IAM user access keys older than a specified number of days.
    
    Args:
        users: A list of user dictionaries.
        session: A boto3 session object.
        max_age_days: The maximum allowed age for access keys.
    
    Returns:
        A list of dictionaries for each aged key.
    """
    iam = session.client('iam')
    aged_keys = []
    age_limit = datetime.now(timezone.utc) - timedelta(days=max_age_days)

    for user in users:
        try:
            keys = iam.list_access_keys(UserName=user['UserName'])['AccessKeyMetadata']
            for key in keys:
                if key.get('Status') == 'Active' and key['CreateDate'] < age_limit:
                    aged_keys.append({
                        'UserName': user['UserName'],
                        'AccessKeyId': key['AccessKeyId'],
                        'CreateDate': key['CreateDate'].isoformat()
                    })
        except ClientError as e:
            print(f"Could not check access keys for user {user['UserName']}: {e}")
    return aged_keys

def check_unrestricted_security_groups(security_groups):
    """
    Checks for security groups with unrestricted inbound rules (0.0.0.0/0).
    
    Args:
        security_groups: A list of security group dictionaries.
    
    Returns:
        A list of dictionaries for each unrestricted rule found.
    """
    unrestricted_groups = []
    for sg in security_groups:
        for permission in sg.get('IpPermissions', []):
            for ip_range in permission.get('IpRanges', []):
                if ip_range.get('CidrIp') == '0.0.0.0/0':
                    port_range = f"{permission.get('FromPort', 'All')}-{permission.get('ToPort', 'All')}"
                    unrestricted_groups.append({
                        'GroupId': sg['GroupId'],
                        'GroupName': sg['GroupName'],
                        'PortRange': port_range
                    })
    return unrestricted_groups

def check_vpc_flow_logs(vpcs, session):
    """
    Checks for VPCs that do not have Flow Logs enabled.
    
    Args:
        vpcs: A list of VPC dictionaries.
        session: A boto3 session object.
    
    Returns:
        A list of VPC IDs without flow logs.
    """
    ec2 = session.client('ec2')
    vpcs_without_flow_logs = []
    try:
        flow_logs = ec2.describe_flow_logs()['FlowLogs']
        vpc_ids_with_flow_logs = {fl['ResourceId'] for fl in flow_logs}
        
        for vpc in vpcs:
            if vpc.get('VpcId') not in vpc_ids_with_flow_logs:
                vpcs_without_flow_logs.append(vpc.get('VpcId'))
    except ClientError as e:
        print(f"Error checking VPC flow logs: {e}")
    return vpcs_without_flow_logs

def check_cloudtrail_status(trails):
    """
    Checks the status of CloudTrail trails to ensure they are logging.
    
    Args:
        trails: A list of trail dictionaries.
    
    Returns:
        A list of trail status dictionaries.
    """
    return [{'Name': t.get('Name'), 'IsLogging': t.get('is_logging', False)} for t in trails if t.get('Name')]

def check_s3_lifecycle(buckets, session):
    """
    Checks for S3 buckets that do not have a lifecycle policy.
    
    Args:
        buckets: A list of bucket dictionaries.
        session: A boto3 session object.
    
    Returns:
        A list of bucket names without lifecycle policies.
    """
    s3 = session.client('s3')
    no_lifecycle_buckets = []
    for bucket in buckets:
        bucket_name = bucket.get('Name')
        if not bucket_name:
            continue
        try:
            s3.get_bucket_lifecycle_configuration(Bucket=bucket_name)
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchLifecycleConfiguration':
                no_lifecycle_buckets.append(bucket_name)
            else:
                print(f"Could not get lifecycle config for {bucket_name}: {e}")
    return no_lifecycle_buckets

def check_compute_optimizer(session):
    """
    Checks if AWS Compute Optimizer is enabled.
    
    Returns:
        A dictionary with status or error information.
    """
    co = session.client('compute-optimizer')
    try:
        status = co.get_enrollment_status()
        # Defensive check for the 'Status' key
        if status.get('Status') != 'Active':
            return {'error': 'Not enabled', 'status': status.get('Status', 'Unknown')}
        return {'status': 'Active'}
    except ClientError as e:
        return {'error': str(e)}

def check_rds_multi_az(rds_instances):
    """
    Checks if RDS instances are configured for Multi-AZ deployment.
    
    Args:
        rds_instances: A list of RDS instance dictionaries.
    
    Returns:
        A list of dictionaries with Multi-AZ status for each instance.
    """
    return [
        {
            'DBInstanceIdentifier': i.get('DBInstanceIdentifier'),
            'Engine': i.get('Engine'),
            'IsMultiAZ': i.get('MultiAZ')
        } for i in rds_instances
    ]

def check_ebs_backups(ebs_volumes, session, backup_age_days=7):
    """
    Checks if EBS volumes have a recent snapshot.
    
    Args:
        ebs_volumes: A list of EBS volume dictionaries.
        session: A boto3 session object.
        backup_age_days: The maximum age for a backup to be considered recent.
    
    Returns:
        A list of volume dictionaries that do not have recent backups.
    """
    ec2 = session.client('ec2')
    sts = session.client('sts')
    no_backup_volumes = []
    recent_date = datetime.now(timezone.utc) - timedelta(days=backup_age_days)
    
    try:
        account_id = sts.get_caller_identity()['Account']
    except ClientError as e:
        print(f"Could not get AWS Account ID: {e}")
        return {"error": "Could not determine AWS Account ID to check snapshots."}

    for vol in ebs_volumes:
        vol_id = vol.get('VolumeId')
        if not vol_id:
            continue
        try:
            snapshots = ec2.describe_snapshots(
                OwnerIds=[account_id],
                Filters=[{'Name': 'volume-id', 'Values': [vol_id]}]
            )['Snapshots']
            
            if not any(snap.get('StartTime') > recent_date for snap in snapshots):
                 no_backup_volumes.append({
                     'VolumeId': vol_id,
                     'SizeGiB': vol.get('Size')
                 })
        except ClientError as e:
            print(f"Error checking snapshots for volume {vol_id}: {e}")
            
    return no_backup_volumes

def check_ec2_detailed_monitoring(ec2_instances):
    """
    Checks if EC2 instances have detailed monitoring enabled.
    
    Args:
        ec2_instances: A list of EC2 instance dictionaries.
    
    Returns:
        A list of instance dictionaries without detailed monitoring.
    """
    no_detailed_monitoring = []
    for inst in ec2_instances:
        if inst.get('Monitoring', {}).get('State') == 'disabled':
             no_detailed_monitoring.append({
                 'InstanceId': inst.get('InstanceId'),
                 'Name': next((tag.get('Value') for tag in inst.get('Tags', []) if tag.get('Key') == 'Name'), 'N/A')
             })
    return no_detailed_monitoring

def check_cloudformation_drift(cfn_stacks, session):
    """
    Checks for drift in CloudFormation stacks.
    
    Args:
        cfn_stacks: A list of stack summary dictionaries.
        session: A boto3 session object.
    
    Returns:
        A list of stacks that have drifted.
    """
    cfn = session.client('cloudformation')
    drifted_stacks = []
    for stack in cfn_stacks:
        stack_name = stack.get('StackName')
        if not stack_name:
            continue
        try:
            drift_status_response = cfn.detect_stack_drift(StackName=stack_name)
            drift_detection_id = drift_status_response['StackDriftDetectionId']
            
            # Manual polling loop to wait for drift detection to complete
            while True:
                status = cfn.describe_stack_drift_detection_status(
                    StackDriftDetectionId=drift_detection_id
                )
                if status['DetectionStatus'] in ['DETECTION_COMPLETE', 'DETECTION_FAILED']:
                    break
                time.sleep(5) # Wait for 5 seconds before checking again

            if status.get('StackDriftStatus') == 'DRIFTED':
                drifted_stacks.append({
                    'StackName': stack_name,
                    'DriftStatus': status.get('StackDriftStatus')
                })
        except ClientError as e:
            if "Drift detection is not supported" in str(e):
                pass
            else:
                 print(f"Could not check drift for stack {stack_name}: {e}")
    return drifted_stacks
