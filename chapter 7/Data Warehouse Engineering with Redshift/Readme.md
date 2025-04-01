# Amazon Redshift Data Warehouse Workshop

This repository contains a Jupyter notebook for a hands-on workshop on building a data warehouse using Amazon Redshift. The workshop guides you through creating, configuring, and using an Amazon Redshift cluster for data warehousing in a step-by-step manner.

## Overview

Amazon Redshift is a fully managed, petabyte-scale data warehouse service that makes it simple and cost-effective to analyze all your data using standard SQL and your existing business intelligence tools. This workshop provides a practical introduction to Redshift's core capabilities, from deployment to optimization and querying.

## Workshop Contents

The Jupyter notebook in this repository covers:

1. **Environment Setup**: Importing required libraries and setting configuration parameters
2. **Resource Creation**: 
   - Creating IAM roles for Redshift to access S3
   - Setting up S3 buckets with sample e-commerce data
   - Deploying a Redshift cluster
3. **Database Setup**: 
   - Creating optimized tables with appropriate distribution and sort keys
   - Loading data from S3 using the COPY command
4. **Running Analytics**: 
   - Creating materialized views to improve query performance
   - Running analytical queries on the e-commerce dataset
5. **Performance Analysis**: 
   - Comparing query performance with and without materialized views
   - Examining execution plans and table design
6. **Cleanup**: Properly removing all AWS resources to avoid unnecessary charges

## Prerequisites

To run this workshop, you'll need:

- An AWS account with appropriate permissions to create resources
- Python 3.8+ installed on your machine
- The following Python packages:
  - boto3
  - pandas
  - psycopg2 or psycopg2-binary
- Jupyter Notebook or JupyterLab

## Getting Started

1. Clone this repository:
   ```
   git clone <repository-url>
   cd redshift-data-warehouse-workshop
   ```

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Open the Jupyter notebook:
   ```
   jupyter notebook redshift_workshop.ipynb
   ```

4. Follow the step-by-step instructions in the notebook, executing each cell sequentially.

## Workshop Architecture

The workshop implements a simple e-commerce data warehouse with the following components:

- **Dimension tables**:
  - `customers`: Customer information
  - `products`: Product catalog
  
- **Fact table**:
  - `sales`: Transaction records linking customers and products

Each table is designed with appropriate distribution and sort keys to optimize query performance in Redshift's distributed computing environment.

## Key Concepts Covered

- Redshift cluster architecture and configuration
- Table design principles (distribution styles, sort keys)
- Data loading best practices with the COPY command
- Query optimization using materialized views
- Analyzing query execution plans
- Performance tuning techniques
- Cost management and resource cleanup

## Cost Considerations

This workshop uses AWS resources that will incur charges. The estimated cost for running the complete workshop is approximately $2-5 if you follow the cleanup instructions immediately after completion. Key resources that incur charges:

- Redshift cluster (dc2.large nodes)
- S3 storage (minimal cost)

The cleanup section at the end of the notebook provides instructions for removing all resources to avoid ongoing charges.

## Security Considerations

The workshop creates a publicly accessible Redshift cluster for demonstration purposes. In a production environment, you would typically:

- Place Redshift in a private subnet
- Use VPC security groups to restrict access
- Implement column-level access controls
- Enable encryption at rest and in transit

## Extending the Workshop

After completing the basic workshop, consider these extensions to further your learning:

1. Implement Redshift Spectrum to query data directly in S3
2. Set up Zero-ETL integration with Aurora PostgreSQL
3. Configure workload management for different user groups
4. Create dashboards using Amazon QuickSight connected to Redshift
5. Design a comprehensive disaster recovery strategy

## Related Resources

- [Amazon Redshift Documentation](https://docs.aws.amazon.com/redshift/)
- [AWS Database Blog - Redshift Best Practices](https://aws.amazon.com/blogs/database/category/database/amazon-redshift/)
- [Redshift Engineering Blog](https://aws.amazon.com/blogs/big-data/tag/amazon-redshift/)
- [AWS Well-Architected Framework: Data Warehouse Lens](https://aws.amazon.com/architecture/analytics-lens/)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

This workshop is based on Chapter 7 of "Data Engineering with AWS" and has been designed to provide a hands-on introduction to Redshift data warehousing concepts.