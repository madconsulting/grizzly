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

# # IAM User -> NOT NEEDED # TODO - delete
# user = aws.iam.User(f"{resource_prefix_name}-user", tags=base_tags)
# user_policy = aws.iam.UserPolicy(
#     f"{resource_prefix_name}-policy",
#     user=user.name,
#     # TODO - limit policies
#     policy=json.dumps(
#         {
#             "Version": "2012-10-17",
#             "Statement": [
#                 {
#                     "Sid": "EMRStudioCreate",
#                     "Effect": "Allow",
#                     "Action": [
#                         "elasticmapreduce:CreateStudioPresignedUrl",
#                         "elasticmapreduce:DescribeStudio",
#                         "elasticmapreduce:CreateStudio",
#                         "elasticmapreduce:ListStudios",
#                     ],
#                     "Resource": "*",
#                 },
#                 {
#                     "Sid": "EMRServerlessFullAccess",
#                     "Effect": "Allow",
#                     "Action": ["emr-serverless:*"],
#                     "Resource": "*",
#                 },
#                 {
#                     "Sid": "AllowEC2ENICreationWithEMRTags",
#                     "Effect": "Allow",
#                     "Action": ["ec2:CreateNetworkInterface"],
#                     "Resource": ["arn:aws:ec2:*:*:network-interface/*"],
#                     "Condition": {
#                         "StringEquals": {
#                             "aws:CalledViaLast": "ops.emr-serverless.amazonaws.com"
#                         }
#                     },
#                 },
#                 {
#                     "Sid": "AllowEMRServerlessServiceLinkedRoleCreation",
#                     "Effect": "Allow",
#                     "Action": "iam:CreateServiceLinkedRole",
#                     "Resource": "arn:aws:iam::*:role/aws-service-role/*",
#                 },
#             ],
#         }
#     ),
# )

# S3 bucket
bucket = aws.s3.Bucket(
    f"{resource_prefix_name}-bucket",
    acl="private",
    versioning=aws.s3.BucketVersioningArgs(enabled=True,),
    tags=base_tags,
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
            # EMR Studio related permissions - TODO temp - EMR studio not working
            # See: https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-studio-service-role.html
            # {
            #     "Sid": "AllowEMRReadOnlyActions",
            #     "Effect": "Allow",
            #     "Action": [
            #         "elasticmapreduce:ListInstances",
            #         "elasticmapreduce:DescribeCluster",
            #         "elasticmapreduce:ListSteps",
            #     ],
            #     "Resource": "*",
            # },
            #             {
            #                 "Sid": "AllowEC2ENIActionsWithEMRTags",
            #                 "Effect": "Allow",
            #                 "Action": [
            #                     "ec2:CreateNetworkInterfacePermission",
            #                     "ec2:DeleteNetworkInterface"
            #                 ],
            #                 "Resource": [
            #                     "arn:aws:ec2:*:*:network-interface/*"
            #                 ],
            #                 "Condition": {
            #                     "StringEquals": {
            #                         "aws:ResourceTag/for-use-with-amazon-emr-managed-policies": "true"
            #                     }
            #                 }
            #             },
            #             {
            #                 "Sid": "AllowEC2ENIAttributeAction",
            #                 "Effect": "Allow",
            #                 "Action": [
            #                     "ec2:ModifyNetworkInterfaceAttribute"
            #                 ],
            #                 "Resource": [
            #                     "arn:aws:ec2:*:*:instance/*",
            #                     "arn:aws:ec2:*:*:network-interface/*",
            #                     "arn:aws:ec2:*:*:security-group/*"
            #                 ]
            #             },
            #             {
            #                 "Sid": "AllowEC2SecurityGroupActionsWithEMRTags",
            #                 "Effect": "Allow",
            #                 "Action": [
            #                     "ec2:AuthorizeSecurityGroupEgress",
            #                     "ec2:AuthorizeSecurityGroupIngress",
            #                     "ec2:RevokeSecurityGroupEgress",
            #                     "ec2:RevokeSecurityGroupIngress",
            #                     "ec2:DeleteNetworkInterfacePermission"
            #                 ],
            #                 "Resource": "*",
            #                 "Condition": {
            #                     "StringEquals": {
            #                         "aws:ResourceTag/for-use-with-amazon-emr-managed-policies": "true"
            #                     }
            #                 }
            #             },
            #             {
            #                 "Sid": "AllowDefaultEC2SecurityGroupsCreationWithEMRTags",
            #                 "Effect": "Allow",
            #                 "Action": [
            #                     "ec2:CreateSecurityGroup"
            #                 ],
            #                 "Resource": [
            #                     "arn:aws:ec2:*:*:security-group/*"
            #                 ],
            #                 "Condition": {
            #                     "StringEquals": {
            #                         "aws:RequestTag/for-use-with-amazon-emr-managed-policies": "true"
            #                     }
            #                 }
            #             },
            #             {
            #                 "Sid": "AllowDefaultEC2SecurityGroupsCreationInVPCWithEMRTags",
            #                 "Effect": "Allow",
            #                 "Action": [
            #                     "ec2:CreateSecurityGroup"
            #                 ],
            #                 "Resource": [
            #                     "arn:aws:ec2:*:*:vpc/*"
            #                 ],
            #                 "Condition": {
            #                     "StringEquals": {
            #                         "aws:ResourceTag/for-use-with-amazon-emr-managed-policies": "true"
            #                     }
            #                 }
            #             },
            #             {
            #                 "Sid": "AllowAddingEMRTagsDuringDefaultSecurityGroupCreation",
            #                 "Effect": "Allow",
            #                 "Action": [
            #                     "ec2:CreateTags"
            #                 ],
            #                 "Resource": "arn:aws:ec2:*:*:security-group/*",
            #                 "Condition": {
            #                     "StringEquals": {
            #                         "aws:RequestTag/for-use-with-amazon-emr-managed-policies": "true",
            #                         "ec2:CreateAction": "CreateSecurityGroup"
            #                     }
            #                 }
            #             },
            #             {
            #                 "Sid": "AllowEC2ENICreationWithEMRTags",
            #                 "Effect": "Allow",
            #                 "Action": [
            #                     "ec2:CreateNetworkInterface"
            #                 ],
            #                 "Resource": [
            #                     "arn:aws:ec2:*:*:network-interface/*"
            #                 ],
            #                 "Condition": {
            #                     "StringEquals": {
            #                         "aws:RequestTag/for-use-with-amazon-emr-managed-policies": "true"
            #                     }
            #                 }
            #             },
            #             {
            #                 "Sid": "AllowEC2ENICreationInSubnetAndSecurityGroupWithEMRTags",
            #                 "Effect": "Allow",
            #                 "Action": [
            #                     "ec2:CreateNetworkInterface"
            #                 ],
            #                 "Resource": [
            #                     "arn:aws:ec2:*:*:subnet/*",
            #                     "arn:aws:ec2:*:*:security-group/*"
            #                 ],
            #                 "Condition": {
            #                     "StringEquals": {
            #                         "aws:ResourceTag/for-use-with-amazon-emr-managed-policies": "true"
            #                     }
            #                 }
            #             },
            #             {
            #                 "Sid": "AllowAddingTagsDuringEC2ENICreation",
            #                 "Effect": "Allow",
            #                 "Action": [
            #                     "ec2:CreateTags"
            #                 ],
            #                 "Resource": "arn:aws:ec2:*:*:network-interface/*",
            #                 "Condition": {
            #                     "StringEquals": {
            #                         "ec2:CreateAction": "CreateNetworkInterface"
            #                     }
            #                 }
            #             },
            #             {
            #                 "Sid": "AllowEC2ReadOnlyActions",
            #                 "Effect": "Allow",
            #                 "Action": [
            #                     "ec2:DescribeSecurityGroups",
            #                     "ec2:DescribeNetworkInterfaces",
            #                     "ec2:DescribeTags",
            #                     "ec2:DescribeInstances",
            #                     "ec2:DescribeSubnets",
            #                     "ec2:DescribeVpcs"
            #                 ],
            #                 "Resource": "*"
            #             },
            #             {
            #                 "Sid": "AllowSecretsManagerReadOnlyActionsWithEMRTags",
            #                 "Effect": "Allow",
            #                 "Action": [
            #                     "secretsmanager:GetSecretValue"
            #                 ],
            #                 "Resource": "arn:aws:secretsmanager:*:*:secret:*",
            #                 "Condition": {
            #                     "StringEquals": {
            #                         "aws:ResourceTag/for-use-with-amazon-emr-managed-policies": "true"
            #                     }
            #                 }
            #             },
            #             {
            #                 "Sid": "AllowWorkspaceCollaboration",
            #                 "Effect": "Allow",
            #                 "Action": [
            #                     "iam:GetUser",
            #                     "iam:GetRole",
            #                     "iam:ListUsers",
            #                     "iam:ListRoles",
            #                     "sso:GetManagedApplicationInstance",
            #                     "sso-directory:SearchUsers"
            #                 ],
            #                 "Resource": "*"
            #             }
        ],
    }


iam_role_policy = aws.iam.RolePolicy(
    f"{resource_prefix_name}-role-policy",
    role=iam_role.id,
    # Need to define a function to pass the bucket.arn - Otherwise an Output is not JSON serializable
    policy=bucket.arn.apply(get_access_role_policy_details),
)

# EMR Studio
# studio_1 = aws.emr.Studio(
#     f"{resource_prefix_name}-emr-studio",
#     auth_mode="IAM",
#     default_s3_location=bucket.bucket.apply(lambda bucket: f"s3://{bucket}/emr_studio"),
#     engine_security_group_id="",
#     service_role=iam_role.arn,
#     subnet_ids=[""],
#     vpc_id="",
#     workspace_security_group_id="",
#     opts=pulumi.ResourceOptions(protect=False),
# )

# EMR Serverless App
poc_spark_emr_serverless_dev_emr_studio = aws.emrserverless.Application(
    f"{resource_prefix_name}-emr-serverless-app",
    initial_capacities=None,  # Not keeping warm instances to limit computational costs
    maximum_capacity=aws.emrserverless.ApplicationMaximumCapacityArgs(
        cpu="4 vCPU",
        memory="10 GB",
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
