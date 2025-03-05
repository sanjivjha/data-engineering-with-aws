import boto3
import json
import time

# Configuration with consistent naming
PROJECT_NAME = "retail-etl"
REGION = "ap-south-1"
ACCOUNT_ID = "359373501475"  # Replace with your AWS account ID

# Use consistent naming instead of timestamps
BUCKET_PREFIX = f"{PROJECT_NAME}"
RAW_BUCKET = f"{BUCKET_PREFIX}-raw"
PROCESSED_BUCKET = f"{BUCKET_PREFIX}-processed"
ANALYTICS_BUCKET = f"{BUCKET_PREFIX}-analytics"
DATABASE_NAME = PROJECT_NAME.replace('-', '_')
ERROR_TOPIC_NAME = f"{PROJECT_NAME}-notifications"

# Initialize AWS clients
s3_client = boto3.client('s3')
glue_client = boto3.client('glue')
sns_client = boto3.client('sns')
sfn_client = boto3.client('stepfunctions')
iam_client = boto3.client('iam')

def create_infrastructure():
    """Create all required AWS resources for the ETL pipeline"""
    print("\n== Creating S3 Buckets ==")
    print("S3 buckets implement the medallion architecture with dedicated storage for each data zone:")
    
    buckets = {
        'raw': RAW_BUCKET,
        'processed': PROCESSED_BUCKET,
        'analytics': ANALYTICS_BUCKET
    }
    
    for purpose, bucket_name in buckets.items():
        print(f"Creating {purpose} bucket: {bucket_name}")
        
        # For regions other than us-east-1, specify the location constraint
        if REGION == 'us-east-1':
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': REGION
                }
            )
            
        if purpose == 'raw':
            print("  - Raw bucket: Stores incoming data, reference data, and scripts")
        elif purpose == 'processed':
            print("  - Processed bucket: Stores validated and transformed datasets")
        else:
            print("  - Analytics bucket: Stores business-ready datasets for reporting")
    
    # Create SNS topic for notifications
    print("\n== Creating SNS Topic ==")
    print("SNS topic enables error notifications and alerting for the ETL process:")
    
    topic_response = sns_client.create_topic(Name=ERROR_TOPIC_NAME)
    topic_arn = topic_response['TopicArn']
    print(f"Created SNS topic: {topic_arn}")
    print("  - Provides real-time alerting for data quality issues")
    print("  - Sends notifications when critical job failures occur")
    print("  - Enables human intervention for error recovery")
    
    # Create IAM role for Glue
    print("\n== Creating IAM Role for Glue ==")
    print("IAM role provides necessary permissions for Glue jobs to access resources:")
    
    role_name = f"{PROJECT_NAME}-glue-role"
    assume_role_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "glue.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_role_policy)
        )
        
        # Attach policies
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn="arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
        )
        
        # Create custom policy for S3 and SNS access
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["s3:*"],
                    "Resource": [
                        f"arn:aws:s3:::{buckets['raw']}/*",
                        f"arn:aws:s3:::{buckets['raw']}",
                        f"arn:aws:s3:::{buckets['processed']}/*",
                        f"arn:aws:s3:::{buckets['processed']}",
                        f"arn:aws:s3:::{buckets['analytics']}/*",
                        f"arn:aws:s3:::{buckets['analytics']}"
                    ]
                },
                {
                    "Effect": "Allow",
                    "Action": ["sns:Publish"],
                    "Resource": [topic_arn]
                }
            ]
        }
        
        policy_name = f"{PROJECT_NAME}-glue-s3-sns-policy"
        iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document)
        )
        
        print(f"Created IAM role: {role_name}")
        print("  - Allows Glue jobs to read from and write to S3 buckets")
        print("  - Enables jobs to publish error notifications to SNS")
        print("  - Provides access to Glue Data Catalog for metadata")
        
        # Wait for role to propagate
        print("\nWaiting for IAM role propagation...")
        time.sleep(10)
        
        # Create Glue database
        print("\n== Creating Glue Database ==")
        print("Glue database provides the metadata repository for our data lake:")
        
        glue_client.create_database(
            DatabaseInput={
                'Name': DATABASE_NAME,
                'Description': 'Retail Sales Data Catalog'
            }
        )
        print(f"Created Glue database: {DATABASE_NAME}")
        print("  - Stores table definitions and schema information")
        print("  - Enables schema evolution tracking over time")
        print("  - Provides a unified view of data across processing stages")
        
        # Create Glue jobs
        print("\n== Creating Glue ETL Jobs ==")
        print("Glue jobs implement the three main stages of our ETL pipeline:")
        
        role_arn = f"arn:aws:iam::{ACCOUNT_ID}:role/{role_name}"
        job_config = {
            'validate_sales': {
                'script': 'validate_sales.py',
                'description': 'Validates raw sales data'
            },
            'transform_sales': {
                'script': 'transform_sales.py',
                'description': 'Transforms and enriches validated sales data'
            },
            'generate_analytics': {
                'script': 'generate_analytics.py',
                'description': 'Generates analytics from transformed data'
            }
        }
        
        for job_name, config in job_config.items():
            script_location = f"s3://{buckets['raw']}/scripts/{config['script']}"
            
            # Create job with properly configured parameters
            # FIXED PARAMETER PASSING: Using multiple formats in DefaultArguments
            glue_client.create_job(
                Name=job_name,
                Role=role_arn,
                Description=config['description'],
                GlueVersion='3.0',
                Command={
                    'Name': 'glueetl',
                    'ScriptLocation': script_location,
                    'PythonVersion': '3'
                },
                DefaultArguments={
                    # Standard Glue parameters
                    '--enable-job-bookmarks': 'true',
                    '--job-bookmark-option': 'job-bookmark-enable',
                    '--TempDir': f"s3://{buckets['raw']}/temp/",
                    
                    # Job-specific parameters in multiple formats
                    # Format 1: Standard format with -- prefix
                    '--raw-bucket': RAW_BUCKET,
                    '--processed-bucket': PROCESSED_BUCKET,
                    '--analytics-bucket': ANALYTICS_BUCKET,
                    '--error-topic': topic_arn,
                    
                    # Format 2: Key=value format with -- prefix
                    '--raw-bucket=': RAW_BUCKET,
                    '--processed-bucket=': PROCESSED_BUCKET,
                    '--analytics-bucket=': ANALYTICS_BUCKET,
                    '--error-topic=': topic_arn,
                    
                    # Format 3: Plain keys without prefix
                    'raw-bucket': RAW_BUCKET,
                    'processed-bucket': PROCESSED_BUCKET,
                    'analytics-bucket': ANALYTICS_BUCKET,
                    'error-topic': topic_arn
                },
                MaxRetries=1,
                WorkerType='G.1X',
                NumberOfWorkers=2,
                Timeout=60
            )
            print(f"Created Glue job: {job_name}")
            
            if job_name == 'validate_sales':
                print("  - Validation job: Implements data quality checks and the Dead Letter Pattern")
                print("  - Separates valid and invalid records for processing")
                print("  - Detects and alerts on data quality issues")
            elif job_name == 'transform_sales':
                print("  - Transformation job: Enriches data with reference information")
                print("  - Implements business logic and data standardization")
                print("  - Prepares data for analytical processing")
            else:
                print("  - Analytics job: Aggregates data into business metrics")
                print("  - Creates summary tables for reporting")
                print("  - Optimizes data for common query patterns")
        
        # Create Step Functions state machine
        print("\n== Creating Step Functions Workflow ==")
        print("Step Functions orchestrates the ETL process with robust error handling:")
        
        # First create a role for Step Functions
        sfn_role_name = f"{PROJECT_NAME}-sfn-role"
        
        # Delete role if it exists
        try:
            iam_client.delete_role(RoleName=sfn_role_name)
            print(f"  - Deleted existing Step Functions role")
        except:
            pass  # Role might not exist
            
        sfn_role = iam_client.create_role(
            RoleName=sfn_role_name,
            AssumeRolePolicyDocument=json.dumps({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "states.amazonaws.com"},
                        "Action": "sts:AssumeRole"
                    }
                ]
            })
        )
        
        # Attach policies to Step Functions role
        iam_client.attach_role_policy(
            RoleName=sfn_role_name,
            PolicyArn="arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
        )
        
        # Custom policy for Step Functions
        sfn_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "glue:StartJobRun",
                        "glue:GetJobRun",
                        "glue:GetJobRuns",
                        "glue:BatchStopJobRun"
                    ],
                    "Resource": "*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "sns:Publish"
                    ],
                    "Resource": [topic_arn]
                }
            ]
        }
        
        iam_client.put_role_policy(
            RoleName=sfn_role_name,
            PolicyName=f"{PROJECT_NAME}-sfn-policy",
            PolicyDocument=json.dumps(sfn_policy)
        )
        
        print(f"  - Created Step Functions role: {sfn_role_name}")
        
        # Define state machine
        state_machine_name = f"{PROJECT_NAME}-workflow"
        state_machine_definition = {
            "Comment": "Retail ETL Workflow",
            "StartAt": "ValidateSales",
            "States": {
                "ValidateSales": {
                    "Type": "Task",
                    "Resource": "arn:aws:states:::glue:startJobRun.sync",
                    "Parameters": {
                        "JobName": "validate_sales"
                    },
                    "Retry": [{
                        "ErrorEquals": ["Glue.ThrottlingException", "States.Timeout"],
                        "IntervalSeconds": 60,
                        "MaxAttempts": 3,
                        "BackoffRate": 2.0
                    }],
                    "Catch": [{
                        "ErrorEquals": ["States.ALL"],
                        "Next": "NotifyFailure"
                    }],
                    "Next": "TransformSales"
                },
                "TransformSales": {
                    "Type": "Task",
                    "Resource": "arn:aws:states:::glue:startJobRun.sync",
                    "Parameters": {
                        "JobName": "transform_sales"
                    },
                    "Retry": [{
                        "ErrorEquals": ["Glue.ThrottlingException", "States.Timeout"],
                        "IntervalSeconds": 60,
                        "MaxAttempts": 3,
                        "BackoffRate": 2.0
                    }],
                    "Catch": [{
                        "ErrorEquals": ["States.ALL"],
                        "Next": "NotifyFailure"
                    }],
                    "Next": "GenerateAnalytics"
                },
                "GenerateAnalytics": {
                    "Type": "Task",
                    "Resource": "arn:aws:states:::glue:startJobRun.sync",
                    "Parameters": {
                        "JobName": "generate_analytics"
                    },
                    "Retry": [{
                        "ErrorEquals": ["Glue.ThrottlingException", "States.Timeout"],
                        "IntervalSeconds": 60,
                        "MaxAttempts": 3,
                        "BackoffRate": 2.0
                    }],
                    "Catch": [{
                        "ErrorEquals": ["States.ALL"],
                        "Next": "NotifyFailure"
                    }],
                    "End": True
                },
                "NotifyFailure": {
                    "Type": "Task",
                    "Resource": "arn:aws:states:::sns:publish",
                    "Parameters": {
                        "TopicArn": topic_arn,
                        "Message": {
                            "Error.$": "$.Error",
                            "Cause.$": "$.Cause"
                        },
                        "Subject": "Retail ETL Workflow Failure"
                    },
                    "End": True
                }
            }
        }
        
        # Create the state machine
        response = sfn_client.create_state_machine(
            name=state_machine_name,
            definition=json.dumps(state_machine_definition),
            roleArn=sfn_role['Role']['Arn'],
            type="STANDARD"
        )
        
        state_machine_arn = response['stateMachineArn']
        print(f"  - Created state machine: {state_machine_name}")
        print(f"  - ARN: {state_machine_arn}")
        
        print("\n== Infrastructure Creation Complete ==")
        print("\nResource Summary:")
        print(f"- S3 Buckets: {', '.join(buckets.values())}")
        print(f"- SNS Topic: {topic_arn}")
        print(f"- Glue Database: {DATABASE_NAME}")
        print(f"- Glue Jobs: {', '.join(job_config.keys())}")
        print(f"- Step Functions: {state_machine_name}")
        
        # Add detailed next steps with actual commands
        print("\n== Next Steps ==")
        
        print("\n1. Upload Glue scripts to S3:")
        print("   These scripts implement the ETL logic for each processing stage")
        for job_name, config in job_config.items():
            print(f"   aws s3 cp scripts/{config['script']} s3://{buckets['raw']}/scripts/{config['script']}")
        
        print("\n2. Upload sample data to raw bucket:")
        print("   This data will be processed through the ETL pipeline")
        print(f"   aws s3 cp sample_data/sales.csv s3://{buckets['raw']}/sales/")
        print(f"   aws s3 cp sample_data/products.csv s3://{buckets['raw']}/reference/")
        
        print("\n3. Create and run a crawler for the reference data:")
        print("   This makes the product reference data available for the transformation job")
        print(f"   aws glue create-crawler \\")
        print(f"     --name {PROJECT_NAME}-reference-crawler \\")
        print(f"     --role {role_name} \\")
        print(f"     --database-name {DATABASE_NAME} \\")
        print(f"     --targets \"{{\\\"S3Targets\\\":[{{\\\"Path\\\":\\\"s3://{buckets['raw']}/reference/\\\"}}]}}\"")
        print(f"   aws glue start-crawler --name {PROJECT_NAME}-reference-crawler")
        
        print("\n4. Start the ETL workflow:")
        print("   This executes the entire ETL pipeline in sequence")
        print(f"   aws stepfunctions start-execution \\")
        print(f"     --state-machine-arn {state_machine_arn}")
        
    except Exception as e:
        print(f"Error creating infrastructure: {str(e)}")

if __name__ == "__main__":
    create_infrastructure()
    
    