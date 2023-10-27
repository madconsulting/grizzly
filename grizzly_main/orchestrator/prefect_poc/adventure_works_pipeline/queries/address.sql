SELECT
    a.AddressID AS a_AddressID,
    a.City AS a_City,
    a.PostalCode AS a_PostalCode,
    s.StateProvinceCode AS a_StateProvinceCode,
    s.CountryRegionCode AS a_CountryRegionCode,
    t.TerritoryID AS a_TerritoryID,
    t.Group AS a_Group
FROM Address a
LEFT JOIN StateProvince s
ON a.StateProvinceId = s.StateProvinceId
LEFT JOIN SalesTerritory t
ON s.TerritoryID = t.TerritoryID
LEFT JOIN CountryRegion c
ON s.CountryRegionCode = c.CountryRegionCode
AND t.CountryRegionCode = c.CountryRegionCode