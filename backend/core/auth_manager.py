# backend/core/auth_manager.py
import boto3
import uuid

def get_boto3_client(service_name, role_arn=None):
    """
    Creates a boto3 client for a given service.
    If a role_arn is provided, it assumes that role first.
    Otherwise, it uses the local environment's default credentials.
    """
    if not role_arn:
        # This is used for local testing without assuming a role.
        # In the production app, role_arn will always be provided.
        print("Warning: No Role ARN provided. Using default credentials.")
        return boto3.client(service_name)
        
    try:
        sts_client = boto3.client('sts')
        
        # Generate a unique session name for each assume role call
        session_name = f"cloudguard-scan-{uuid.uuid4()}"
        
        assumed_role_object = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName=session_name
        )
        
        credentials = assumed_role_object['Credentials']
        
        # Create the service client using the temporary credentials from the assumed role
        return boto3.client(
            service_name,
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'],
        )
    except Exception as e:
        print(f"FATAL: Error assuming role {role_arn}: {e}")
        # This error is critical, so we return it to be handled by the API caller.
        return {"error": str(e)}

def test_role_connection(role_arn):
    """
    Tests the connection by attempting to assume the role and getting the caller identity.
    This is a lightweight way to verify the role ARN and trust policy are correct.
    """
    test_client = get_boto3_client('sts', role_arn=role_arn)
    
    # Check if get_boto3_client returned an error dictionary
    if isinstance(test_client, dict) and 'error' in test_client:
        return {"success": False, "error": test_client['error']}
        
    try:
        # Get the identity of the assumed role to confirm it works
        identity = test_client.get_caller_identity()
        return {
            "success": True, 
            "assumed_role_arn": identity['Arn'],
            "account_id": identity['Account']
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

