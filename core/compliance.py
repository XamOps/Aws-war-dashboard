import boto3

def check_mfa():
    iam = boto3.client('iam')
    users = iam.list_users()['Users']
    non_compliant = []
    for user in users:
        mfa = iam.list_mfa_devices(UserName=user['UserName'])
        if not mfa['MFADevices']:
            non_compliant.append(user['UserName'])
    return non_compliant
