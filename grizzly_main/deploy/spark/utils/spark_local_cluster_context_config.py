spark_local_cluster_context_config = {
    "spark.submit.deployMode": "client",
    "spark.driver.bindAddress": "127.0.0.1",  # Bind to localhost only
    "spark.ui.showConsoleProgress": "true",
    "spark.eventLog.enabled": "false",
    # The line `spark.executor.memory": "2GB"` is setting the amount of memory allocated to each executor in the Spark
    # cluster to 2GB. Executors are the worker processes that run the tasks in parallel on the cluster. By setting this
    # configuration, you are specifying the amount of memory that each executor can use for processing data.
    "spark.executor.memory": "2GB",
}
