# core/architecture_export.py
import json
import boto3

def export_architecture_json(s3_client, filename='architecture.json'):
    """
    Performs a basic discovery action (listing S3 buckets) using the provided
    s3 client and exports the findings to a JSON file.
    """
    try:
        # Use the provided s3_client to make the API call
        buckets_data = s3_client.list_buckets()

        # Process the data to be JSON serializable (handling datetime)
        processed_buckets = []
        for bucket in buckets_data.get('Buckets', []):
            processed_buckets.append({
                'Name': bucket['Name'],
                'CreationDate': bucket['CreationDate'].isoformat()
            })

        output_data = {
            "S3Buckets": processed_buckets,
            "Owner": buckets_data.get('Owner', {})
        }

        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=4)
        
        return {"status": "success", "file": filename}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

