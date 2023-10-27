SELECT
    so_reason.SalesOrderID AS so_r_SalesOrderID,
    reason.SalesReasonID AS so_r_SalesReasonID,
    reason.ReasonType AS so_r_ReasonType
FROM SalesOrderHeaderSalesReason so_reason
LEFT JOIN SalesReason reason
ON so_reason.SalesReasonID = reason.SalesReasonID