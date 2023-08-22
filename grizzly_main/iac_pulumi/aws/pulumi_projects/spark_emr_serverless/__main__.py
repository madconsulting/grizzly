import pulumi

from grizzly_main.iac_pulumi.aws.reusable_architectures.spark_emr_serverless import (
    create_spark_emr_serverless_architecture,
)

config = pulumi.Config()
stack_name = pulumi.get_stack()
resource_prefix_name = config.name.replace("_", "-")

create_spark_emr_serverless_architecture(
    resource_prefix_name=f"{resource_prefix_name}-{stack_name}",
    max_vcpu=int(config.require("max_vcpu")),
    max_memory_gb=int(config.require("max_memory_gb")),
    max_disk_gb=int(config.require("max_disk_gb")),
    idle_timeout_minutes=int(config.require("idle_timeout_minutes")),
    additional_read_access_resources=[
        # S3 bucket for pySpark code example
        "arn:aws:s3:::noaa-gsod-pds",
        "arn:aws:s3:::noaa-gsod-pds/*",
    ],
    tags={
        "environment": stack_name,
    },
)
