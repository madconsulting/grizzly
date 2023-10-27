import logging

import mysql.connector
import pandas as pd
from mysql.connector import MySQLConnection


def connect_to_database(host: str, port: int, user: str, password: str, database: str) -> MySQLConnection:
    """
    Establishes a connection to the MySQL database.

    :param host: The hostname of the database server.
    :param port: The port number to connect to.
    :param user: The username for authentication.
    :param password: The password for authentication.
    :param database: The name of the database to connect to.
    :return: A connection to the database
    """
    try:
        connection = mysql.connector.connect(host=host, port=port, user=user, password=password, database=database)
        if connection.is_connected():
            logging.info("Connected to the database")
        return connection  # type: ignore
    except mysql.connector.Error as e:
        raise ValueError(f"Error when connecting to MySQL DB: {e}") from e
    except Exception as e:
        raise ValueError(f"Error: {e}") from e


def execute_query(connection: MySQLConnection, query: str) -> pd.DataFrame:
    """
    Executes an SQL query on the database connection and fetches the results.

    :param connection: A connection to the MySQL database.
    :param query: The SQL query to execute.
    :return: The query results as a DataFrame
    """
    try:
        return pd.read_sql(query, connection)
    except mysql.connector.Error as e:
        raise ValueError(f"Error executing query: {e}") from e


def execute_query_from_file(connection: MySQLConnection, query_file_path: str) -> pd.DataFrame:
    """
    Executes an SQL query on the database connection importing the query from the file path

    :param connection: MySQL connection
    :param query_file_path: Query file path
    :return: The query results as a DataFrame
    """
    with open(query_file_path) as file:
        query = file.read()
    return execute_query(connection=connection, query=query)


def close_connection(connection: MySQLConnection) -> None:
    """
    Closes the MySQL database connection.

    :param connection: A connection to the MySQL database.
    :return: None
    """
    if connection.is_connected():
        connection.close()
        logging.info("Connection closed")


if __name__ in "__main__":
    from grizzly_main.orchestrator.prefect_poc.adventure_works_pipeline.configs.dataset_db_credentials import (
        db_credentials,
    )
    from grizzly_main.orchestrator.prefect_poc.tools.custom_logger import add_stdout_logger_as_root

    add_stdout_logger_as_root()

    db_conn = connect_to_database(
        host=db_credentials["hostname"],  # type: ignore
        port=db_credentials["port"],  # type: ignore
        user=db_credentials["username"],  # type: ignore
        password=db_credentials["password"],  # type: ignore
        database=db_credentials["database"],  # type: ignore
    )

    # Example SQL query to retrieve the DB schema
    query_ = """
    SELECT table_name, column_name, data_type
    FROM information_schema.columns
    WHERE TABLE_SCHEMA = 'AdventureWorks2014';
    """
    res_1 = execute_query(connection=db_conn, query=query_)

    # Example to execute query from file
    res_2 = execute_query_from_file(
        connection=db_conn,
        query_file_path="grizzly_main/orchestrator/prefect_poc/adventure_works_pipeline/queries/product.sql",
    )

    close_connection(connection=db_conn)
