from grizzly_main.deploy.spark.cloud.spark_emr_serverless.stop_emr_app import (
    stop_emr_app,
)
from deploy_examples.spark_emr_serverless_example.main_config import (
    main_config,
)
from grizzly_main.deploy.spark.cloud.spark_emr_serverless.get_config_variables import (
    get_spark_emr_serverless_config,
)

spark_emr_serverless_config = get_spark_emr_serverless_config(**main_config)

# Stop EMR Serverless application
stop_emr_app(spark_emr_serverless_config=spark_emr_serverless_config)
