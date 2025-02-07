from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_kms as kms,
    aws_iam as iam,
    aws_glue as glue,
    Duration,
    RemovalPolicy
)

from constructs import Construct

class DataLakeStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        encryption_key = kms.Key(self, "DataLakeKey",
            enable_key_rotation=True,
            alias="retail-data-lake-key"
        )

        bucket_config = {
            "encryption": s3.BucketEncryption.KMS,
            "encryption_key": encryption_key,
            "versioned": True,
            "removal_policy": RemovalPolicy.RETAIN
        }

        self.raw_bucket = s3.Bucket(self, "RawZone",
            **bucket_config,
            lifecycle_rules=[
                s3.LifecycleRule(
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.INTELLIGENT_TIERING,
                            transition_after=Duration.days(90)
                        )
                    ]
                )
            ]
        )

        self.trusted_bucket = s3.Bucket(self, "TrustedZone", **bucket_config)
        self.curated_bucket = s3.Bucket(self, "CuratedZone", **bucket_config)