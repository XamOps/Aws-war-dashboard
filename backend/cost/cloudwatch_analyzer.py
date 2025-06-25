# cost/cloudwatch_analyzer.py
import boto3
import datetime

def get_data_transfer_cost():
    # This is your original function
    cw = boto3.client('cloudwatch')
    end = datetime.datetime.utcnow()
    start = end - datetime.timedelta(days=7)
    result = {}
    for metric in ['NetworkOut', 'BytesDownloaded']:
        res = cw.get_metric_statistics(
            Namespace='AWS/EC2' if metric == 'NetworkOut' else 'AWS/S3',
            MetricName=metric,
            StartTime=start,
            EndTime=end,
            Period=86400,
            Statistics=['Sum']
        )
        gb = sum([pt['Sum'] for pt in res['Datapoints']]) / (1024 ** 3)
        result[metric] = round(gb, 2)
    return result

# --- NEW FUNCTION TO GET REAL THROTTLING DATA ---
def get_api_throttle_events(cloudwatch_client):
    """
    Queries CloudWatch for the sum of ThrottledRequests across key services
    over the last 24 hours.
    """
    throttled_count = 0
    end_time = datetime.datetime.utcnow()
    start_time = end_time - datetime.timedelta(hours=24)

    # List of key services to check for throttling
    services = ['EC2', 'S3', 'IAM', 'RDS', 'Lambda']

    queries = []
    for i, service in enumerate(services):
        queries.append({
            'Id': f"throttling{i}",
            'MetricStat': {
                'Metric': {
                    'Namespace': 'AWS/Usage',
                    'MetricName': 'CallCount',
                    'Dimensions': [
                        {'Name': 'Service', 'Value': service},
                        {'Name': 'Type', 'Value': 'API'},
                        {'Name': 'Resource', 'Value': 'ThrottledRequests'}
                    ]
                },
                'Period': 86400, # 24 hours
                'Stat': 'Sum',
            },
            'ReturnData': True,
        })
        
    try:
        response = cloudwatch_client.get_metric_data(
            MetricDataQueries=queries,
            StartTime=start_time,
            EndTime=end_time
        )
        
        for result in response['MetricDataResults']:
            if result['Values']:
                throttled_count += sum(result['Values'])
                
    except Exception as e:
        print(f"Could not retrieve throttling metrics from CloudWatch: {e}")
        return -1 # Return -1 to indicate an error

    return int(throttled_count)
