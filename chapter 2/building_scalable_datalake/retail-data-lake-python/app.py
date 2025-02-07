#!/usr/bin/env python3
from aws_cdk import App
from retail_data_lake_python.datalake_stack import DataLakeStack
from retail_data_lake_python.monitoring_stack import MonitoringStack
from retail_data_lake_python.catalogue_stack import CatalogStack

app = App()

data_lake = DataLakeStack(app, "RetailDataLakeStack")

CatalogStack(app, "RetailDataLakeCatalog", 
    raw_bucket=data_lake.raw_bucket,
    trusted_bucket=data_lake.trusted_bucket,
    curated_bucket=data_lake.curated_bucket
)

MonitoringStack(app, "RetailDataLakeMonitoring", 
    raw_bucket=data_lake.raw_bucket,
    trusted_bucket=data_lake.trusted_bucket,
    curated_bucket=data_lake.curated_bucket
)

app.synth()