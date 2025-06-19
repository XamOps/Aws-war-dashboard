import boto3

def list_ec2_instances():
    ec2 = boto3.client('ec2')
    return ec2.describe_instances()

def list_s3_buckets():
    s3 = boto3.client('s3')
    return s3.list_buckets()
