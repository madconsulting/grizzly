from typing import Any, Optional

from woodwork.logical_types import Categorical, CountryCode, Datetime, Double, Integer, PostalCode

dataset_fields: Optional[dict[str, dict[str, Any]]] = {
    "target": {
        "short_prefix": "tar",
        "index": "index",
        "time_index": None,
        "logical_types": {
            "SalesOrderID": Categorical,
            "churn": Categorical,
        },
    },
    "sales_order": {
        "short_prefix": "so",
        "index": "SalesOrderID",
        "time_index": "OrderDate",
        "logical_types": {
            "RevisionNumber": Categorical,
            "DueDate": Datetime,
            "ShipDate": Datetime,
            "OnlineOrderFlag": Categorical,
            "CustomerID": Categorical,
            "SalesPersonID": Categorical,
            "TerritoryID": Categorical,
            "ShipToAddressID": Categorical,
            "SubTotal": Double,
            "TaxAmt": Double,
            "Freight": Double,
            "TotalDue": Double,
        },
    },
    "sales_order_detail": {
        "short_prefix": "so_d",
        "index": "SalesOrderDetailID",
        "time_index": None,
        "logical_types": {
            "SalesOrderID": Categorical,
            "OrderQty": Integer,
            "ProductID": Categorical,
            "UnitPrice": Double,
            "UnitPriceDiscount": Double,
            "LineTotal": Double,
            "SpecialOfferID": Categorical,
            "DiscountPct": Double,
            "Type": Categorical,
            "Category": Categorical,
        },
    },
    "sales_order_reason": {
        "short_prefix": "so_r",
        "index": ["SalesOrderID", "SalesReasonID"],
        "time_index": None,
        "logical_types": {
            "SalesReasonID": Categorical,
            "ReasonType": Categorical,
        },
    },
    "product": {
        "short_prefix": "p",
        "index": "ProductID",
        "time_index": None,
        "logical_types": {
            "ProductID": Categorical,
            "Color": Categorical,
            "Weight": Double,
            "ProductLine": Categorical,
            "Class": Categorical,
            "Style": Categorical,
            "ProductSubcategoryID": Categorical,
            "ProductModelID": Categorical,
            "ProductCategoryID": Categorical,
        },
    },
    "customer": {
        "short_prefix": "c",
        "index": "CustomerID",
        "time_index": None,
        "logical_types": {
            "CustomerID": Categorical,
            "PersonType": Categorical,
            "Title": Categorical,
            "EmailPromotion": Categorical,
        },
    },
    "address": {
        "short_prefix": "a",
        "index": "AddressID",
        "time_index": None,
        "logical_types": {
            "AddressID": Categorical,
            "City": Categorical,
            "PostalCode": PostalCode,
            "StateProvinceCode": Categorical,
            "CountryRegionCode": CountryCode,
            "TerritoryID": Categorical,
            "Group": Categorical,
        },
    },
}

# Define featuretool relationships
dataset_relationships = [
    # Many to one relationships (parent to child)
    {
        "parent_dataframe_name": "customer",
        "parent_column_name": "CustomerID",
        "child_dataframe_name": "sales_order",
        "child_column_name": "CustomerID",
    },
    {
        "parent_dataframe_name": "address",
        "parent_column_name": "AddressID",
        "child_dataframe_name": "sales_order",
        "child_column_name": "ShipToAddressID",
    },
    {
        "parent_dataframe_name": "sales_order",
        "parent_column_name": "SalesOrderID",
        "child_dataframe_name": "sales_order_reason",
        "child_column_name": "SalesOrderID",
    },
    {
        "parent_dataframe_name": "sales_order",
        "parent_column_name": "SalesOrderID",
        "child_dataframe_name": "sales_order_detail",
        "child_column_name": "SalesOrderID",
    },
    {
        "parent_dataframe_name": "product",
        "parent_column_name": "ProductID",
        "child_dataframe_name": "sales_order_detail",
        "child_column_name": "ProductID",
    },
    # Target dataframe relationship (one to one)
    {
        "parent_dataframe_name": "sales_order",
        "parent_column_name": "SalesOrderID",
        "child_dataframe_name": "target",
        "child_column_name": "SalesOrderID",
    },
]
