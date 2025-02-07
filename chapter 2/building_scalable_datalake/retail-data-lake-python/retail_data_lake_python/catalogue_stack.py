from aws_cdk import (
    Stack,
    aws_glue as glue,
    aws_iam as iam,
    aws_s3 as s3
)
from constructs import Construct

class CatalogStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, 
                 raw_bucket: s3.Bucket, 
                 trusted_bucket: s3.Bucket, 
                 curated_bucket: s3.Bucket, 
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        database = glue.CfnDatabase(self, "RetailDataLakeDB",
            catalog_id=self.account,
            database_input=glue.CfnDatabase.DatabaseInputProperty(
                name="retail_analytics",
                description="Retail data lake catalog database"
            )
        )

        crawler_role = iam.Role(self, "GlueCrawlerRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSGlueServiceRole"
                )
            ]
        )

        # Grant permissions for all buckets
        raw_bucket.grant_read(crawler_role)
        trusted_bucket.grant_read(crawler_role)
        curated_bucket.grant_read(crawler_role)

        crawlers = {
            "raw": (raw_bucket, "transactions"),
            "trusted": (trusted_bucket, "transactions"),
            "curated": (curated_bucket, "analytics")
        }

        for zone, (bucket, prefix) in crawlers.items():
            glue.CfnCrawler(self, f"{zone.capitalize()}ZoneCrawler",
                name=f"{zone}-zone-crawler",
                role=crawler_role.role_arn,
                database_name=database.ref,
                targets=glue.CfnCrawler.TargetsProperty(
                    s3_targets=[glue.CfnCrawler.S3TargetProperty(
                        path=f"s3://{bucket.bucket_name}/{prefix}/"
                    )]
                ),
                schedule=glue.CfnCrawler.ScheduleProperty(
                    schedule_expression="cron(0 0/6 * * ? *)"
                ),
                schema_change_policy=glue.CfnCrawler.SchemaChangePolicyProperty(
                    update_behavior="UPDATE_IN_DATABASE",
                    delete_behavior="LOG"
                )
            )