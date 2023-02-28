"""
This is inspired in the Pyspark code example from
https://github.com/aws-samples/emr-serverless-samples/blob/main/examples/pyspark/extreme_weather.py
"""

from pyspark.sql import SparkSession, DataFrame, Row
from pyspark.sql import functions as F


def find_largest(df: DataFrame, col_name: str) -> Row:
    """
    Find the largest value in `col_name` column.
    Values of 99.99, 999.9 and 9999.9 are excluded because they indicate "no reading" for that attribute.
    While 99.99 _could_ be a valid value for temperature, for example, we know there are higher readings.
    :param df: DataFrame
    :param col_name: Column name
    :return: Row with largest value
    """
    return (
        df.select(
            "STATION", "DATE", "LATITUDE", "LONGITUDE", "ELEVATION", "NAME", col_name
        )
        .filter(~F.col(col_name).isin([99.99, 999.9, 9999.9]))
        .orderBy(F.desc(col_name))
        .limit(1)
        .first()
    )


def pyspark_example_3(
    spark: SparkSession,
    year: int,
    is_specific_csv_file_only: bool,
    csv_file_name: str = None,
):
    """
    Pyspark example nº 3 - extreme-weather
    Displays extreme weather stats (highest temperature, wind, precipitation) for the given, or latest, year.
    :param spark: Spark session
    :param year: Year
    :param is_specific_csv_file_only: True if using a single specific CSV file for that year, False if using all the
                                      csv files for that year.
    :param csv_file_name: CSV file name
    :return: None
    """
    s3_path = f"s3://noaa-gsod-pds/{year}/"
    if is_specific_csv_file_only:
        if csv_file_name is None:
            raise ValueError(
                "csv_file_name needs to be defined if is_specific_csv_file_only is True"
            )
        s3_path += csv_file_name
    df = spark.read.csv(s3_path, header=True, inferSchema=True)
    print(f"The amount of weather readings in {year} is: {df.count()}\n")
    print(f"Here are some extreme weather stats for {year}:")
    stats_to_gather = [
        {"description": "Highest temperature", "column_name": "MAX", "units": "°F"},
        {
            "description": "Highest all-day average temperature",
            "column_name": "TEMP",
            "units": "°F",
        },
        {"description": "Highest wind gust", "column_name": "GUST", "units": "mph"},
        {
            "description": "Highest average wind speed",
            "column_name": "WDSP",
            "units": "mph",
        },
        {
            "description": "Highest precipitation",
            "column_name": "PRCP",
            "units": "inches",
        },
    ]
    for stat in stats_to_gather:
        max_row = find_largest(df, stat["column_name"])
        print(
            f"  {stat['description']}: {max_row[stat['column_name']]}{stat['units']} on {max_row.DATE} at {max_row.NAME} ({max_row.LATITUDE}, {max_row.LONGITUDE})"
        )
