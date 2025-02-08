## Resource Cleanup


#1. Empty S3 Buckets:

# cleanup_resources.py
import boto3
import json
import subprocess

def get_bucket_names():
    cmd = "aws cloudformation describe-stacks --stack-name RetailDataLakeStack"
    result = subprocess.run(cmd.split(), capture_output=True, text=True)
    stack_info = json.loads(result.stdout)
    
    buckets = []
    for output in stack_info['Stacks'][0]['Outputs']:
        if 'Ref' in output['OutputKey'] and 'Zone' in output['OutputKey']:
            buckets.append(output['OutputValue'])
    return buckets

def empty_bucket(bucket_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    bucket.objects.all().delete()
    print(f"Emptied bucket: {bucket_name}")

if __name__ == "__main__":
    buckets = get_bucket_names()
    for bucket in buckets:
        empty_bucket(bucket)