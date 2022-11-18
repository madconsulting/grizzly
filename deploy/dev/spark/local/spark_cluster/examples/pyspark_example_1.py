from deploy.dev.spark.utils.spark_context import get_spark_context


def spark_example_1(run_mode: str) -> None:
    """
    Spark example nº 1 - Create and show DataFrame
    :param run_mode: Run mode
    :return: None
    """
    spark = get_spark_context(
        app_name="pyspark_example_1", run_mode=run_mode
    )
    data = [
        ("James", "", "Smith", "1991-04-01", "M", 3000),
        ("Michael", "Rose", "", "2000-05-19", "M", 4000),
        ("Robert", "", "Williams", "1978-09-05", "M", 4000),
        ("Maria", "Anne", "Jones", "1967-12-01", "F", 4000),
        ("Jen", "Mary", "Brown", "1980-02-17", "F", -1),
    ]
    columns = ["firstname", "middlename", "lastname", "dob", "gender", "salary"]
    df = spark.createDataFrame(data=data, schema=columns)
    df.show()
    spark.stop()


if __name__ == "__main__":

    # Inputs
    is_run_on_cluster = True

    # Example trigger
    if is_run_on_cluster:
        run_mode = "local_cluster"
    else:
        run_mode = "local_single_worker"
    spark_example_1(run_mode=run_mode)
