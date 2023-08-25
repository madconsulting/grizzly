import gzip
import os
import pathlib
import shutil
from typing import Any, Dict, Union

import boto3
import botocore


def download_logs_from_s3(
    s3_bucket: str,
    emr_app_id: str,
    job_run_id: str,
    job_name: str,
    logs_dir: str,
    base_dir_client_repo: Union[str, pathlib.Path] = "",
) -> None:
    """
    Download Spark logs from s3
    :param s3_bucket: S3 bucket id
    :param emr_app_id: EMR Serverless application ID
    :param job_run_id: Job run id
    :param job_name: Job name
    :param logs_dir: Relative directory path in the client repository where to store the downloaded logs
    :param base_dir_client_repo: Base directory of client repository
    :return: None
    """
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(name=s3_bucket)
    common_log_path = f"{job_name}/applications/{emr_app_id}/jobs/{job_run_id}/"
    s3_folder = f"logs/{common_log_path}"
    target_base_dir = f"{base_dir_client_repo}/{logs_dir}/{common_log_path}"
    print(f"Job logs stored in the following folder: {target_base_dir}")
    for obj in bucket.objects.filter(Prefix=s3_folder):
        target = os.path.join(target_base_dir, os.path.relpath(obj.key, s3_folder))
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))
        if obj.key[-1] == "/":
            continue
        bucket.download_file(obj.key, target)
        # Unzip GZIP files as .txt files
        if ".gz" in target:
            with gzip.open(target, "rb") as f_in:
                with open(target.replace(".gz", ".txt"), "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.remove(target)
        # Print the stdout logs from the driver
        if "SPARK_DRIVER/stdout" in target:
            print("Printing below the Spark driver stdout logs:")
            print("-" * 50, end="\n\n")
            with open(target.replace(".gz", ".txt"), encoding="utf8") as f:
                for line in f:
                    print(line.strip())
            print("-" * 50)


def analyse_job_run(
    spark_emr_serverless_config: Dict[str, Any],
    job_run_id: str,
    logs_dir: str,
    base_dir_client_repo: Union[str, pathlib.Path] = "",
) -> None:
    """
    Get information regarding a job ID

    NOTE: boto3 EMR Serverless client does not provide a way to retrieve the Spark UI for historic jobs that already
    finished. You can get that UI that from EMR Studio in the AWS console (or alternatively build a custom docker file
    to access that Spark UI locally as described in here:
    https://github.com/aws-samples/emr-serverless-samples/blob/main/utilities/spark-ui/README.md,
    but it's simpler from the EMR Studio)

    :param spark_emr_serverless_config: Spark EMR Serverless config
    :param job_run_id: EMR Serverless job run ID
    :param logs_dir: Relative directory path in the client repository where to store the downloaded logs
    :param base_dir_client_repo: Base directory of client repository
    :return: None
    """
    # https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/job-states.html
    not_started_job_states = ["submitted", "pending", "scheduled"]
    emr_app_id = spark_emr_serverless_config["emr_serverless"]["app_id"]
    emr_client = boto3.client("emr-serverless")
    job_run_info = emr_client.get_job_run(applicationId=emr_app_id, jobRunId=job_run_id)["jobRun"]
    job_state = job_run_info["state"].lower()
    print(f"Job state: {job_state}")
    job_details = job_run_info["stateDetails"]
    print(f"Job state details: {job_details if job_details!='' else 'None'}")
    if "totalResourceUtilization" in job_run_info.keys():
        print(f"Job total resource utilization: {job_run_info['totalResourceUtilization']}")
    try:
        dashboard_url = emr_client.get_dashboard_for_job_run(applicationId=emr_app_id, jobRunId=job_run_id)["url"]
        print(f"Dashboard URL: {dashboard_url}")
    except botocore.exceptions.ClientError as e:
        if "LiveUI is not supported for jobs that are not running" in str(e):
            if job_state in not_started_job_states:
                print(f"You can't check the Spark Live UI until the job transitions from {job_state} to RUNNING state")
            elif job_state != "running":
                print(
                    "The job is not running and thus, there is no Spark Live UI available. If you'd like to check "
                    "the Spark UI for historic jobs, you can get that UI from the EMR Studio in the AWS console."
                )
            else:
                raise ValueError(
                    "The LiveUI should have been available for a running job. Check why. This was the "
                    f"error from EMR Serverless client side: {e}"
                ) from e
        else:
            raise ValueError(f"EMR Serverless client error: {e}") from e
    job_name = job_run_info["name"]
    if job_state not in not_started_job_states:
        download_logs_from_s3(
            s3_bucket=spark_emr_serverless_config["s3_bucket"],
            emr_app_id=spark_emr_serverless_config["emr_serverless"]["app_id"],
            job_run_id=job_run_id,
            job_name=job_name,
            logs_dir=logs_dir,
            base_dir_client_repo=base_dir_client_repo,
        )
