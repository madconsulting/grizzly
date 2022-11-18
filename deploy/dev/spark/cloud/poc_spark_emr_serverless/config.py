poc_spark_emr_serverless_config = {
    "s3_bucket": "poc-spark-emr-serverless-dev-bucket-7cb2462",
    "emr_serverless": {
        "app_name": "poc-spark-emr-serverless-dev-emr-serverless-app-a442433",
        "app_id": "00f5lp5iapag6909",
        "job_role_arn": "arn:aws:iam::561796644494:role/poc-spark-emr-serverless-dev-role-c4ae352",
    },
    "spark_submit_parameters": {
        "spark.driver.cores": "1",
        "spark.driver.memory": "3g",
        "spark.executor.cores": "4",
        "spark.executor.memory": "3g",
        "spark.executor.instances": "1",
    },
}