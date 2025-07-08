"""
This file provides an example of how to import the s3sql client and use it in python code.
This code is equivalent to the terminal command: 
```
s3sql query --uri "s3://s3sql-demo/sql_engines.csv" --sql "SELECT * FROM df" --out "output.csv"
```
"""

import s3sql.cli as s3sql
import os

uri = 's3://s3sql-demo/sql_engines.csv' #todo: change to your bucket/file path
sql = 'SELECT * from df'
out = 'output.csv'

s3sql_client = s3sql.S3SQLClient()
#s3sql_client.set_key(os.getenv('AWS_ACCESS_KEY_ID')) #todo: set to env variable with access key.
#s3sql_client.set_secret(os.getenv('AWS_SECRET_ACCESS_KEY')) #todo: set to env variable with access secret.
s3sql_client.query(uri, sql, out)