import botocore
import boto3
from datetime import datetime
from typing import Dict, Any, Tuple

from grizzly.path_interations import get_base_dir


def upload_file_to_s3(s3_bucket: str, script_file_path: str) -> None:
    """
    Upload script file to S3
    :param s3_bucket: S3 bucket id
    :param script_file_path: File path of the script to be run
    :return: None
    """
    base_dir = get_base_dir()
    s3_client = boto3.client("s3")
    s3_client.upload_file(
        Filename=f"{base_dir}/deploy/dev/spark/cloud/poc_spark_emr_serverless/{script_file_path}",
        Bucket=s3_bucket,
        Key=f"code_examples/{script_file_path}",
    )


def start_emr_app(
    emr_client: botocore.client.BaseClient, emr_app_id: str, emr_app_name: str,
) -> None:
    """
    Start EMR Serverless application - the app needs to be in STARTED mode in order to be able to run a job
    :param emr_client: EMR Serverless boto3 client
    :param emr_app_id: EMR Serverless application ID
    :param emr_app_name: EMR Serverless app name
    :return: None
    """
    emr_app_details = emr_client.get_application(applicationId=emr_app_id)[
        "application"
    ]
    print(f"{emr_app_name} - details:")
    print(emr_app_details)
    _ = emr_client.start_application(applicationId=emr_app_id)


def define_job_run_args(
    spark_emr_serverless_config: Dict[str, Any],
    script_file_path: str,
    emr_app_id: str,
    execution_timeout_min: int = None,
) -> Tuple[str, Dict[str, Any]]:
    """
    Define job run arguments
    :param spark_emr_serverless_config: Spark EMR Serverless config
    :param script_file_path: File path of the script to be run
    :param emr_app_id: EMR Serverless application ID
    :param execution_timeout_min: Execution timeout in minutes
    :return: 
    """
    job_driver = {
        "sparkSubmit": {
            "entryPoint": f"s3://{spark_emr_serverless_config['s3_bucket']}/code_examples/{script_file_path}",
        },
    }
    if len(spark_emr_serverless_config["spark_submit_parameters"]) > 0:
        spark_submit_parameters = " ".join(
            [
                f"--conf {k}={v}"
                for k, v in spark_emr_serverless_config[
                    "spark_submit_parameters"
                ].items()
            ]
        )
        job_driver["sparkSubmit"].update(
            {"sparkSubmitParameters": spark_submit_parameters}
        )
    job_name = f"{script_file_path.replace('/', '__')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    job_args = {
        "applicationId": emr_app_id,
        "executionRoleArn": spark_emr_serverless_config["emr_serverless"][
            "job_role_arn"
        ],
        "jobDriver": job_driver,
        "configurationOverrides": {
            "monitoringConfiguration": {
                "s3MonitoringConfiguration": {
                    "logUri": f"s3://{spark_emr_serverless_config['s3_bucket']}/logs/{job_name}/",
                },
            }
        },
        "name": job_name,
    }
    if execution_timeout_min is not None:
        job_args.update({"executionTimeoutMinutes": execution_timeout_min})
    return job_name, job_args


def trigger_emr_job(
    spark_emr_serverless_config: Dict[str, Any],
    script_file_path: str,
    is_update_script_s3: bool,
    execution_timeout_min: int = None,
) -> str:
    """
    Trigger EMR Serverless job
    :param spark_emr_serverless_config: Spark EMR Serverless config
    :param script_file_path: File path of the script to be run
    :param is_update_script_s3: True if updating the script in s3, False otherwise
    :param execution_timeout_min: Execution timeout in minutes
    :return: Job run ID
    """
    if is_update_script_s3:
        upload_file_to_s3(
            s3_bucket=spark_emr_serverless_config["s3_bucket"],
            script_file_path=script_file_path,
        )
    emr_app_id = spark_emr_serverless_config["emr_serverless"]["app_id"]
    emr_client = boto3.client("emr-serverless")
    start_emr_app(
        emr_client=emr_client,
        emr_app_id=emr_app_id,
        emr_app_name=spark_emr_serverless_config["emr_serverless"]["app_name"],
    )
    job_name, job_args = define_job_run_args(
        spark_emr_serverless_config=spark_emr_serverless_config,
        script_file_path=script_file_path,
        emr_app_id=emr_app_id,
        execution_timeout_min=execution_timeout_min,
    )
    start_job_run_resp = emr_client.start_job_run(**job_args)
    job_run_id = start_job_run_resp["jobRunId"]
    print(f"Job executed with name: {job_name}, and id: {job_run_id}")
    return job_run_id
