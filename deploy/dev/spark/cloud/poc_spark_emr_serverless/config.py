poc_spark_emr_serverless_config = {
    "s3_bucket": "poc-spark-emr-serverless-dev-bucket-7cb2462",
    "emr_serverless": {
        "app_name": "poc-spark-emr-serverless-dev-emr-serverless-app-a442433",
        "app_id": "00f5lp5iapag6909",
        "job_role_arn": "arn:aws:iam::561796644494:role/poc-spark-emr-serverless-dev-role-c4ae352",
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
        # Custom environment
        "spark.archives": "s3://poc-spark-emr-serverless-dev-bucket-7cb2462/artifacts/pyspark_venv/pyspark_3.9.12.tar.gz#environment",
        "spark.emr-serverless.driverEnv.PYSPARK_DRIVER_PYTHON": "./environment/bin/python",
        "spark.emr-serverless.driverEnv.PYSPARK_PYTHON": "./environment/bin/python",
        "spark.emr-serverless.executorEnv.PYSPARK_PYTHON": "./environment/bin/python",
        # Worker specifications
        "spark.driver.cores": "1",
        "spark.driver.memory": "2g",
        "spark.driver.disk": 20,
        "spark.executor.instances": "2",
        "spark.executor.cores": "1",
        "spark.executor.memory": "2g",
        "spark.executor.disk": 20,
    },
}
