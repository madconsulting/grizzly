import os
import botocore
import boto3
import gzip
import shutil

from path_interations import get_base_dir
from deploy.dev.spark.cloud.poc_spark_emr_serverless.config import (
    poc_spark_emr_serverless_config as poc_config,
)


def download_s3_folder(job_run_id: str, job_name: str, local_dir: str = "deploy/dev/spark/cloud/poc_spark_emr_serverless/job_logs"):
    """
    Download the contents of a folder directory
    Args:
    bucket_name: the name of the s3 bucket
    s3_folder: the folder path in the s3 bucket
    local_dir: a relative or absolute directory path in the local file system
    """
    emr_app_id = poc_config["emr_serverless"]["app_id"]
    s3 = boto3.resource("s3")
    s3_bucket_name = poc_config["s3_bucket"]
    bucket = s3.Bucket(name=s3_bucket_name)
    common_log_path = f"{job_name}/applications/{emr_app_id}/jobs/{job_run_id}/"
    s3_folder = f"logs/{common_log_path}"
    target_base_dir = f"{get_base_dir()}/{local_dir}/{common_log_path}"
    for obj in bucket.objects.filter(Prefix=s3_folder):
        target = os.path.join(target_base_dir, os.path.relpath(obj.key, s3_folder))
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))
        if obj.key[-1] == '/':
            continue
        bucket.download_file(obj.key, target)
        # Unzip GZIP files as .txt files
        if ".gz" in target:
            with gzip.open(target, 'rb') as f_in:
                with open(target.replace(".gz", ".txt"), 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.remove(target)
    print(f"Job logs stored in the following folder: {target_base_dir}")
    print("Check the SPARK_DRIVED/stdout.txt file in that folder for the STDOUT logs")


def analyse_job_run(job_run_id: str) -> None:
    """
    Get information regarding a job ID
    NOTE: boto3 EMR Serverless client does not provide a way to retrieve the Spark UI for historic jobs that already
    finished. You can get that UI that from EMR Studio in the AWS console
    :param job_run_id: EMR Serverless job run ID
    :return: None
    """
    emr_app_id = poc_config["emr_serverless"]["app_id"]
    emr_client = boto3.client("emr-serverless")
    job_run_info = emr_client.get_job_run(
        applicationId=emr_app_id, jobRunId=job_run_id
    )["jobRun"]
    job_state = job_run_info["state"]
    print(f"Job state: {job_state}")
    job_details = job_run_info["stateDetails"]
    print(f"Job state details: {job_details if job_details!='' else 'None'}")
    if "totalResourceUtilization" in job_run_info.keys():
        print(
            f"Job total resource utilization: {job_run_info['totalResourceUtilization']}"
        )
    try:
        dashboard_url = emr_client.get_dashboard_for_job_run(
            applicationId=emr_app_id, jobRunId=job_run_id
        )["url"]
        print(f"Dashboard URL: {dashboard_url}")
    except botocore.exceptions.ClientError as e:
        if "LiveUI is not supported for jobs that are not running" in str(e):
            if job_state in ["SCHEDULED", "PENDING"]:
                print(
                    f"You can't check the Spark Live UI until the job transitions from {job_state} to RUNNING state"
                )
            elif job_state != "RUNNING":
                print(
                    "The job is not running and thus, there is no Spark Live UI available. If you'd like to check"
                    "the the Spark UI for historic jobs, you can get that UI from the EMR Studio in the AWS console."
                )
            else:
                raise ValueError(
                    "The LiveUI should have been available for a running job. Check why. This was the "
                    f"error from EMR Serverless client side: {e}"
                )
        else:
            raise ValueError(f"EMR Serverless client error: {e}")
    job_name = job_run_info["name"]
    download_s3_folder(job_run_id=job_run_id, job_name=job_name)


if __name__ == "__main__":

    # Inputs
    job_run_id = "00f5o2d6c2qhk709"

    # Analyse EMR Serverless job
    analyse_job_run(job_run_id=job_run_id)
