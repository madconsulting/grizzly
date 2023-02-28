from grizzly_main.deploy.spark.cloud.spark_emr_serverless.analyse_emr_job import (
    analyse_job_run,
)
from grizzly_main.deploy.spark.cloud.spark_emr_serverless.grizzly_client_example.main_config import (
    main_config,
)
from grizzly_main.deploy.spark.cloud.spark_emr_serverless.get_config_variables import (
    get_spark_emr_serverless_config,
)

spark_emr_serverless_config = get_spark_emr_serverless_config(**main_config)

# Additional Inputs --------------------------------------------------------------------------------------------
job_run_id = "00f63dfqf53i0i09"
# --------------------------------------------------------------------------------------------------------------

# Analyse EMR Serverless job
analyse_job_run(
    spark_emr_serverless_config=spark_emr_serverless_config, job_run_id=job_run_id
)
