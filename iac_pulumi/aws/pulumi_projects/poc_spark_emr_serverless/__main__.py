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
# IAM User
user = aws.iam.User(f"{resource_prefix_name}-user", tags=base_tags)
user_policy = aws.iam.UserPolicy(
    f"{resource_prefix_name}-policy",
    user=user.name,
    # TODO - limit policies
    policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "EMRStudioCreate",
                    "Effect": "Allow",
                    "Action": [
                        "elasticmapreduce:CreateStudioPresignedUrl",
                        "elasticmapreduce:DescribeStudio",
                        "elasticmapreduce:CreateStudio",
                        "elasticmapreduce:ListStudios",
                    ],
                    "Resource": "*",
                },
                {
                    "Sid": "EMRServerlessFullAccess",
                    "Effect": "Allow",
                    "Action": ["emr-serverless:*"],
                    "Resource": "*",
                },
                {
                    "Sid": "AllowEC2ENICreationWithEMRTags",
                    "Effect": "Allow",
                    "Action": ["ec2:CreateNetworkInterface"],
                    "Resource": ["arn:aws:ec2:*:*:network-interface/*"],
                    "Condition": {
                        "StringEquals": {
                            "aws:CalledViaLast": "ops.emr-serverless.amazonaws.com"
                        }
                    },
                },
                {
                    "Sid": "AllowEMRServerlessServiceLinkedRoleCreation",
                    "Effect": "Allow",
                    "Action": "iam:CreateServiceLinkedRole",
                    "Resource": "arn:aws:iam::*:role/aws-service-role/*",
                },
            ],
        }
    ),
)

# S3 bucket
bucket = aws.s3.Bucket(
    f"{resource_prefix_name}-bucket",
    acl="private",
    versioning=aws.s3.BucketVersioningArgs(enabled=True,),
    tags=base_tags,
)

# IAM Role to allow jobs submitted to the Amazon EMR Serverless application to access other AWS services on our behalf
access_role = aws.iam.Role(
    f"{resource_prefix_name}-access-role",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "emr-serverless.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }
    ),
    tags=base_tags,
)

bucket_arn = bucket.arn.apply(lambda arn: arn)


def get_access_role_policy_details(bucket_arn):
    return {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "ReadAccessForEMRSamples",
                    "Effect": "Allow",
                    "Action": ["s3:GetObject", "s3:ListBucket"],
                    "Resource": [
                        "arn:aws:s3:::*.elasticmapreduce",
                        "arn:aws:s3:::*.elasticmapreduce/*",
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
                    "Resource": [
                        bucket_arn,
                        f"{bucket_arn}/*",
                    ],
                },
                {
                    "Sid": "GlueCreateAndReadDataCatalog",
                    "Effect": "Allow",
                    "Action": [
                        "glue:GetDatabase",
                        "glue:CreateDatabase",
                        "glue:GetDataBases",
                        "glue:CreateTable",
                        "glue:GetTable",
                        "glue:UpdateTable",
                        "glue:DeleteTable",
                        "glue:GetTables",
                        "glue:GetPartition",
                        "glue:GetPartitions",
                        "glue:CreatePartition",
                        "glue:BatchCreatePartition",
                        "glue:GetUserDefinedFunctions",
                    ],
                    "Resource": ["*"],
                },
            ],
        }


access_role_policy = aws.iam.RolePolicy(
    "testPolicy",
    role=access_role.id,
    # Need to define a function to pass the bucket.arn - Otherwise an Output is not JSON serializable
    policy=bucket.arn.apply(get_access_role_policy_details),
)
