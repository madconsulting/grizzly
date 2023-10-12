SELECT
    SalesOrderID AS so_SalesOrderID,
    RevisionNumber AS so_RevisionNumber,
    OrderDate AS so_OrderDate,
    ModifiedDate AS so_ModifiedDate,
    DueDate AS so_DueDate,
    ShipDate AS so_ShipDate,
    -- Status AS so_Status -> Not used (only status 5 = Shipped present)
    OnlineOrderFlag AS  so_OnlineOrderFlag,
    CustomerID AS so_CustomerID,
    SalesPersonID AS so_SalesPersonID,
    TerritoryID AS so_TerritoryID,
    ShipToAddressID AS so_ShipToAddressID,
    SubTotal AS so_SubTotal,
    TaxAmt AS so_TaxAmt,
    Freight AS so_Freight,
    TotalDue AS so_TotalDue
FROM SalesOrderHeader