# Retail ETL Pipeline Example

This project demonstrates a complete batch ETL workflow using AWS services, as described in Chapter 5 of "Data Engineering with AWS". The implementation showcases:

- ETL workflow orchestration with Step Functions
- Data validation and quality checks
- Error handling patterns (Dead Letter, Circuit Breaker, Retry)
- Metadata management
- Analytics generation

## Project Structure

```
chapter5-batch-etl/
├── infrastructure/
│   ├── app.py                      # Main infrastructure script
│   └── requirements.txt            # Dependencies
├── scripts/
│   ├── validate_sales.py           # Data validation Glue script
│   ├── transform_sales.py          # Data transformation Glue script
│   └── generate_analytics.py       # Analytics generation Glue script
├── sample_data/
│   ├── sales.csv                   # Sample sales data
│   └── products.csv                # Sample product data
└── README.md                       # Setup and usage instructions
```

## Key Components

1. **Data Storage Zones**
   - Raw Data: Original, unmodified data from source systems
   - Processed Data: Validated and transformed datasets
   - Analytics: Business-ready datasets optimized for reporting

2. **ETL Process Flow**
   - Data Validation: Quality checks and error isolation
   - Data Transformation: Enrichment and standardization
   - Analytics Generation: Metrics and aggregations

3. **Error Handling Patterns**
   - Dead Letter Pattern: Isolating invalid records for later analysis
   - Retry Pattern: Handling transient failures with backoff
   - Circuit Breaker Pattern: Preventing cascade failures
   - Checkpoint Pattern: Tracking progress for resumability

## Setup Instructions

### Prerequisites

- AWS account with appropriate permissions
- AWS CLI installed and configured
- Python 3.7 or higher

### Installation Steps

1. **Clone the repository**:
   ```
   git clone https://github.com/data-engineering-book/chapter5-batch-etl.git
   cd chapter5-batch-etl
   ```

2. **Configure AWS credentials**:
   ```
   aws configure
   ```

3. **Update the configuration** in `infrastructure/app.py`:
   - Set your AWS account ID
   - Modify region if needed

4. **Create the infrastructure**:
   ```
   cd infrastructure
   pip install -r requirements.txt
   python app.py
   ```

5. **Follow the next steps** output by the script to:
   - Upload scripts to S3
   - Upload sample data
   - Create and run a crawler for reference data
   - Start the ETL workflow

## Usage Examples

### Monitoring Job Execution

```bash
# Get the status of a Glue job run
aws glue get-job-run --job-name validate_sales --run-id jr_1234567890abcdef

# List all executions of the Step Functions state machine
aws stepfunctions list-executions --state-machine-arn arn:aws:states:region:account-id:stateMachine:retail-etl-workflow
```

### Triggering the Workflow Manually

```bash
# Start a new execution of the workflow
aws stepfunctions start-execution \
  --state-machine-arn arn:aws:states:region:account-id:stateMachine:retail-etl-workflow \
  --input '{"date": "2023-01-15"}'
```

### Reviewing Results

```bash
# List the analytics files generated
aws s3 ls s3://retail-etl-analytics-TIMESTAMP/daily_sales/

# View error records (if any)
aws s3 ls s3://retail-etl-raw-TIMESTAMP/errors/sales/
```

## Error Handling Demonstrations

The implementation demonstrates several key error handling patterns:

1. **Dead Letter Pattern** (in `validate_sales.py`)
   - Invalid records are isolated and stored for analysis
   - SNS notifications are sent for data quality issues
   - Processing continues with valid records

2. **Retry Pattern** (in Step Functions definition)
   - Transient errors are retried automatically
   - Exponential backoff prevents overwhelming resources
   - Limited retry attempts prevent infinite loops

3. **Circuit Breaker Pattern** (in error handling sections)
   - Critical failures trigger notifications
   - The workflow stops on permanent errors
   - Error context is preserved for analysis

4. **Checkpoint Pattern** (via job bookmarks)
   - Progress is tracked automatically
   - Processing can resume after failures
   - Duplicate processing is prevented

## Customization

The example can be extended in several ways:

1. **Additional Data Sources**
   - Create new Glue jobs for different data types
   - Add more tables to the Glue Data Catalog
   - Expand the Step Functions workflow

2. **Enhanced Monitoring**
   - Add CloudWatch alarms for job failures
   - Create a dashboard for ETL metrics
   - Implement detailed logging

3. **Scheduling**
   - Add EventBridge rules to trigger the workflow
   - Implement time-based or event-based triggers
   - Configure dependencies between workflows

## Cleanup

To avoid unnecessary charges, clean up the resources when finished:

```bash
# Empty S3 buckets
aws s3 rm s3://retail-etl-raw-TIMESTAMP --recursive
aws s3 rm s3://retail-etl-processed-TIMESTAMP --recursive
aws s3 rm s3://retail-etl-analytics-TIMESTAMP --recursive

# Delete S3 buckets
aws s3 rb s3://retail-etl-raw-TIMESTAMP
aws s3 rb s3://retail-etl-processed-TIMESTAMP
aws s3 rb s3://retail-etl-analytics-TIMESTAMP

# Delete Glue resources
aws glue delete-job --job-name validate_sales
aws glue delete-job --job-name transform_sales
aws glue delete-job --job-name generate_analytics
aws glue delete-crawler --name retail-etl-reference-crawler
aws glue delete-database --name retail_etl

# Delete SNS topic
aws sns delete-topic --topic-arn TOPIC_ARN

# Delete IAM role
aws iam delete-role-policy --role-name retail-etl-glue-role --policy-name retail-etl-glue-s3-sns-policy
aws iam detach-role-policy --role-name retail-etl-glue-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole
aws iam delete-role --role-name retail-etl-glue-role
```

# Verifying Your Retail ETL Pipeline

After successfully setting up your ETL infrastructure and running the workflow, here are some steps to verify everything is working properly and see the results:

## 1. Check Step Functions Execution

First, verify your workflow is running or has completed:

```bash
# Get the execution ARN from the start-execution command output
aws stepfunctions describe-execution \
  --execution-arn arn:aws:states:ap-south-1:359373501475:execution:retail-etl-workflow:EXECUTION_ID
```

You can also check the status through the AWS Console:
- Go to Step Functions
- Select your state machine (retail-etl-workflow)
- View the execution details, including the visual workflow

## 2. Monitor Glue Jobs

Check the status of individual Glue jobs:

```bash
# List recent job runs for validate_sales
aws glue get-job-runs --job-name validate_sales

# Get detailed logs for a specific job run
aws glue get-job-run --job-name validate_sales --run-id JOB_RUN_ID
```

Through the AWS Console:
- Go to AWS Glue > Jobs
- Select each job to see its run history
- Click on a specific run to see detailed logs and metrics

## 3. Examine the Processed Data

Verify data has moved through each stage of the pipeline:

```bash
# Check validated data
aws s3 ls s3://retail-etl-processed-TIMESTAMP/sales/validated/ --recursive

# Check transformed data
aws s3 ls s3://retail-etl-processed-TIMESTAMP/sales/transformed/ --recursive

# Check analytics outputs
aws s3 ls s3://retail-etl-analytics-TIMESTAMP/ --recursive
```

## 4. Verify Data Quality

Check if any errors were detected and routed to the error location:

```bash
# Look for invalid records
aws s3 ls s3://retail-etl-raw-TIMESTAMP/errors/sales/ --recursive
```

## 5. Query the Results

Use Athena to query the processed data:

```bash
# First, make sure your Glue Data Catalog is updated
aws glue start-crawler --name retail-etl-reference-crawler

# Wait for crawler to complete
aws glue get-crawler --name retail-etl-reference-crawler
```

Then in the AWS Console:
- Go to Amazon Athena
- Select the retail_etl database
- Run sample queries against your tables
- Example: `SELECT * FROM "retail_etl"."daily_sales" LIMIT 10;`

## 6. Check CloudWatch Logs

Examine detailed logs for each job:

```bash
# Get the log group name (typically /aws-glue/jobs/output)
aws logs describe-log-groups --log-group-name-prefix /aws-glue/jobs

# Get log streams for a specific job
aws logs describe-log-streams \
  --log-group-name /aws-glue/jobs/output \
  --log-stream-name-prefix validate_sales
```

Through the Console:
- Go to CloudWatch > Log Groups
- Select the /aws-glue/jobs/output log group
- Browse log streams for your job runs

## 7. Check SNS Notifications

If there were any errors, check for SNS notifications:

```bash
# List topics to confirm the ARN
aws sns list-topics

# List subscriptions to the topic
aws sns list-subscriptions-by-topic --topic-arn TOPIC_ARN
```

## 8. Visualize the Pipeline

For a more visual verification:
- Go to the AWS Glue Studio console
- Select "Monitoring" from the left navigation
- View the job run statistics and performance metrics

## Next Steps

Once you've verified everything is working correctly, you can:

1. **Add more data** - Upload additional sales data to test incremental processing
2. **Modify scripts** - Add more complex transformations or analytics
3. **Extend the pipeline** - Add more data sources or downstream consumers
4. **Schedule regular runs** - Set up EventBridge rules to trigger the workflow daily


## Troubleshooting

### Common Issues

1. **IAM Permission Errors**
   - Ensure the IAM role has appropriate permissions
   - Check for resource policy restrictions on S3 buckets
   - Verify the trust relationship for cross-account access

2. **Glue Job Failures**
   - Review CloudWatch logs for detailed error messages
   - Check for schema mismatches between datasets
   - Verify that referenced tables exist in the Glue Data Catalog

3. **Step Functions Errors**
   - Examine the execution details in the AWS console
   - Check the service roles and permissions
   - Review state input/output for format issues

## Additional Resources

- [AWS Glue Documentation](https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html)
- [AWS Step Functions Documentation](https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html)
- [Error Handling in AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/invocation-retries.html)
- [AWS Best Practices for Data Lakes](https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/build-an-aws-glue-catalog-using-the-iac-approach-with-cdk.html)

---

**Note**: This example is for educational purposes and may require adjustments for production use. Always follow security best practices and optimize resources for your specific needs.