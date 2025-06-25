# core/war_mapper.py

def generate_autofilled_answers():
    """
    Returns a static dictionary of autofilled answers for the WAR tool.
    This function does not require a boto3 client as it returns hardcoded data.
    """
    return {
        'Operational Excellence': 'Basic monitoring in place. Consider adding CloudWatch alarms.',
        'Security': 'Some users missing MFA. S3 buckets need encryption.',
    }
