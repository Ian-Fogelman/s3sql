#pytest -s s3sql/test_cli.py
import re
import pytest
import pandas as pd
from click.testing import CliRunner
from cli import get_key,get_secret,query, cli
runner = CliRunner()

def check_result_message(result_str):
    if('Query executed in' in result_str and 'Data successfully written to file' in result_str):
        return True
    else:
        return False
    

def test_get_version_flag():
    result = runner.invoke(cli, ['--version'])
    result_str = result.output
    assert re.match(r'^s3sql, version \d+\.\d+\.\d+$', result_str.strip())

def test_get_key():
    #s3sql get-key
    result = runner.invoke(get_key)
    result_str = result.output
    assert('Stored API key:' in result_str)

def test_get_secret():
    #s3sql get-secret
    result = runner.invoke(get_secret)
    result_str = result.output
    assert('Stored API secret:' in result_str)

def test_query_csv():
    #s3sql query --uri "s3://s3sql-demo/folder_example/sql_database_releases.csv" --query "SELECT * FROM df WHERE 1=1 LIMIT 1" --out "output.csv"
    output_file = 'output.csv'
    result = runner.invoke(query, ['--uri','s3://s3sql-demo/sql_engines.csv',
                                   '--query','SELECT * FROM df WHERE 1=1',
                                   '--out',output_file])
    result_str = result.output
    df = pd.read_csv('output.csv')
    assert(df.shape == (5, 7)) #5 rows 7 columns in results (exclude header)
    assert(check_result_message(result_str) == True)

def test_query_json():
    #s3sql query --uri "s3://s3sql-demo/json/database_default_ports.json" --query "SELECT * FROM df WHERE 1=1" --out "output.json"
    output_file = 'output.json'
    result = runner.invoke(query, ['--uri','s3://s3sql-demo/json/database_default_ports.json',
                                   '--query','SELECT * FROM df WHERE 1=1',
                                   '--out',output_file])
    result_str = result.output
    df = pd.read_json(output_file)
    assert(df.shape == (5, 2)) #5 rows 2 columns in results (exclude header)
    assert(check_result_message(result_str) == True)

def test_query_parquet():
    #s3sql query --uri "s3://s3sql-demo/parquet/database_features.parquet" --query "SELECT * FROM df WHERE 1=1" --out "output.parquet"
    output_file = 'output.parquet'
    result = runner.invoke(query, ['--uri','s3://s3sql-demo/parquet/database_features.parquet',
                                   '--query','SELECT * FROM df WHERE 1=1',
                                   '--out',output_file])
    result_str = result.output
    df = pd.read_parquet(output_file)
    assert(df.shape == (5, 3)) #5 rows 3 columns in results (exclude header)
    assert(check_result_message(result_str) == True)