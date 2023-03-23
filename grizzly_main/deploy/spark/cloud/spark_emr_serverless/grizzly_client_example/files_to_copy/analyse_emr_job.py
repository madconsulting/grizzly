from grizzly_main.deploy.spark.cloud.spark_emr_serverless.analyse_emr_job import (
    analyse_job_run,
)
from deploy_examples.spark_emr_serverless_example.main.main_config import main_config
from grizzly_main.deploy.spark.cloud.spark_emr_serverless.get_config_variables import (
    get_spark_emr_serverless_config,
)
from grizzly_main.path_interations import get_base_dir

base_dir_client_repo = get_base_dir(path_end=main_config["repository_name"],)
spark_emr_serverless_config = get_spark_emr_serverless_config(
    base_dir_client_repo=base_dir_client_repo, **main_config
)

if __name__ in "__main__":
    # Additional Inputs --------------------------------------------------------------------------------------------
    job_run_id = ""
    # --------------------------------------------------------------------------------------------------------------

    # Analyse EMR Serverless job
    analyse_job_run(
        spark_emr_serverless_config=spark_emr_serverless_config,
        job_run_id=job_run_id,
        logs_dir="deploy_examples/spark_emr_serverless_example/main/job_logs",
        base_dir_client_repo=base_dir_client_repo
    )
