# Data Quality Pipeline with AWS CDK

This repository contains a Jupyter notebook implementation of a serverless data quality pipeline using AWS CDK with Python. The implementation is part of the examples for Chapter 6 (Data Transformation and Quality) of the book "Data Engineering with AWS".

## Overview

The serverless data quality pipeline automatically validates data files as they arrive in S3, separates valid and invalid records, publishes quality metrics to CloudWatch, and sends alerts when quality thresholds aren't met.

![Pipeline Architecture](images/quality-pipeline-architecture.png)

Key components:
- S3 buckets for raw and validated data
- Lambda function for serverless validation
- CloudWatch for metrics, dashboards, and alerting
- SNS for notifications

## Prerequisites

To run the notebook, you'll need:

- AWS account with appropriate permissions
- Python 3.7 or later
- Jupyter notebook environment
- AWS CLI configured with credentials
- Node.js and npm (for AWS CDK)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/sanjivjha/data-engineering-with-aws.git
   cd data-engineering-with-aws/chapter6
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   npm install -g aws-cdk
   ```

4. Start Jupyter and open the notebook:
   ```bash
   jupyter notebook data_quality_pipeline.ipynb
   ```

## Notebook Contents

The notebook walks through the implementation of a data quality pipeline using a cell-by-cell approach:

1. **Setup and Configuration**: Install required packages and configure AWS environment
2. **Define Infrastructure**: Create AWS CDK app defining all resources
3. **Deploy Resources**: Deploy the stack to your AWS account
4. **Generate Sample Data**: Create and upload test data with intentional quality issues
5. **Monitor Processing**: Check Lambda logs and validation results
6. **Visualize Metrics**: Create charts from CloudWatch metrics
7. **Clean Up Resources**: Optional cleanup when you're done experimenting

## Implementation Details

### Data Validation Logic

The Lambda function checks transactions for several quality issues:
- Missing required fields (customer_id)
- Invalid values (negative amounts)
- Format errors (invalid timestamps)
- Domain constraint violations (invalid payment methods)

Valid records are saved to a dedicated path, while invalid records are saved with error annotations for further analysis.

### Quality Metrics

The pipeline publishes several metrics to CloudWatch:
- Overall quality score
- Percentage of valid records
- Error percentages by type

These metrics are visualized in both the notebook and a CloudWatch dashboard.

### Alerting

When the quality score drops below a configurable threshold (default: 85), the system triggers a CloudWatch alarm that publishes to an SNS topic. This can be connected to email, SMS, or other notification channels.

## Extending the Pipeline

You can extend this implementation in several ways:

1. **Add data transformations**: Modify the Lambda function to apply transformations to valid records
2. **Implement schema evolution**: Use AWS Glue Schema Registry to manage schema changes
3. **Add machine learning**: Connect to SageMaker for anomaly detection in quality metrics
4. **Enhance visualization**: Create QuickSight dashboards for business users
5. **Implement remediation**: Add automated workflow for fixing common issues

## Cleanup

To avoid ongoing charges, run the cleanup cell in the notebook or use the AWS CDK CLI:

```bash
cdk destroy --force
```

## Further Reading

- [AWS CDK Developer Guide](https://docs.aws.amazon.com/cdk/latest/guide/home.html)
- [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
- [CloudWatch User Guide](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.