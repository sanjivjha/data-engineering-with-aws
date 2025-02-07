import boto3
import pandas as pd
import numpy as np
import subprocess
import json

def get_raw_bucket_name():
   cmd = "aws cloudformation describe-stacks --stack-name RetailDataLakeStack"
   result = subprocess.run(cmd.split(), capture_output=True, text=True)
   stack_info = json.loads(result.stdout)

   # Get bucket name from exports output that contains 'RawZone'
   for output in stack_info['Stacks'][0]['Outputs']:
       if 'RawZone' in output['OutputKey'] and 'Ref' in output['OutputKey']:
           return output['OutputValue']
   return None

def generate_and_upload_data():
   bucket_name = get_raw_bucket_name()
   print(f"Using bucket: {bucket_name}")
   
   dates = pd.date_range(start='2024-01-01', end='2024-02-07', freq='H')
   data = {
       'transaction_id': [f'TRX-{i:06d}' for i in range(len(dates))],
       'timestamp': dates,
       'amount': np.random.uniform(10, 1000, len(dates)),
       'store_id': np.random.choice(range(1, 51), len(dates))
   }
   df = pd.DataFrame(data)
   
   s3 = boto3.client('s3')
   
   for (year, month), group in df.groupby([df['timestamp'].dt.year, df['timestamp'].dt.month]):
       key = f"transactions/year={year}/month={month:02d}/data.parquet"
       s3.put_object(
           Bucket=bucket_name,
           Key=key,
           Body=group.to_parquet()
       )
       print(f"Uploaded: {key}")

if __name__ == "__main__":
   generate_and_upload_data()