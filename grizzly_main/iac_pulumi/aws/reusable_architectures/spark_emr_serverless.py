import json
from typing import Any, Dict, List, Tuple

import pulumi
import pulumi_aws as aws


def create_s3_bucket(
    resource_prefix_name: str,
    is_bucket_encryption: bool,
    tags: Dict[str, Any] = None,
) -> aws.s3.Bucket:
    """
    Create a s3 bucket
    :param resource_prefix_name: Resource prefix name
    :param tags: Common tags for the infrastructure resources
    :param is_bucket_encryption: True if using s3 bucket server side encryption, False otherwise.
    :return: s3 bucket
    """
    s3_bucket = aws.s3.Bucket(
        f"{resource_prefix_name}-bucket",
        acl="private",
        versioning=aws.s3.BucketVersioningArgs(
            enabled=True,
        ),
        tags=tags,
        force_destroy=True,  # To be able to delete a not empty bucket
    )
    if is_bucket_encryption:
        aws.s3.BucketServerSideEncryptionConfigurationV2(
            f"{resource_prefix_name}-bucket_encryption",
            bucket=s3_bucket.bucket,
            rules=[
                aws.s3.BucketServerSideEncryptionConfigurationV2RuleArgs(
                    apply_server_side_encryption_by_default=aws.s3.BucketServerSideEncryptionConfigurationV2RuleApplyServerSideEncryptionByDefaultArgs(
                        sse_algorithm="AES256",
                    ),
                )
            ],
        )
    return s3_bucket


def create_iam_role(
    resource_prefix_name: str,
    tags: Dict[str, Any] = None,
) -> aws.iam.Role:
    """
    Create IAM role to allow jobs submitted to the Amazon EMR Serverless application to access other AWS services
    on our behalf
    :param resource_prefix_name: Resource prefix name
    :param tags: Common tags for the infrastructure resources
    :return: IAM role
    """
    return aws.iam.Role(
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
        tags=tags,
    )


def get_access_role_policy_details(
    s3_bucket_arn: aws.s3.Bucket.arn, additional_read_access_resources: List[str] = None
) -> Dict[str, Any]:
    """
    Get access IAM role policy details
    :param s3_bucket_arn: S3 bucket
    :param additional_read_access_resources: Additional read access resources (e.g. to access public s3 buckets)
    :return: IAM role policy details
    """
    if additional_read_access_resources is None:
        additional_read_access_resources = []
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
                ]
                + additional_read_access_resources,
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
                "Resource": [s3_bucket_arn, f"{s3_bucket_arn}/*"],
            },
        ],
    }


def create_iam_role_policy(
    resource_prefix_name: str,
    s3_bucket: aws.s3.Bucket,
    iam_role: aws.iam.Role,
    additional_read_access_resources: List[str] = None,
) -> aws.iam.RolePolicy:
    """
    Create IAM Role Policy
    :param resource_prefix_name: Resource prefix name
    :param s3_bucket: S3 bucket
    :param iam_role: IAM Role
    :param additional_read_access_resources: Additional read access resources
    :return: IAM Role Policy
    """
    s3_bucket_arn = s3_bucket.arn.apply(lambda arn: arn)
    return aws.iam.RolePolicy(
        f"{resource_prefix_name}-role-policy",
        role=iam_role.id,
        # Note: Need to define the get_access_role_policy_details function to pass the bucket.arn. Otherwise an Output
        # is not JSON serializable
        policy=pulumi.Output.all(s3_bucket_arn, additional_read_access_resources).apply(
            lambda args: get_access_role_policy_details(
                s3_bucket_arn=args[0], additional_read_access_resources=args[1]
            )
        ),
    )


def create_emr_serverless_app(
    resource_prefix_name: str,
    max_vcpu: int,
    max_memory_gb: int,
    max_disk_gb: int,
    idle_timeout_minutes: int = 60,
    tags: Dict[str, Any] = None,
) -> aws.emrserverless.Application:
    """
    Create EMR Serverless app
    :param resource_prefix_name: Resource prefix name
    :param max_vcpu: The maximum allowed vCPU for an application.
    :param max_memory_gb: The maximum allowed memory in GB for an application.
    :param max_disk_gb: The maximum allowed disk in GB for an application.
    :param idle_timeout_minutes: The amount of idle time in minutes after which your application will automatically stop
    :param tags: Common tags for the infrastructure resources
    :return: EMR Serverless app
    """
    return aws.emrserverless.Application(
        f"{resource_prefix_name}-emr-serverless-app",
        initial_capacities=None,  # Not keeping warm instances to limit computational costs
        maximum_capacity=aws.emrserverless.ApplicationMaximumCapacityArgs(
            cpu=f"{max_vcpu} vCPU",
            memory=f"{max_memory_gb} GB",
            disk=f"{max_disk_gb} GB",
        ),
        auto_start_configuration=aws.emrserverless.ApplicationAutoStartConfigurationArgs(
            enabled=True
        ),
        auto_stop_configuration=aws.emrserverless.ApplicationAutoStopConfigurationArgs(
            enabled=True,
            idle_timeout_minutes=idle_timeout_minutes,
        ),
        release_label="emr-6.8.0",
        tags=tags,
        type="spark",
    )


def create_spark_emr_serverless_architecture(
    resource_prefix_name: str,
    max_vcpu: int,
    max_memory_gb: int,
    max_disk_gb: int,
    idle_timeout_minutes: int = 60,
    additional_read_access_resources: List[str] = None,
    is_bucket_encryption: bool = True,
    tags: Dict[str, Any] = None,
) -> Tuple[
    aws.s3.Bucket, aws.iam.Role, aws.iam.RolePolicy, aws.emrserverless.Application
]:
    """
    Creates the following infrastructure is required to run Spark on AWS with EMR Serverless:
    - S3 bucket
    - IAM role
    - IAM role policy
    - EMR Serverless app
    Note that we can add any additional optional arguments in the future to further customize any resources parameters
    from this architecture.
    :param max_vcpu: The maximum allowed vCPU for an application.
    :param max_memory_gb: The maximum allowed memory in GB for an application.
    :param max_disk_gb: The maximum allowed disk in GB for an application.
    :param idle_timeout_minutes: The amount of idle time in minutes after which your application will automatically stop
    :param resource_prefix_name: Resource prefix name
    :param additional_read_access_resources: Additional read access resources
    :param is_bucket_encryption: True if using s3 bucket server side encryption, False otherwise.
    :param tags: Common tags for the infrastructure resources
    :return: Architecture infrastructure
    """
    s3_bucket = create_s3_bucket(
        resource_prefix_name=resource_prefix_name,
        is_bucket_encryption=is_bucket_encryption,
        tags=tags,
    )
    iam_role = create_iam_role(resource_prefix_name=resource_prefix_name, tags=tags)
    iam_role_policy = create_iam_role_policy(
        resource_prefix_name=resource_prefix_name,
        s3_bucket=s3_bucket,
        iam_role=iam_role,
        additional_read_access_resources=additional_read_access_resources,
    )
    emr_serverless_app = create_emr_serverless_app(
        resource_prefix_name=resource_prefix_name,
        max_vcpu=max_vcpu,
        max_memory_gb=max_memory_gb,
        max_disk_gb=max_disk_gb,
        idle_timeout_minutes=idle_timeout_minutes,
        tags=tags,
    )
    return s3_bucket, iam_role, iam_role_policy, emr_serverless_app
