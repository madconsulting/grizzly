import sys
from pyspark.conf import SparkConf
from pyspark.sql import SparkSession


# TODO - script temp duplicated from local/spark_cluster for debugging purposes - without imports from other
#  files (I would need a custom docker with the deploy poetry package implemented beforehand)


def check_python_version() -> None:
    """
    Check python version corresponds to the one installed in the custom venv used for the job
    :return: None
    """
    print(sys.executable)
    print(sys.version)


def spark_simple_example() -> None:
    """
    Spark example nº 1 - Create and show DataFrame
    :param run_mode: Run mode
    :return: None
    """
    check_python_version()
    spark_config = SparkConf()
    config_var_list = [("spark.app.name", "Simple Spark Example")]
    spark_config.setAll(config_var_list)
    spark = SparkSession.builder.config(conf=spark_config).getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
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
    spark_simple_example()
