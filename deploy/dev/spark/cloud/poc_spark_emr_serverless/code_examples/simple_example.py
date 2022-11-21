from pyspark.conf import SparkConf
from pyspark.sql import SparkSession


# TODO - script temp duplicated from local/spark_cluster for debugging purposes - without imports from other
#  files (I would need a custom docker with the deploy poetry package implemented beforehand)


def spark_simple_example() -> None:
    """
    Spark example nº 1 - Create and show DataFrame
    :param run_mode: Run mode
    :return: None
    """
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
    # TODO - This example is failing on the cloud due to the app limits:
    # com.amazonaws.services.emrserverlessresourcemanager.model.ApplicationMaxCapacityExceededException: Worker could
    # not be allocated as the application has exceeded maximumCapacity settings: [cpu: 2 vCPU, memory: 8 GB, disk: 20 GB]
    # TODO - Need to change the settings in the config.py or extend limits in Pulumi in order to make it work!!
    spark_simple_example()
