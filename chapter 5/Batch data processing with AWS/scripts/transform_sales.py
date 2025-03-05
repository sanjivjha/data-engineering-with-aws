import sys
import boto3
import json
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, current_timestamp, lit

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
error_topic = "arn:aws:sns:ap-south-1:359373501475:retail-etl-notifications"

print(f"Using hardcoded parameters:")
print(f"  processed_bucket: {processed_bucket}")
print(f"  error_topic: {error_topic}")

# Initialize job
job = Job(glueContext)
job.init(job_name, args)
sns = boto3.client('sns')

try:
    # Log job start
    print(f"Starting transformation job")
    
    # Read validated sales data
    validated_sales_path = f"s3://{processed_bucket}/sales/validated/"
    print(f"Reading validated data from: {validated_sales_path}")
    
    validated_sales = glueContext.create_dynamic_frame.from_options(
        connection_type="s3",
        connection_options={"paths": [validated_sales_path]},
        format="parquet"
    )
    
    # Check if we have data to process
    if validated_sales.count() == 0:
        print("No validated sales data found")
        sys.exit(0)
    
    print(f"Found {validated_sales.count()} records to transform")
    
    # Print the schema for debugging
    print("Schema of validated data:")
    validated_sales.printSchema()
    
    # Convert to DataFrame for operations
    sales_df = validated_sales.toDF()
    
    # Display a sample row for debugging
    print("Sample row from validated data:")
    if sales_df.count() > 0:
        sample = sales_df.limit(1).collect()
        for row in sample:
            print(row)
    
    # Read product reference data
    try:
        products = glueContext.create_dynamic_frame.from_catalog(
            database="retail_etl",
            table_name="products"
        )
        print(f"Found {products.count()} products for enrichment")
        enriched_sales = Join.apply(
            validated_sales, 
            products, 
            "product_id", 
            "product_id"
        )
        print(f"Enriched {enriched_sales.count()} records with product data")
        enriched_df = enriched_sales.toDF()
    except Exception as e:
        print(f"Warning: Could not read or join product data: {str(e)}")
        enriched_df = sales_df
        print("Proceeding without product enrichment")
    
    # Calculate derived fields
    # Add a total_value field if price exists, otherwise use sales_amount
    if 'price' in enriched_df.columns:
        transformed_df = enriched_df.withColumn(
            "total_value", col("quantity") * col("price")
        )
    else:
        transformed_df = enriched_df.withColumn(
            "total_value", col("sales_amount")
        )
    
    # Add processing metadata
    transformed_df = transformed_df.withColumn(
        "processing_timestamp", current_timestamp()
    )
    
    # Print the final schema for debugging
    print("Final schema of transformed data:")
    transformed_df.printSchema()
    
    # Write transformed data - IMPORTANT: NO PARTITIONING
    output_path = f"s3://{processed_bucket}/sales/transformed/"
    print(f"Writing transformed data to: {output_path} (without partitioning)")
    
    # Write without partitioning for now to avoid the error
    transformed_df.write.mode("overwrite").parquet(output_path)
    
    print(f"Transformation complete. Processed {transformed_df.count()} records")
    
except Exception as e:
    # Error handling
    error_message = str(e)
    print(f"Job failed: {error_message}")
    
    # Send notification
    try:
        sns.publish(
            TopicArn=error_topic,
            Subject=f"ETL Transform Job Failed: {job_name}",
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