## Bellman Tools (bellman_tools)
Python tools to upload data into SQL Server using SQL Alchemy


## Installation
 - ```pip install bellman-tools```


## Usage

### SQL Tools

To retrieve data from a SQL Server.
You need first to add connection string to the .env file in the project root folder.

Example of the .env file:

```DATABASE_CONNECTION_STRING="mssql+pyodbc://user:password@server_name:1433/{db}?driver=SQL+Server"```

Then you can execute this python code :

```python
from bellman_tools import sql_tools
SQL = sql_tools.Sql(db='DB')
df = SQL.load_dataframe_from_query("SELECT TOP 1 * FROM Test")
``` 

#### Notes on environment loading

- `bellman_tools.sql_tools` looks for a `.env` file only in your current
  working directory (typically your project root) when it is imported. If it
  does not find one, it prints the current directory and continues.
- Best practice is to set environment variables outside of your code (shell,
  CI/CD secrets, process manager). The `.env` loading is a convenience
  fallback.

### Upload Tools

To upload data into a SQL Server database.

```python
import pandas as pd
from bellman_tools import sql_tools, upload_tools

SQL = sql_tools.Sql(db='SAM')
UPLOAD = upload_tools.Upload(SQL)

from bellman_tools.database import Test

df = pd.DataFrame([dict(Test='Testing with Upload tools')])

UPLOAD.load_basic_df_to_db(
    df,
    SQL_Alchemy_Table=Test.Test,
)
```

