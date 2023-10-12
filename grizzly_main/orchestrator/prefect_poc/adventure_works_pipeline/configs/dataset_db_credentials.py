from typing import Union

# Credentials to publicly available dataset from: https://relational.fit.cvut.cz/dataset/AdventureWorks
db_credentials: dict[str, Union[str, int]] = {
    "database": "AdventureWorks2014",
    "hostname": "relational.fit.cvut.cz",
    "port": 3306,
    "username": "guest",
    "password": "relational",
}
