import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta, timezone

def get_unattached_ebs_volumes(session):
    """
    Identifies and returns a list of unattached EBS volumes.

    Args:
        session: A Boto3 session object.

    Returns:
        A list of dictionaries, where each dictionary represents an unattached EBS volume.
    """
    ec2 = session.client('ec2')
    unattached_volumes = []
    try:
        # CORRECTED: 'Value' should be 'Values' and it should be a list.
        volumes = ec2.describe_volumes(Filters=[{'Name': 'status', 'Values': ['available']}])
        for volume in volumes.get('Volumes', []):
            unattached_volumes.append({
                'VolumeId': volume.get('VolumeId'),
                'Size': volume.get('Size'),
                'CreateTime': volume.get('CreateTime').isoformat() if volume.get('CreateTime') else None
            })
    except ClientError as e:
        print(f"Error checking for unattached EBS volumes: {e}")
    return unattached_volumes

def get_idle_load_balancers(session):
    """
    Identifies and returns a list of idle Application and Network Load Balancers.
    An ELB is considered idle if it has no registered instances/targets.

    Args:
        session: A Boto3 session object.

    Returns:
        A list of dictionaries, where each dictionary represents an idle load balancer.
    """
    elbv2 = session.client('elbv2')
    idle_lbs = []
    try:
        load_balancers = elbv2.describe_load_balancers().get('LoadBalancers', [])
        for lb in load_balancers:
            lb_arn = lb.get('LoadBalancerArn')
            if not lb_arn:
                continue
                
            target_groups = elbv2.describe_target_groups(LoadBalancerArn=lb_arn).get('TargetGroups', [])
            if not target_groups:
                 idle_lbs.append({
                    'Name': lb.get('LoadBalancerName'),
                    'Type': lb.get('Type'),
                    'Reason': 'No target groups associated.'
                })
                 continue
            
            has_healthy_targets = False
            for tg in target_groups:
                tg_arn = tg.get('TargetGroupArn')
                if not tg_arn:
                    continue
                health_descriptions = elbv2.describe_target_health(TargetGroupArn=tg_arn).get('TargetHealthDescriptions', [])
                if any(target.get('TargetHealth', {}).get('State') == 'healthy' for target in health_descriptions):
                    has_healthy_targets = True
                    break
            
            if not has_healthy_targets:
                 idle_lbs.append({
                    'Name': lb.get('LoadBalancerName'),
                    'Type': lb.get('Type'),
                    'Reason': 'No healthy targets registered.'
                })

    except ClientError as e:
        print(f"Error checking for idle load balancers: {e}")
    return idle_lbs

def get_old_ebs_snapshots(session):
    """
    Identifies and returns a list of EBS snapshots older than one year.

    Args:
        session: A Boto3 session object.

    Returns:
        A list of dictionaries, where each dictionary represents an old EBS snapshot.
    """
    ec2 = session.client('ec2')
    sts = session.client('sts')
    old_snapshots = []
    one_year_ago = datetime.now(timezone.utc) - timedelta(days=365)
    
    try:
        owner_id = sts.get_caller_identity().get('Account')
        paginator = ec2.get_paginator('describe_snapshots')
        
        for page in paginator.paginate(OwnerIds=[owner_id]):
            for snapshot in page.get('Snapshots', []):
                if snapshot.get('StartTime') and snapshot.get('StartTime') < one_year_ago:
                    old_snapshots.append({
                        'SnapshotId': snapshot.get('SnapshotId'),
                        'VolumeId': snapshot.get('VolumeId', 'N/A'),
                        'StartTime': snapshot.get('StartTime').isoformat(),
                        'VolumeSize': snapshot.get('VolumeSize', 'N/A')
                    })
    except ClientError as e:
        print(f"Error checking for old EBS snapshots: {e}")
        if "AuthFailure" in str(e):
            print("Could not check snapshots due to authentication failure. You may not be the owner.")
        else:
            # Don't raise, just return what we have
            pass
    return old_snapshots

def run_all_advanced_checks(session):
    """
    Runs all advanced checks and aggregates the results.

    Args:
        session: A Boto3 session object.

    Returns:
        A dictionary containing the results of all advanced checks.
    """
    results = {
        "cost_optimization": {
            "unattached_ebs_volumes": get_unattached_ebs_volumes(session),
            "idle_load_balancers": get_idle_load_balancers(session),
            "old_ebs_snapshots": get_old_ebs_snapshots(session)
        }
    }
    return results
