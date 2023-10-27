SELECT
    -- SalesOrderDetail relevant fields
    so_d.SalesOrderID AS so_d_SalesOrderID,
    so_d.SalesOrderDetailID AS so_d_SalesOrderDetailID,
    so_d.OrderQty AS so_d_OrderQty,
    so_d.ProductID AS so_d_ProductID,
    so_d.UnitPrice AS so_d_UnitPrice,
    so_d.UnitPriceDiscount AS so_d_UnitPriceDiscount,
    so_d.LineTotal AS so_d_LineTotal,
    -- SpecialOffer relevant fields
    offer.SpecialOfferID AS so_d_SpecialOfferID,
    offer.DiscountPct AS so_d_DiscountPct,
    offer.Type AS so_d_Type,
    offer.Category AS so_d_Category
FROM SalesOrderDetail so_d
LEFT JOIN SpecialOfferProduct offer_product
ON so_d.ProductID = offer_product.ProductID
AND so_d.SpecialOfferID = offer_product.SpecialOfferID
LEFT JOIN SpecialOffer offer
ON offer_product.SpecialOfferID = offer.SpecialOfferID