import boto3
import datetime

def get_data_transfer_cost():
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
