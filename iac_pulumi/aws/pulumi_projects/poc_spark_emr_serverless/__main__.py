"""An AWS Python Pulumi program"""
import json
import pulumi
import pulumi_aws as aws

config = pulumi.Config()
stack_name = pulumi.get_stack()
region = config.require("region")
resource_prefix_name = f"poc-spark-emr-serverless-{stack_name}"
base_tags = {
    "environment": stack_name,
}

# S3 bucket
bucket = aws.s3.Bucket(
    f"{resource_prefix_name}-bucket",
    acl="private",
    versioning=aws.s3.BucketVersioningArgs(enabled=True,),
    tags=base_tags,
    force_destroy=True  # To be able to delete a not empty bucket
)

# IAM Role:
# - To allow jobs submitted to the Amazon EMR Serverless application to access other AWS services on our behalf
# - Required for the EMR Studio
iam_role = aws.iam.Role(
    f"{resource_prefix_name}-role",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "emr-serverless.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                },
            ],
        },
    ),
    tags=base_tags,
)

bucket_arn = bucket.arn.apply(lambda arn: arn)


def get_access_role_policy_details(bucket_arn):
    return {
        "Version": "2012-10-17",
        "Statement": [
            # S3 related permissions
            {
                "Sid": "ReadAccessForEMRSamples",
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:ListBucket"],
                "Resource": [
                    "arn:aws:s3:::*.elasticmapreduce",
                    "arn:aws:s3:::*.elasticmapreduce/*",
                    # S3 bucket for code example
                    "arn:aws:s3:::noaa-gsod-pds",
                    "arn:aws:s3:::noaa-gsod-pds/*",
                ],
            },

            {
                "Sid": "FullAccessToOutputBucket",
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject",
                    "s3:GetObject",
                    "s3:ListBucket",
                    "s3:DeleteObject",
                ],
                "Resource": [bucket_arn, f"{bucket_arn}/*"],
            },
        ],
    }


iam_role_policy = aws.iam.RolePolicy(
    f"{resource_prefix_name}-role-policy",
    role=iam_role.id,
    # Need to define a function to pass the bucket.arn - Otherwise an Output is not JSON serializable
    policy=bucket.arn.apply(get_access_role_policy_details),
)

# EMR Serverless App
poc_spark_emr_serverless_dev_emr_studio = aws.emrserverless.Application(
    f"{resource_prefix_name}-emr-serverless-app",
    initial_capacities=None,  # Not keeping warm instances to limit computational costs
    maximum_capacity=aws.emrserverless.ApplicationMaximumCapacityArgs(
        cpu="4 vCPU",
        memory="12 GB",
        disk="80 GB",
    ),
    auto_start_configuration=aws.emrserverless.ApplicationAutoStartConfigurationArgs(
        enabled=True
    ),
    auto_stop_configuration=aws.emrserverless.ApplicationAutoStopConfigurationArgs(
        enabled=True,
        idle_timeout_minutes=5,
    ),
    release_label="emr-6.8.0",
    tags=base_tags,
    type="spark",
)
