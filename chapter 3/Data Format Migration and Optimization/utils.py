# src/utils.py

import boto3
import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import pyarrow as pa
import pyarrow.parquet as pq
from typing import Dict, List, Any
import yaml
import logging
from tqdm import tqdm
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
   level=logging.INFO,
   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AWSManager:
   """Handles AWS resource management"""
   
   def __init__(self):
       self.s3_client = boto3.client('s3')
       self.s3_resource = boto3.resource('s3')
   
   def create_buckets(self, config: Dict) -> None:
       """Create source and target S3 buckets if they don't exist"""
       for bucket in [config['aws']['source_bucket'], config['aws']['target_bucket']]:
           try:
               self.s3_client.head_bucket(Bucket=bucket)
               logger.info(f"Bucket {bucket} already exists")
           except:
               logger.info(f"Creating bucket {bucket}")
               self.s3_client.create_bucket(
                   Bucket=bucket,
                   CreateBucketConfiguration={'LocationConstraint': config['aws']['region']}
               )

   def clean_up_buckets(self, config: Dict) -> None:
       """Remove all objects from buckets"""
       for bucket in [config['aws']['source_bucket'], config['aws']['target_bucket']]:
           try:
               bucket_obj = self.s3_resource.Bucket(bucket)
               bucket_obj.objects.all().delete()
               logger.info(f"Cleaned up bucket {bucket}")
           except Exception as e:
               logger.error(f"Error cleaning bucket {bucket}: {str(e)}")

class DataGenerator:
   """Generates sample retail data"""
   
   def __init__(self, config: Dict):
       self.config = config
       self.fake = Faker()
       self.aws_manager = AWSManager()
       
   def generate_transactions(self) -> pd.DataFrame:
       """Generate transaction data"""
       logger.info("Generating transaction data...")
       
       records = []
       start_date = datetime.strptime(self.config['data_generation']['transactions']['date_range']['start'], '%Y-%m-%d')
       end_date = datetime.strptime(self.config['data_generation']['transactions']['date_range']['end'], '%Y-%m-%d')
       
       for _ in tqdm(range(self.config['data_generation']['transactions']['num_records'])):
           transaction_date = self.fake.date_time_between(start_date=start_date, end_date=end_date)
           
           record = {
               'transaction_id': self.fake.uuid4(),
               'customer_id': self.fake.uuid4(),
               'store_id': self.fake.random_int(min=1, max=100),
               'amount': round(self.fake.random.uniform(10, 1000), 2),
               'timestamp': transaction_date,
               'payment_method': self.fake.random_element(['credit_card', 'debit_card', 'cash', 'digital_wallet']),
               'category': self.fake.random_element(['electronics', 'clothing', 'groceries', 'home', 'sports'])
           }
           records.append(record)
           
       return pd.DataFrame(records)
   
   def generate_customers(self) -> pd.DataFrame:
       """Generate customer profile data"""
       logger.info("Generating customer data...")
       
       records = []
       for _ in tqdm(range(self.config['data_generation']['customers']['num_records'])):
           record = {
               'customer_id': self.fake.uuid4(),
               'name': self.fake.name(),
               'email': self.fake.email(),
               'country': self.fake.country(),
               'join_date': self.fake.date_between(start_date='-5y', end_date='today'),
               'segment': self.fake.random_element(['premium', 'standard', 'basic']),
               'age_group': self.fake.random_element(['18-25', '26-35', '36-45', '46-55', '55+'])
           }
           records.append(record)
           
       return pd.DataFrame(records)

class PerformanceAnalyzer:
   """Analyzes and compares format performance"""
   
   def __init__(self, spark):
       self.spark = spark
       
   def measure_query_performance(self, query: str, iterations: int = 3) -> Dict:
       """Measure query execution time"""
       execution_times = []
       
       for i in range(iterations):
           start_time = datetime.now()
           self.spark.sql(query).collect()
           end_time = datetime.now()
           execution_times.append((end_time - start_time).total_seconds())
           
       return {
           'mean': np.mean(execution_times),
           'min': np.min(execution_times),
           'max': np.max(execution_times),
           'std': np.std(execution_times)
       }
   
   def analyze_storage_metrics(self, bucket: str, prefix: str) -> Dict:
       """Analyze storage metrics for a given S3 path"""
       s3 = boto3.client('s3')
       total_size = 0
       object_count = 0
       
       paginator = s3.get_paginator('list_objects_v2')
       for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
           if 'Contents' in page:
               for obj in page['Contents']:
                   total_size += obj['Size']
                   object_count += 1
                   
       return {
           'total_size_gb': total_size / (1024 ** 3),
           'object_count': object_count,
           'avg_object_size_mb': (total_size / object_count) / (1024 ** 2) if object_count > 0 else 0
       }

def load_config() -> Dict:
   """Load configuration from yaml file"""
   with open('config/config.yaml', 'r') as file:
       return yaml.safe_load(file)

def setup_spark_session(app_name: str = "RetailFormatMigration"):
   """Create Spark session with Delta Lake support"""
   from pyspark.sql import SparkSession
   
   return SparkSession.builder \
       .appName(app_name) \
       .config("spark.jars.packages", "io.delta:delta-core_2.12:2.2.0") \
       .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
       .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
       .getOrCreate()

def format_size(size_bytes: int) -> str:
   """Convert bytes to human readable format"""
   for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
       if size_bytes < 1024:
           return f"{size_bytes:.2f} {unit}"
       size_bytes /= 1024