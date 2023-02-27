from typing import Dict, Any

from grizzly.deploy.spark.cloud.spark_emr_serverless.build.build_artifacts_interactions import (
    get_poetry_wheel_file,
    get_venv_file,
)
from grizzly.iac_pulumi.pulumi_rest_api_functions import get_pulumi_stack_state


def _find_single_pulumi_resource_based_on_type(
    stack_state_dict: Dict[str, Any], resource_type: str, project_stack_name: str = "",
):
    chosen_resource_dict = None
    for resource_dict in stack_state_dict["deployment"]["resources"]:
        if resource_dict["type"] == resource_type:
            if chosen_resource_dict is not None:
                raise ValueError(
                    f"Multiple resources of type {resource_type} found in Pulumi stack {project_stack_name}. "
                    "This is not expected."
                )
            else:
                chosen_resource_dict = resource_dict
    if chosen_resource_dict is None:
        raise ValueError(
            f"resource of type {resource_type} not found in Pulumi stack {project_stack_name}."
        )
    return chosen_resource_dict


def get_s3_bucket_id_from_pulumi(
    stack_state_dict: Dict[str, Any], project_stack_name: str = "",
):
    return _find_single_pulumi_resource_based_on_type(
        stack_state_dict=stack_state_dict,
        resource_type="aws:s3/bucket:Bucket",
        project_stack_name=project_stack_name,
    )["id"]


def get_emr_serverless_app_from_pulumi(
    stack_state_dict: Dict[str, Any], project_stack_name: str = "",
):
    app_dict = _find_single_pulumi_resource_based_on_type(
        stack_state_dict=stack_state_dict,
        resource_type="aws:emrserverless/application:Application",
        project_stack_name=project_stack_name,
    )
    return app_dict["id"], app_dict["outputs"]["name"]


def get_job_role_arm_from_pulumi(
    stack_state_dict: Dict[str, Any], project_stack_name: str = "",
):
    return _find_single_pulumi_resource_based_on_type(
        stack_state_dict=stack_state_dict,
        resource_type="aws:iam/role:Role",
        project_stack_name=project_stack_name,
    )["outputs"]["arn"]


def get_spark_emr_serverless_config(
    pulumi_organization: str,
    pulumi_project: str,
    pulumi_stack: str,
    spark_resources_dict: Dict[str, Any],
    poetry_package_version: str = None,
    **kwargs,
):
    """

    :param pulumi_organization:
    :param pulumi_project:
    :param pulumi_stack:
    :param spark_resources_dict:
    :param poetry_package_version: Poetry package version. If a specific version is provided, it will override current
                                   Poetry package (e.g. to run PySpark code using a past deployed version of Poetry)
    :return:
    """
    stack_state_dict = get_pulumi_stack_state(
        pulumi_organization=pulumi_organization,
        pulumi_project=pulumi_project,
        is_allow_input_token=False,
        pulumi_stack=pulumi_stack,
    )
    project_stack_name = f"{pulumi_organization}/{pulumi_project}/{pulumi_stack}"
    s3_bucket = get_s3_bucket_id_from_pulumi(
        stack_state_dict=stack_state_dict, project_stack_name=project_stack_name,
    )
    app_id, app_name = get_emr_serverless_app_from_pulumi(
        stack_state_dict=stack_state_dict, project_stack_name=project_stack_name,
    )
    job_role_arm = get_job_role_arm_from_pulumi(
        stack_state_dict=stack_state_dict, project_stack_name=project_stack_name,
    )
    venv_file_name = get_venv_file(package_version=poetry_package_version)
    wheel_file_name = get_poetry_wheel_file(package_version=poetry_package_version)
    return {
        "s3_bucket": s3_bucket,
        "emr_serverless": {
            "app_name": app_name,
            "app_id": app_id,
            "job_role_arn": job_role_arm,
        },
        # The default Spark Job properties are described below:
        # https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/jobs-spark.html#spark-defaults
        # If using custom properties ensure that these are within the worker configuration limits:
        # (https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/application-capacity.html#worker-configs)
        # CPU - Memory:
        #  - 1vCPU -> Minimum 2 GB, maximum 8 GB, in 1 GB increments
        #  - 2vCPU -> Minimum 4 GB, maximum 16 GB, in 1 GB increments
        #  - 4vCPU -> Minimum 8 GB, maximum 30 GB, in 1 GB increments
        # Disk: Minimum 20GB, maximum 200 GB.
        # Finally, note that the maximum_capacity in Pulumi needs to be set equal or above the job properties
        # (https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/application-capacity.html#max-capacity)
        "spark_submit_parameters": {
            # Custom virtual environment
            "spark.archives": f"s3://{s3_bucket}/artifacts/venvs/{venv_file_name}#environment",
            "spark.emr-serverless.driverEnv.PYSPARK_DRIVER_PYTHON": "./environment/bin/python",
            "spark.emr-serverless.driverEnv.PYSPARK_PYTHON": "./environment/bin/python",
            "spark.emr-serverless.executorEnv.PYSPARK_PYTHON": "./environment/bin/python",
            # Base code package as a wheel file
            "spark.submit.pyFiles": f"s3://{s3_bucket}/artifacts/package_wheel_files/{wheel_file_name}",
            # Worker specifications
            "spark.driver.cores": str(spark_resources_dict["driver"]["num_cores"]),
            "spark.driver.memory": f"{spark_resources_dict['driver']['memory_in_GB']}g",
            "spark.driver.disk": spark_resources_dict["driver"]["disk_in_GB"],
            "spark.executor.cores": str(spark_resources_dict["executor"]["num_cores"]),
            "spark.executor.instances": str(
                spark_resources_dict["executor"]["instances"]
            ),
            "spark.executor.memory": f"{spark_resources_dict['executor']['memory_in_GB']}g",
            "spark.executor.disk": spark_resources_dict["executor"]["disk_in_GB"],
        },
    }
