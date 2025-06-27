import boto3
from botocore.exceptions import ClientError

# This file contains functions to discover resources in the AWS account.
# Each function creates its own boto3 client and does not require a session object to be passed in.

def list_iam_users():
    """Lists all IAM users."""
    iam = boto3.client('iam')
    try:
        # The list_users operation returns a paginator, but for most accounts,
        # a single call is sufficient. For very large accounts, you might implement pagination.
        return iam.list_users()['Users']
    except ClientError as e:
        print(f"Error listing IAM users: {e}")
        return []

def list_s3_buckets():
    """Lists all S3 buckets."""
    s3 = boto3.client('s3')
    try:
        return s3.list_buckets()['Buckets']
    except ClientError as e:
        print(f"Error listing S3 buckets: {e}")
        return []

def list_ec2_instances():
    """Lists all EC2 instances."""
    ec2 = boto3.client('ec2')
    try:
        # describe_instances returns a nested structure. We extract the instances.
        reservations = ec2.describe_instances()['Reservations']
        instances = [instance for reservation in reservations for instance in reservation['Instances']]
        return instances
    except ClientError as e:
        print(f"Error listing EC2 instances: {e}")
        return []

def list_rds_instances():
    """Lists all RDS DB instances."""
    rds = boto3.client('rds')
    try:
        return rds.describe_db_instances()['DBInstances']
    except ClientError as e:
        print(f"Error listing RDS instances: {e}")
        return []

def list_vpcs():
    """Lists all VPCs."""
    ec2 = boto3.client('ec2')
    try:
        return ec2.describe_vpcs()['Vpcs']
    except ClientError as e:
        print(f"Error listing VPCs: {e}")
        return []

def list_cloudtrails():
    """Lists all CloudTrail trails."""
    cloudtrail = boto3.client('cloudtrail')
    try:
        return cloudtrail.describe_trails()['trailList']
    except ClientError as e:
        print(f"Error listing CloudTrails: {e}")
        return []

def list_security_groups():
    """Lists all security groups."""
    ec2 = boto3.client('ec2')
    try:
        return ec2.describe_security_groups()['SecurityGroups']
    except ClientError as e:
        print(f"Error listing security groups: {e}")
        return []

def list_ebs_volumes():
    """Lists all EBS volumes."""
    ec2 = boto3.client('ec2')
    try:
        return ec2.describe_volumes()['Volumes']
    except ClientError as e:
        print(f"Error listing EBS volumes: {e}")
        return []

def list_cloudformation_stacks():
    """Lists all CloudFormation stacks."""
    cfn = boto3.client('cloudformation')
    try:
        # We only care about stacks that are in a final state, not DELETED.
        all_stacks = []
        paginator = cfn.get_paginator('list_stacks')
        for page in paginator.paginate(StackStatusFilter=[
            'CREATE_COMPLETE', 'UPDATE_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE', 
            'IMPORT_COMPLETE', 'IMPORT_ROLLBACK_COMPLETE'
        ]):
            all_stacks.extend(page['StackSummaries'])
        return all_stacks
    except ClientError as e:
        print(f"Error listing CloudFormation stacks: {e}")
        return []

