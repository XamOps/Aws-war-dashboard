# core/discovery.py
import boto3

def list_ec2_instances():
    ec2 = boto3.client('ec2')
    try:
        return ec2.describe_instances()
    except Exception as e:
        return {"error": f"Could not describe EC2 instances. Error: {e}"}

def list_s3_buckets():
    s3 = boto3.client('s3')
    try:
        return s3.list_buckets()
    except Exception as e:
        return {"error": f"Could not list S3 buckets. Error: {e}"}
