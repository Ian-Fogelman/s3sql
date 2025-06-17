import click
import requests 
import json
import configparser
import os
import duckdb
from tabulate import tabulate
import boto3
import pandas as pd
import time

# Define the config file path
CONFIG_DIR = os.path.expanduser("~/s3sql") #C:\Users\<YourUsername>\s3sql\ | MacOS ...
CONFIG_FILE = os.path.join(CONFIG_DIR, "credentials") #Windows: ...\credentials | MacOS ...
os.makedirs(CONFIG_DIR, exist_ok=True) # Create the directory if it doesn't exist

def get_config():
    """Load the config file."""
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    if 'DEFAULT' not in config:
        config['DEFAULT'] = {}
    return config

def save_config(config):
    """Save the config file."""
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

def mask_string(input_string): #show only the first 3 and last 3 characters of string for sensitive credentials
    if len(input_string) <= 6:
        return "*" * len(input_string)
    masked_string = input_string[:3] + "*" * (len(input_string) - 6) + input_string[-3:]
    return masked_string

@click.group()
def cli():
    """The S3SQL CLI, the simplest way to query your S3 objects."""
    pass

@cli.command()
@click.option('--api-key', prompt='Enter API key', hide_input=True, help='Set the API key.')
def set_key(api_key):
    """Set and persist the access key."""
    config = get_config()
    config['DEFAULT']['api_key'] = api_key
    save_config(config)
    click.echo("API key saved successfully!")

@cli.command()
def get_key():
    """Retrieve the stored API key."""
    config = get_config()
    api_key = config['DEFAULT'].get('api_key', None)
    if api_key:
        masked_key = mask_string(api_key)
        click.echo(f"Stored API key: {masked_key}")
    else:
        click.echo("No API key set. Use 'set-key' to set one.")

@cli.command()
@click.option('--api-secret', prompt='Enter secret key', hide_input=True, help='Set the secret key.')
def set_secret(api_secret):
    """Set and persist the secret key."""
    config = get_config()
    config['DEFAULT']['api_secret'] = api_secret
    save_config(config)
    click.echo("API secret saved successfully!")

@cli.command()
def get_secret():
    """Retrieve the stored secret key."""
    config = get_config()
    api_secret = config['DEFAULT'].get('api_secret', None)
    if api_secret:
        masked_secret = mask_string(api_secret)
        click.echo(f"Stored API secret: {masked_secret}")
    else:
        click.echo("No API key set. Use 'set-key' to set one.")

@cli.command()
@click.option('--uri', prompt='Enter a quoted S3 URI for the object', hide_input=True, help='Example: s3://osg-repo-scan-data/branches.csv')
@click.option('--query', prompt='Enter a quoted SQL query for the data returned from the object', hide_input=True, help='Example: SELECT * FROM df WHERE ID > 1')
@click.option('--out', default=None, hide_input=True, help='Example: output.csv') #no "prompt", makes optional, only set if writing to file.
def query(uri,query,out):
    start = time.time()
    """Query an object stored in S3."""
    config = get_config()
    api_key = config['DEFAULT'].get('api_key', None)
    api_secret = config['DEFAULT'].get('api_secret', None)
    conn = duckdb.connect()
    conn.execute("INSTALL httpfs;")  # Install if not already installed
    conn.execute("LOAD httpfs;")     # Load the extension for use
    conn.execute("""
    CREATE SECRET my_secret (
                 TYPE s3,
                 PROVIDER config,KEY_ID '{key}',
                 SECRET '{secret}',
                 REGION 'us-east-1');
                """.format(key=api_key,secret=api_secret))
    q = "SELECT * FROM read_csv('{uri}');".format(uri=uri)
    df = conn.execute(q).df()
    df = duckdb.query(query).df()
    end = time.time()
    click.echo(f"Query' executed in {end - start:.4f} seconds")
    print(tabulate(df, headers='keys', tablefmt='grid', showindex=False)) #psql, grid, plain, fancy_grid
    if out:
        df.to_csv(out)
        print(f'Data successfully written to file: {out}')
    return df

@cli.command()
@click.option('--bucket', prompt='Enter a S3 bucket name.', hide_input=True, help='Example: s3://osg-repo-scan-data/ -> "osg-repo-scan-data"')
def ls(bucket):
    config = get_config()
    api_key = config['DEFAULT'].get('api_key', None)
    api_secret = config['DEFAULT'].get('api_secret', None)
    client = boto3.client(
        's3',
        aws_access_key_id='{key}'.format(key=api_key),
        aws_secret_access_key='{secret}'.format(secret=api_secret)
    )
    try:
        response = client.list_objects_v2(Bucket=bucket)
        if 'Contents' in response:
            df = pd.DataFrame(response['Contents'])
            print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
        else:
            print("No objects found in the bucket.")
    except Exception as e:
        print(f"Error: {e}")