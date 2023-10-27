SELECT
    p.ProductID AS p_ProductID,
    p.Color AS p_Color,
    p.Weight AS p_Weight,
    p.ProductLine AS p_ProductLine,
    p.Class AS p_Class,
    p.Style AS p_Style,
    p.ProductSubcategoryID AS p_ProductSubcategoryID,
    p.ProductModelID AS p_ProductModelID,
    p_sub.ProductCategoryID AS p_ProductCategoryID
FROM Product p
LEFT JOIN ProductSubcategory p_sub
ON p.ProductSubcategoryID = p_sub.ProductSubcategoryID
