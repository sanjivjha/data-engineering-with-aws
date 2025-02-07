from aws_cdk import (
    Stack,
    aws_cloudwatch as cloudwatch,
    aws_sns as sns,
    aws_s3 as s3,
    aws_cloudwatch_actions as cw_actions,
    Duration
)
from constructs import Construct

class MonitoringStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, raw_bucket: s3.Bucket, 
                 trusted_bucket: s3.Bucket, curated_bucket: s3.Bucket, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        alert_topic = sns.Topic(self, "DataLakeAlerts")
        dashboard = cloudwatch.Dashboard(self, "DataLakeDashboard",
            dashboard_name="RetailDataLakeMetrics"
        )

        # Storage metrics for all zones
        def create_bucket_metrics(bucket: s3.Bucket, zone_name: str):
            return [
                cloudwatch.Metric(
                    namespace="AWS/S3",
                    metric_name="BucketSizeBytes",
                    dimensions_map={
                        "BucketName": bucket.bucket_name,
                        "StorageType": "StandardStorage"
                    },
                    period=Duration.hours(6)
                ),
                cloudwatch.Metric(
                    namespace="AWS/S3",
                    metric_name="NumberOfObjects",
                    dimensions_map={
                        "BucketName": bucket.bucket_name
                    },
                    period=Duration.hours(6)
                )
            ]

        for bucket, name in [(raw_bucket, "Raw"), (trusted_bucket, "Trusted"), 
                           (curated_bucket, "Curated")]:
            dashboard.add_widgets(
                cloudwatch.GraphWidget(
                    title=f"{name} Zone Metrics",
                    left=create_bucket_metrics(bucket, name)
                )
            )

            storage_alarm = cloudwatch.Alarm(self, f"{name}StorageGrowthAlarm",
                metric=create_bucket_metrics(bucket, name)[0],
                threshold=5_000_000_000,  # 5GB
                evaluation_periods=1,
                alarm_description=f"Alert when {name} zone storage exceeds 5GB"
            )
            storage_alarm.add_alarm_action(cw_actions.SnsAction(alert_topic))

        # Crawler metrics
        crawler_names = ["raw-zone-crawler", "trusted-zone-crawler", "curated-zone-crawler"]
        
        for crawler_name in crawler_names:
            failure_metric = cloudwatch.Metric(
                namespace="AWS/Glue",
                metric_name="glue.driver.aggregate.numFailedTasks",
                dimensions_map={
                    "JobName": crawler_name
                }
            )

            crawler_alarm = cloudwatch.Alarm(self, f"{crawler_name}-failure-alarm",
                metric=failure_metric,
                threshold=1,
                evaluation_periods=1,
                alarm_description=f"Alert on {crawler_name} failures"
            )
            crawler_alarm.add_alarm_action(cw_actions.SnsAction(alert_topic))