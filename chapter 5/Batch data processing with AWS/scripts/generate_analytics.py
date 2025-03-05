import sys
import boto3
import json
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, sum, avg, count, current_timestamp, lit, current_date

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
processed_bucket = "retail-etl-processed"
analytics_bucket = "retail-etl-analytics"
error_topic = "arn:aws:sns:ap-south-1:359373501475:retail-etl-notifications"

print(f"Using hardcoded parameters:")
print(f"  processed_bucket: {processed_bucket}")
print(f"  analytics_bucket: {analytics_bucket}")
print(f"  error_topic: {error_topic}")

# Initialize job
job = Job(glueContext)
job.init(job_name, args)
sns = boto3.client('sns')

try:
    # Log job start
    print(f"Starting analytics generation job")
    
    # Read transformed sales data
    transformed_sales_path = f"s3://{processed_bucket}/sales/transformed/"
    print(f"Reading transformed data from: {transformed_sales_path}")
    
    transformed_sales = glueContext.create_dynamic_frame.from_options(
        connection_type="s3",
        connection_options={"paths": [transformed_sales_path]},
        format="parquet"
    )
    
    # Check if we have data to process
    if transformed_sales.count() == 0:
        print("No transformed sales data found")
        sys.exit(0)
    
    print(f"Found {transformed_sales.count()} records to analyze")
    
    # Print schema for debugging
    print("Schema of transformed data:")
    transformed_sales.printSchema()
    
    # Convert to DataFrame for analytics
    sales_df = transformed_sales.toDF()
    
    # Create a default date column if it doesn't exist
    if 'date' not in sales_df.columns:
        print("Adding a date column with current date as we don't have one")
        sales_df = sales_df.withColumn("date", current_date())
    
    # Generate daily sales summary
    print("Generating daily sales summary")
    
    # Determine grouping columns based on available columns
    group_columns = []
    if "date" in sales_df.columns:
        group_columns.append("date")
    else:
        print("Warning: No date column available for grouping")
    
    if "store_id" in sales_df.columns:
        group_columns.append("store_id")
    
    if "category" in sales_df.columns:
        group_columns.append("category")
    
    # If no grouping columns, use a literal column
    if not group_columns:
        print("Warning: No grouping columns available, creating a default grouping")
        sales_df = sales_df.withColumn("analysis_group", lit("all"))
        group_columns = ["analysis_group"]
    
    print(f"Grouping by columns: {group_columns}")
    
    daily_sales = sales_df.groupBy(*group_columns).agg(
        sum("total_value").alias("total_sales"),
        count("*").alias("transaction_count"),
        avg("total_value").alias("avg_transaction_value")
    ).withColumn(
        "processing_timestamp", current_timestamp()
    )
    
    # Write analytics results (with or without partitioning)
    daily_sales_path = f"s3://{analytics_bucket}/daily_sales/"
    print(f"Writing daily sales summary to: {daily_sales_path}")
    
    if "date" in daily_sales.columns:
        print("Partitioning by date")
        daily_sales.write.partitionBy("date").parquet(daily_sales_path)
    else:
        print("Writing without partitioning")
        daily_sales.write.parquet(daily_sales_path)
    
    # Generate product performance analytics if product data available
    if "product_id" in sales_df.columns:
        print("Generating product performance analytics")
        
        # Use product_name if available, otherwise just use product_id
        group_cols = ["product_id"]
        if "product_name" in sales_df.columns:
            group_cols.append("product_name")
        
        product_sales = sales_df.groupBy(*group_cols).agg(
            sum(col("quantity").cast("double")).alias("total_quantity"),
            sum(col("total_value").cast("double")).alias("total_sales")
        ).withColumn(
            "processing_timestamp", current_timestamp()
        )
        
        # Write product analytics
        product_sales_path = f"s3://{analytics_bucket}/product_performance/"
        print(f"Writing product performance analytics to: {product_sales_path}")
        product_sales.write.parquet(product_sales_path)
    
    print(f"Analytics generation complete")
    
except Exception as e:
    # Error handling
    error_message = str(e)
    print(f"Job failed: {error_message}")
    print(f"Error type: {type(e).__name__}")
    
    # Send notification
    try:
        sns.publish(
            TopicArn=error_topic,
            Subject=f"ETL Analytics Job Failed: {job_name}",
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
    job.commit()
    print("Job state committed")