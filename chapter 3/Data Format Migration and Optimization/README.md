**Overview**

This repository contains a complete implementation of the data format migration and optimization concepts discussed in Chapter 3 of "Modern Data Engineering on AWS". The code demonstrates practical techniques for migrating data between formats, optimizing storage, and measuring performance improvements.
**Project Structure **
retail-format-migration/
├── notebooks/
│   └── format_migration_demo.ipynb    # Main implementation notebook
├── src/
│   └── utils.py                       # Helper functions
├── config/
│   └── config.yaml                    # Configuration parameters
├── requirements.txt
└── README.md

**Features**

Generate realistic retail transaction and customer data
Analyze storage patterns and performance metrics
Migrate data between formats (CSV/JSON → Parquet/Delta)
Implement optimized partitioning strategies
Benchmark performance improvements
Visualize optimization results

**Requirements**

Python 3.8+
AWS Account with S3 access
Spark 3.2+ (for Delta Lake operations)

**Installation**

Clone the repository:
  git clone https://github.com/data-engineering-book/retail-format-migration
  cd retail-format-migration
Create a virtual environment:
  python -m venv .venv
  source .venv/bin/activate  # On Windows: .venv\Scripts\activate
Install dependencies:
  pip install -r requirements.txt
Configure AWS credentials:
  Create a .env file with:
  AWS_ACCESS_KEY_ID=your_key_here
  AWS_SECRET_ACCESS_KEY=your_secret_here
  AWS_DEFAULT_REGION=your_region

**Usage**
Launch Jupyter Notebook:
  jupyter notebook notebooks/format_migration_demo.ipynb

Follow the step-by-step instructions in the notebook to:

  Generate sample data
  Analyze initial storage metrics
  Perform format migration
  Benchmark performance
  Visualize results

**Performance Expectations**
When running this demo, you can expect to see:

30-40% reduction in storage requirements
40-60% improvement in query performance
Clear visualization of optimization benefits

**Troubleshooting**

Permission errors: Ensure your AWS credentials have proper S3 access
Memory issues: Reduce data generation volume in config.yaml
Delta Lake errors: Verify Spark is configured with Delta Lake support

**License**
MIT License
