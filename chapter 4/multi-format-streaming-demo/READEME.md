# Multi-format Streaming Pipeline with AWS

This Jupyter notebook demonstrates a complete end-to-end AWS streaming pipeline that can process data in multiple formats (JSON, CSV, and binary). It's designed as a hands-on companion to the book chapter on multi-format streaming data processing.

## Prerequisites

To run this notebook, you'll need:

1. **AWS Account**: An AWS account with permissions to create and manage the following services:
   - Amazon Kinesis Data Streams
   - AWS Lambda
   - Amazon S3
   - IAM Roles and Policies
   - Amazon CloudWatch

2. **AWS Credentials**: Configured in one of the following ways:
   - AWS CLI (`aws configure`)
   - Environment variables
   - IAM role (if running in SageMaker or EC2)

3. **Python Packages**:
   - boto3
   - pandas
   - matplotlib
   - seaborn

## What This Notebook Demonstrates

1. **Creating AWS Infrastructure:**
   - Setting up a Kinesis Data Stream
   - Creating an S3 bucket for processed data
   - Deploying a Lambda function with the necessary IAM permissions

2. **Generating and Sending Multi-format Data:**
   - JSON data (structured, human-readable)
   - CSV data (row-based text format)
   - Binary data (compact, efficient binary encoding)

3. **Processing Streaming Data:**
   - Automatic format detection
   - Format-specific processing
   - Standardized output generation

4. **Monitoring and Visualization:**
   - Checking CloudWatch metrics
   - Retrieving and displaying processed results
   - Visualizing data across different formats

## Important Notes

- **Resource Naming**: The notebook generates unique names for all AWS resources to avoid conflicts.
- **Costs**: While the resources created are minimal, they may incur AWS charges if left running. Use the cleanup function provided at the end of the notebook.
- **Permissions**: Ensure your AWS credentials have sufficient permissions to create and manage the required resources.
- **Region**: By default, the notebook uses the 'us-east-1' region. You can modify this as needed in the first code cell.

## Running the Notebook

1. Install required packages:
   ```
   pip install boto3 pandas matplotlib seaborn
   ```

2. Start Jupyter:
   ```
   jupyter notebook
   ```

3. Open this notebook and run each cell in sequence

4. After completing the demonstration, run the cleanup cell to remove all AWS resources

## Troubleshooting

- **Lambda Function Errors**: Check CloudWatch Logs in the AWS Console
- **Permission Issues**: Verify your AWS credentials have the necessary permissions
- **Resource Already Exists**: If you encounter name conflicts, modify the unique ID generation in the first code cell

## Extending the Example

This notebook provides a foundation you can extend in several ways:

- Add support for additional data formats (XML, Avro, Parquet)
- Implement schema validation using AWS Glue Schema Registry
- Add real-time dashboarding with Amazon QuickSight
- Set up automated alerts based on data content

## License

This code is provided under the MIT License. See the LICENSE file for details.
