import logging
from typing import Any, Optional, Union

import numpy as np
import pandas as pd
from prefect import task

from grizzly_main.orchestrator.prefect_poc.adventure_works_pipeline.configs.dataset_db_credentials import (
    db_credentials as default_db_credentials,
)
from grizzly_main.orchestrator.prefect_poc.adventure_works_pipeline.configs.dataset_info import (
    dataset_fields as default_dataset_fields,
)
from grizzly_main.orchestrator.prefect_poc.tools.mysql_connector import (
    close_connection,
    connect_to_database,
    execute_query_from_file,
)
from grizzly_main.path_interations import get_base_dir


class DataPreprocessing:
    """
    Data preprocessing class for the Adventure Works pipeline
    """

    def __init__(
        self,
        queries_path: str = "orchestrator/prefect_poc/adventure_works_pipeline/queries",
        db_credentials: Optional[dict[str, Union[str, int]]] = None,
        dataset_fields: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize DataPreprocessing class

        :param queries_path: Directory path where all queries for the data groups of the Adventure Works dataset
                             are located
        :param db_credentials: DB credentials
        :param dataset_fields: Dataset fields
        """
        self.base_dir = get_base_dir()
        if db_credentials is None:
            self.db_credentials = default_db_credentials
        else:
            self.db_credentials = db_credentials
        if dataset_fields is None:
            self.dataset_fields = default_dataset_fields
        else:
            self.dataset_fields = dataset_fields
        self.queries_path = f"{self.base_dir}/{queries_path}"
        self.data_group_list = list(self.dataset_fields.keys())  # type: ignore

    def _pull_data(self) -> dict[str, pd.DataFrame]:
        """
        Execute queries for each data group

        :return: Dictionary of data group DataFrame's
        """
        df_dict = {data_group: f"{self.queries_path}/{data_group}.sql" for data_group in self.data_group_list}
        db_conn = connect_to_database(
            host=self.db_credentials["hostname"],  # type: ignore
            port=self.db_credentials["port"],  # type: ignore
            user=self.db_credentials["username"],  # type: ignore
            password=self.db_credentials["password"],  # type: ignore
            database=self.db_credentials["database"],  # type: ignore
        )
        for data_group, query_path in df_dict.items():
            if data_group != "target":
                logging.info(f"Retrieving {data_group} data")
                df_dict[data_group] = execute_query_from_file(connection=db_conn, query_file_path=query_path)
        close_connection(connection=db_conn)
        logging.info("Data pull completed")
        return df_dict

    @staticmethod
    def _compute_churn(df_dict: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """
        Compute churn (target)

        Customer churn is defined as a customer not making another purchase within 180 days of his or her last purchase.
        Thus, the churn variable is defined as follows:
            - 0, if another purchase by the same customer has been made within 180 days after OrderDate
            - 1, if no purchase by the same customer has been made within 180 days after OrderDate
            - NULL, if max(OrderDate) - OrderDate <= 180 days

        Note: We have used the same problem definition to compute the churn as in:
        https://github.com/getml/getml-demo/blob/master/adventure_works.ipynb

        :param df_dict: Dictionary of data group DataFrame's
        :return: Updated dictionary of data group DataFrame's, now containing the target dataframe as well
        """
        sales_order_df = df_dict["sales_order"].copy()
        repeat_purchases = sales_order_df.merge(
            sales_order_df[["so_OrderDate", "so_CustomerID"]],
            on="so_CustomerID",
            how="left",
        )
        repeat_purchases = repeat_purchases[repeat_purchases["so_OrderDate_y"] > repeat_purchases["so_OrderDate_x"]]
        repeat_purchases = repeat_purchases[
            repeat_purchases["so_OrderDate_y"] - repeat_purchases["so_OrderDate_x"] > pd.Timedelta("180 days")
        ]
        repeat_purchases.groupby("so_SalesOrderID", as_index=False).aggregate({"so_CustomerID": "max"})
        repeat_purchase_ids = list(repeat_purchases["so_SalesOrderID"])
        cut_off_date = max(sales_order_df["so_OrderDate"]) - pd.Timedelta("180 days")
        churn = np.asarray(
            [
                np.nan if order_date >= cut_off_date else 0 if order_id in repeat_purchase_ids else 1
                for (order_date, order_id) in zip(sales_order_df["so_OrderDate"], sales_order_df["so_SalesOrderID"])
            ]
        )
        sales_order_df["churn"] = churn
        # Remove rows for which we don't have a target and update the sales_orders DF in the df_dict
        sales_order_df = sales_order_df[~sales_order_df["churn"].isnull()]
        non_target_cols = [col for col in sales_order_df.columns if col != "churn"]
        df_dict["sales_order"] = sales_order_df[non_target_cols]
        # Return target df
        target_df = sales_order_df[["so_SalesOrderID", "churn"]]
        target_df.rename(
            columns={"so_SalesOrderID": "tar_SalesOrderID", "churn": "tar_churn"},
            inplace=True,
        )
        # Need to create dummy index, we can't use SalesOrderID as index for featuretools, as we can't create
        # a relationship between 2 DFs with the same index (as "sales_order")
        target_df.reset_index(inplace=True, drop=True)
        target_df["tar_index"] = target_df.index
        df_dict["target"] = target_df
        logging.info("Churn computed")
        return df_dict

    def run_process(self) -> dict[str, pd.DataFrame]:
        """
        Run main process of the DataPreprocessing class

        :return: Dictionary of data group DataFrame's
        """
        df_dict = self._pull_data()
        df_dict = self._compute_churn(df_dict=df_dict)
        return df_dict


@task
def data_preprocessing_pr_task() -> dict[str, pd.DataFrame]:
    """
    Prefect task for data preprocessing of the Adventure Works dataset

    :return: Dictionary of data group DataFrame's
    """
    logging.info("Starting data preprocessing task in Prefect")
    data_prep = DataPreprocessing()
    df_dict = data_prep.run_process()
    logging.info("Data preprocessing task completed in Prefect")
    return df_dict


if __name__ in "__main__":
    from grizzly_main.orchestrator.prefect_poc.tools.custom_logger import add_stdout_logger_as_root

    add_stdout_logger_as_root()

    data_prep_ = DataPreprocessing()
    # self = data_prep_  # For debugging purposes

    df_dict_ = data_prep_.run_process()
