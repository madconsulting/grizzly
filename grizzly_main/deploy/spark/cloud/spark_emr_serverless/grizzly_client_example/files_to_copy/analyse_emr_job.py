import argparse

from grizzly_main.deploy.spark.cloud.spark_emr_serverless.analyse_emr_job import (
    analyse_job_run,
)
from grizzly_main.deploy.spark.cloud.spark_emr_serverless.get_config_variables import (
    get_spark_emr_serverless_config,
)

from deploy_examples.spark_emr_serverless_example.main.main_config import main_config
from deploy_examples.spark_emr_serverless_example.main.get_base_dir import get_client_base_dir

base_dir_client_repo = get_client_base_dir()
spark_emr_serverless_config = get_spark_emr_serverless_config(
    base_dir_client_repo=base_dir_client_repo, **main_config
)

if __name__ in "__main__":

    # Additional Inputs --------------------------------------------------------------------------------------------
    job_run_id = ""
    # --------------------------------------------------------------------------------------------------------------

    # Method to overwrite job_run_id input above calling the script with --job_run_id flag
    parser = argparse.ArgumentParser()
    parser.add_argument("--job_run_id", dest="job_run_id", type=str)
    args, unknown = parser.parse_known_args()
    job_run_id_arg = args.job_run_id
    if job_run_id_arg is not None:
        job_run_id = job_run_id_arg

    if job_run_id == "" or job_run_id is None:
        raise ValueError("job_run_id needs to be defined.")

    # Analyse EMR Serverless job
    analyse_job_run(
        spark_emr_serverless_config=spark_emr_serverless_config,
        job_run_id=job_run_id,
        logs_dir="deploy_examples/spark_emr_serverless_example/main/job_logs",
        base_dir_client_repo=base_dir_client_repo,
    )
