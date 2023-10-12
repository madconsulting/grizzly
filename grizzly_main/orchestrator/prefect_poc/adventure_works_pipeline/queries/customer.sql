SELECT
    c.CustomerID AS c_CustomerID,
    p.PersonType AS c_PersonType,
    p.Title AS c_Title,
    p.EmailPromotion AS c_EmailPromotion
FROM Customer AS c
-- Store information (not required for now)
-- LEFT JOIN Store AS s
-- ON c.StoreID = s.BusinessEntityID
-- Customer person information
LEFT JOIN Person AS p
ON c.PersonID = p.BusinessEntityID