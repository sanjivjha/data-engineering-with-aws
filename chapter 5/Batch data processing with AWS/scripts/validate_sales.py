import sys
import boto3
import json
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, lit, current_timestamp

# Initialize Glue context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Debugging: Print all command line arguments
print("Command line arguments:")
for i, arg in enumerate(sys.argv):
    print(f"  [{i}] {arg}")

# Get job name only from arguments
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
job_name = args['JOB_NAME']

# HARDCODING PARAMETERS FOR TROUBLESHOOTING
# Replace these with your actual bucket names and SNS topic ARN
raw_bucket = "retail-etl-raw"
processed_bucket = "retail-etl-processed"
error_topic = "arn:aws:sns:ap-south-1:359373501475:retail-etl-notifications"

print(f"Using hardcoded parameters:")
print(f"  raw_bucket: {raw_bucket}")
print(f"  processed_bucket: {processed_bucket}")
print(f"  error_topic: {error_topic}")

# Initialize job
job = Job(glueContext)
job.init(job_name, args)
sns = boto3.client('sns')

try:
    # Log job start
    print(f"Starting validation job")
    
    # Read raw sales data
    raw_sales_path = f"s3://{raw_bucket}/sales/"
    print(f"Reading data from: {raw_sales_path}")
    
    raw_sales = glueContext.create_dynamic_frame.from_options(
        connection_type="s3",
        connection_options={"paths": [raw_sales_path]},
        format="csv",
        format_options={"withHeader": True}
    )
    
    # Check if data exists
    if raw_sales.count() == 0:
        raise Exception(f"No data found at {raw_sales_path}")
    
    print(f"Found {raw_sales.count()} records to process")
    
    # Convert to DataFrame for validation
    sales_df = raw_sales.toDF()
    
    # Identify invalid records (Dead Letter Pattern)
    invalid_records = sales_df.filter(
        (col("quantity").isNull()) | 
        (col("sales_amount").isNull()) | 
        (col("store_id") == "") | 
        (col("product_id") == "")
    )
    
    invalid_count = invalid_records.count()
    print(f"Found {invalid_count} invalid records")
    
    if invalid_count > 0:
        # Save invalid records for analysis
        error_path = f"s3://{raw_bucket}/errors/sales/"
        print(f"Writing invalid records to: {error_path}")
        
        invalid_records.write.mode("append").parquet(error_path)
        
        # Send notification
        sns.publish(
            TopicArn=error_topic,
            Subject="Data Quality Issues Detected",
            Message=json.dumps({
                "job_name": job_name,
                "invalid_record_count": invalid_count,
                "error_location": error_path
            })
        )
    
    # Process valid records
    valid_records = sales_df.filter(
        (col("quantity").isNotNull()) &
        (col("sales_amount").isNotNull()) &
        (col("store_id") != "") &
        (col("product_id") != "")
    )
    
    valid_count = valid_records.count()
    print(f"Processing {valid_count} valid records")
    
    # Add processing metadata
    valid_records = valid_records.withColumn(
        "processing_timestamp", current_timestamp()
    ).withColumn(
        "data_quality_status", lit("VALID")
    )
    
    # Write to processed zone
    output_path = f"s3://{processed_bucket}/sales/validated/"
    print(f"Writing validated data to: {output_path}")
    
    valid_records.write.partitionBy("date").parquet(output_path)
    
    print(f"Validation complete. Valid: {valid_count}, Invalid: {invalid_count}")
    
except Exception as e:
    # Error handling
    error_message = str(e)
    print(f"Job failed: {error_message}")
    
    # Send notification
    try:
        sns.publish(
            TopicArn=error_topic,
            Subject=f"ETL Validation Job Failed: {job_name}",
            Message=json.dumps({
                "job_name": job_name,
                "error": error_message
            })
        )
        print("Sent error notification to SNS")
    except Exception as sns_error:
        print(f"Failed to send SNS notification: {str(sns_error)}")
    
    raise
    
finally:
    # Always commit job state
    job.commit()
    print("Job state committed")