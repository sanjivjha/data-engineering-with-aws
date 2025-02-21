# Retail Data Lake with AWS CDK

This repository contains an implementation of a production-ready data lake using AWS CDK with Python. The architecture implements a secure, scalable, and well-monitored data lake suitable for retail analytics workloads.

## Architecture Overview

The data lake follows a three-zone architecture:
- **Raw Zone**: Initial landing zone for raw data
- **Trusted Zone**: Validated and cleansed data
- **Curated Zone**: Business-ready datasets

Key Features:
- 🔒 End-to-end encryption using KMS
- 📊 Automated data cataloging with AWS Glue
- 📈 Built-in monitoring and alerting
- 🔄 Lifecycle management for cost optimization
- ✅ Comprehensive testing utilities

## Prerequisites

- AWS Account and configured AWS CLI
- Python 3.8+
- AWS CDK CLI
- Node.js 14+ (for CDK)

## Project Structure

```
retail-data-lake-python/
├── retail_data_lake/              
│   ├── __init__.py
│   ├── data_lake_stack.py        # Core storage infrastructure
│   ├── catalog_stack.py          # Data cataloging configuration
│   └── monitoring_stack.py       # Monitoring and alerting setup
├── scripts/
│   └── generate_test_data.py     # Test data generation utility
├── tests/                        # Unit tests directory
├── app.py                        # Main CDK app file
├── cdk.json                      # CDK configuration
└── requirements.txt              # Python dependencies
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/sanjivjha/data-engineering-with-aws.git
cd chapter\ 2/building_scalable_datalake/retail-data-lake-python
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Deployment

1. Bootstrap CDK (first-time only):
```bash
cdk bootstrap
```

2. Deploy all stacks:
```bash
cdk deploy --all
```

This will deploy:
- Storage infrastructure (S3 buckets with encryption)
- Data catalog (Glue database and crawlers)
- Monitoring dashboard and alerts

## Testing the Setup

1. Generate sample data:
```bash
python scripts/generate_test_data.py
```

2. Verify data in AWS Console:
   - Check S3 buckets for uploaded data
   - Review Glue crawlers and database
   - Examine CloudWatch dashboard

3. Run sample queries in Athena:
```sql
-- Sample query for transaction analysis
SELECT 
    year,
    month,
    COUNT(*) as transaction_count,
    ROUND(AVG(amount), 2) as avg_amount
FROM transactions
GROUP BY year, month
ORDER BY year, month;
```

## Component Details

### Data Lake Stack
- Creates three S3 buckets for different data zones
- Implements KMS encryption
- Configures versioning and lifecycle rules
- Prevents accidental deletion

### Catalog Stack
- Sets up Glue Data Catalog database
- Configures crawlers for automated schema discovery
- Manages IAM roles and permissions
- Schedules regular data discovery

### Monitoring Stack
- Creates CloudWatch dashboard
- Sets up metric collection
- Configures SNS alerts
- Monitors storage usage and data processing

## Cost Management

The implementation includes several cost optimization features:
- Intelligent-Tiering storage class for older data
- Scheduled Glue crawlers (every 6 hours by default)
- Lifecycle rules for cost-effective data management

## Cleanup

To avoid unnecessary AWS charges, clean up resources when done:

1. Empty S3 buckets:
```bash
python scripts/cleanup_resources.py
```

2. Destroy CDK stacks:
```bash
cdk destroy --all
```

## Security Features

- KMS encryption for all data zones
- Versioning enabled for data protection
- IAM roles with minimal required permissions
- Bucket policies preventing public access
- Encrypted SNS topics for alerts

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Sanjiv Jha

## Acknowledgments

This project is part of the "Data Engineering with AWS" book examples.
