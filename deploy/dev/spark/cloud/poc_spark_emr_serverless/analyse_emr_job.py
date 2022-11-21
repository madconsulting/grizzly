import botocore
import boto3

from deploy.dev.spark.cloud.poc_spark_emr_serverless.config import (
    poc_spark_emr_serverless_config as poc_config,
)


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


if __name__ == "__main__":

    # Inputs
    job_run_id = "00f5o2d6c2qhk709"

    # Analyse EMR Serverless job
    analyse_job_run(job_run_id=job_run_id)
