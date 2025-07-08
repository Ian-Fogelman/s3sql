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
from pathlib import Path
from importlib.metadata import version

class S3SQLClient:
    def __init__(self):
        self.config_dir = os.path.expanduser("~/s3sql")
        self.config_file = os.path.join(self.config_dir, "credentials")
        os.makedirs(self.config_dir, exist_ok=True)
        self.config = self.get_config()

    def get_config(self):
        """Load the config file."""
        config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            config.read(self.config_file)
        if 'DEFAULT' not in config:
            config['DEFAULT'] = {}
        return config

    def save_config(self):
        """Save the config file."""
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def mask_string(self, input_string):
        """Mask sensitive strings, showing only the first 3 and last 3 characters."""
        if len(input_string) <= 6:
            return "*" * len(input_string)
        return input_string[:3] + "*" * (len(input_string) - 6) + input_string[-3:]

    def detect_file(self, ext):
        """Detect file type and return appropriate read method."""
        file_types = {
            ".csv": {'ext': '.csv', 'read_method': 'read_csv'},
            ".json": {'ext': '.json', 'read_method': 'read_json'},
            ".parquet": {'ext': '.parquet', 'read_method': 'read_parquet'}
        }
        return file_types.get(ext, "Read file type not supported, please try again with either a .csv, .json, or .parquet file extension.")

    def get_version(self):
        """Get the version of the s3sql package."""
        return version("s3sql")

    def set_key(self, api_key):
        """Set and persist the access key."""
        self.config['DEFAULT']['api_key'] = api_key
        self.save_config()
        click.echo("API key saved successfully!")

    def get_key(self):
        """Retrieve the stored API key."""
        api_key = self.config['DEFAULT'].get('api_key', None)
        if api_key:
            masked_key = self.mask_string(api_key)
            msg = f"Stored API key: {masked_key}"
            click.echo(msg)
            return msg
        else:
            msg = "No API key set. Use 's3sql set-key' to set one."
            click.echo(msg)
            return msg

    def set_secret(self, api_secret):
        """Set and persist the secret key."""
        self.config['DEFAULT']['api_secret'] = api_secret
        self.save_config()
        click.echo("API secret saved successfully!")

    def get_secret(self):
        """Retrieve the stored secret key."""
        api_secret = self.config['DEFAULT'].get('api_secret', None)
        if api_secret:
            masked_secret = self.mask_string(api_secret)
            msg = f"Stored API secret: {masked_secret}"
            click.echo(msg)
            return msg
        else:
            msg = "No API secret set. Use 's3sql set-secret' to set one."
            click.echo(msg)
            return msg

    def query(self, uri, sql, out=None):
        """Query an object stored in S3."""
        start = time.time()
        api_key = self.config['DEFAULT'].get('api_key', None)
        api_secret = self.config['DEFAULT'].get('api_secret', None)
        conn = duckdb.connect()
        conn.execute("INSTALL httpfs;")
        conn.execute("LOAD httpfs;")
        conn.execute("""
        CREATE SECRET my_secret (
                     TYPE s3,
                     PROVIDER config,
                     KEY_ID '{key}',
                     SECRET '{secret}',
                     REGION 'us-east-1');
                    """.format(key=api_key, secret=api_secret))
        ext = Path(uri).suffix
        details = self.detect_file(ext)
        if isinstance(details, str):
            click.echo(details)
            return
        ext = details['ext']
        rm = details['read_method']
        q = "SELECT * FROM {read}('{uri}');".format(read=rm, uri=uri)
        df = conn.execute(q).df()
        df = duckdb.query(sql).df()
        end = time.time()
        click.echo(f"Query executed in {end - start:.4f} seconds")
        click.echo(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
        if out:
            out_ext = Path(out).suffix
            if out_ext == '.csv':
                df.to_csv(out)
                click.echo(f'Data successfully written to file: {out}')
            elif out_ext == '.json':
                df.to_json(out)
                click.echo(f'Data successfully written to file: {out}')
            elif out_ext == '.parquet':
                df.to_parquet(out)
                click.echo(f'Data successfully written to file: {out}')
            else:
                click.echo("Output file type not supported, please try again with either a .csv, .json, or .parquet file extension.")
        return df

    def list_bucket(self, bucket):
        """List objects in an S3 bucket."""
        api_key = self.config['DEFAULT'].get('api_key', None)
        api_secret = self.config['DEFAULT'].get('api_secret', None)
        client = boto3.client(
            's3',
            aws_access_key_id=api_key,
            aws_secret_access_key=api_secret
        )
        try:
            response = client.list_objects_v2(Bucket=bucket)
            if 'Contents' in response:
                df = pd.DataFrame(response['Contents'])
                click.echo(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
            else:
                click.echo("No objects found in the bucket.")
        except Exception as e:
            click.echo(f"Error: {e}")

@click.group()
@click.version_option(version=S3SQLClient().get_version())
def cli():
    """The S3SQL CLI, the simplest way to query your S3 objects."""
    pass

@cli.command()
@click.option('--api-key', prompt='Enter API key', hide_input=True, help='Set the API key.')
def set_key(api_key):
    """Set and persist the access key."""
    client = S3SQLClient()
    client.set_key(api_key)

@cli.command()
def get_key():
    """Retrieve the stored API key."""
    client = S3SQLClient()
    client.get_key()

@cli.command()
@click.option('--api-secret', prompt='Enter secret key', hide_input=True, help='Set the secret key.')
def set_secret(api_secret):
    """Set and persist the secret key."""
    client = S3SQLClient()
    client.set_secret(api_secret)

@cli.command()
def get_secret():
    """Retrieve the stored secret key."""
    client = S3SQLClient()
    client.get_secret()

@cli.command()
@click.option('--uri', prompt='Enter a quoted S3 URI for the object', hide_input=True, help='Example: s3://osg-repo-scan-data/branches.csv')
@click.option('--sql', prompt='Enter a quoted SQL query for the data returned from the object', hide_input=True, help='Example: SELECT * FROM df WHERE ID > 1')
@click.option('--out', default=None, hide_input=True, help='Example: output.csv')
def query(uri, sql, out):
    """Query an object stored in S3."""
    client = S3SQLClient()
    client.query(uri, sql, out)

@cli.command()
@click.option('--bucket', prompt='Enter a S3 bucket name.', hide_input=True, help='Example: s3://osg-repo-scan-data/ -> "osg-repo-scan-data"')
def ls(bucket):
    """List bucket objects."""
    client = S3SQLClient()
    client.list_bucket(bucket)

if __name__ == '__main__':
    cli()