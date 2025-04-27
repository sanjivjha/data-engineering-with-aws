# AWS Data Governance and Security Workshop

This repository contains the code and materials for the AWS Data Governance and Security Workshop - a comprehensive guide for implementing enterprise-grade security for data lakes on AWS.

## Overview

In this workshop, you'll implement a complete security framework for your data lake using AWS Lake Formation, IAM roles, column-level security, LF-Tags, and comprehensive audit capabilities.

By the end of the workshop, you'll have built:

- A secure data lake foundation with encryption and proper access controls
- Column-level security with persona-based access patterns
- Tag-based governance for scalable security
- Comprehensive audit logging and monitoring
- Visualizations of security controls

## Prerequisites

- An AWS account with the required permissions
- Python 3.7 or later
- Required Python packages: boto3, pandas, matplotlib, numpy
- Jupyter Notebook environment (local or SageMaker)
- AWS credentials configured for your environment

## Getting Started

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/aws-data-governance-workshop.git
   ```

2. Navigate to the repository directory:
   ```
   cd aws-data-governance-workshop
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Launch Jupyter Notebook:
   ```
   jupyter notebook
   ```

5. Open the `Data_Governance_Security_Workshop.ipynb` notebook and follow the instructions.

## Workshop Modules

The workshop is divided into the following modules:

1. **Setting Up the Data Lake Foundation**
   - Creating an encrypted S3 bucket
   - Registering with Lake Formation
   - Creating domain-specific databases

2. **Creating Sample Tables with Sensitive Data**
   - Setting up tables with various sensitivity levels
   - Generating and uploading sample data

3. **Implementing Persona-Based Security**
   - Creating IAM roles for different user personas
   - Applying column-level security with Lake Formation

4. **Setting Up LF-Tags for Scalable Governance**
   - Creating and assigning LF-Tags
   - Implementing tag-based access controls

5. **Setting Up Audit and Monitoring**
   - Configuring CloudTrail for comprehensive logging
   - Creating CloudWatch metrics and dashboards
   - Setting up alerts for sensitive data access

6. **Testing and Verification**
   - Validating security controls
   - Visualizing column-level access patterns

## Architecture Diagram

The security architecture implemented in this workshop:

```
┌────────────────┐     ┌─────────────────┐     ┌────────────────┐
│                │     │                 │     │                │
│  IAM Personas  │     │ Lake Formation  │     │  CloudTrail    │
│                │◄────┤  Permissions    │────►│   Logging      │
└────────────────┘     │                 │     │                │
                       └────────┬────────┘     └────────────────┘
                                │
                                ▼
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│                │     │                │     │                │
│   LF-Tags      │────►│   Data Lake    │────►│  CloudWatch    │
│                │     │   (S3)         │     │   Monitoring   │
└────────────────┘     │                │     │                │
                       └────────────────┘     └────────────────┘
```

## Cleaning Up

After completing the workshop, make sure to clean up the AWS resources to avoid unnecessary charges. The notebook includes a cleanup function that you can run with:

```python
clean_up_resources(confirm=True)
```

## Additional Resources

- [AWS Lake Formation Documentation](https://docs.aws.amazon.com/lake-formation/)
- [AWS Identity and Access Management Documentation](https://docs.aws.amazon.com/iam/)
- [AWS CloudTrail Documentation](https://docs.aws.amazon.com/cloudtrail/)
- [AWS CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)

## License

This workshop is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

This workshop was created by Sanjiv Kumar Jha as part of the book "Data Engineering with AWS: Architecting Scalable, Secure, and Cost-Effective Data Platforms for the Modern Enterprise."

## Acknowledgements

Special thanks to AWS for providing the services and documentation that make this workshop possible.