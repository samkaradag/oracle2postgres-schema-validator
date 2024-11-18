# Copyright 2024 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import argparse
import os
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import zipfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
from sqlalchemy import text
import shutil
import re
import sys
from google.cloud import secretmanager

def resolve_postgres_connection_string(connection_string):
    """
    Resolves the PostgreSQL connection string, replacing the password with a secret
    fetched from Google Secret Manager if specified.

    Args:
        connection_string (str): The PostgreSQL connection string.

    Returns:
        str: The updated PostgreSQL connection string.
    """
    if not connection_string:
        raise ValueError("Postgres connection string is required.")

    # Check if the password part is a GCP secret
    pattern = r"postgresql://(?P<user>[^:]+):(?P<password>[^@]+)@(?P<host>[^/]+)/(?P<db>.+)"
    match = re.match(pattern, connection_string)
    if not match:
        raise ValueError("Invalid PostgreSQL connection string format.")

    user, password, host, db = match.group("user"), match.group("password"), match.group("host"), match.group("db")

    # If the password is prefixed with "gcp-secret:", replace it with the secret value
    if password.startswith("gcp-secret:"):
        secret_name = password.split("gcp-secret:")[1]
        password = get_secret(secret_name)

    # Reconstruct the connection string
    return f"postgresql://{user}:{password}@{host}/{db}"

def get_secret(secret_name):
    """Fetches the secret value from Google Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is not set.")
    secret_path = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(name=secret_path)
    # print(response)
    return response.payload.data.decode("UTF-8")

def resolve_password(password_arg):
    """Resolves the password from the argument or Google Secret Manager."""
    if password_arg and password_arg.startswith("gcp-secret:"):
        secret_name = password_arg.split("gcp-secret:")[1]
        return get_secret(secret_name)
    return password_arg

# Base = declarative_base()


def unzip_all_files(directory_path):
    """
    Unzips all ZIP files found in the specified directory.

    Args:
        directory_path (str): The path to the directory containing the ZIP files.
    """
    for filename in os.listdir(directory_path):
        if filename.endswith('.zip'):
            zip_path = os.path.join(directory_path, filename)

            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(directory_path)  # Extract to same directory
                    print(f"Unzipped: {filename}")
            except zipfile.BadZipFile:
                print(f"Error: {filename} is not a valid ZIP file.")

def truncate_tables(client, project_id, dataset_id, csv_directory):
    """Truncates each unique table corresponding to CSV files in the directory."""
    truncated_tables = set()
    for filename in os.listdir(csv_directory):
        if filename.endswith(".csv"):
            table_name = filename.split("__")[1]
            if table_name not in truncated_tables:
                table_id = f"{project_id}.{dataset_id}.{table_name}"
                try:
                    truncate_query = f"DROP TABLE `{table_id}`"
                    query_job = client.query(truncate_query)
                    query_job.result()  # Wait for the truncation to complete
                    print(f"Dropped table {table_name}")
                except NotFound:
                    print(f"Table {table_id} not found. Skipping drop operation.")
                truncated_tables.add(table_name)  # Mark as truncated

def load_csv_files(client, project_id, dataset_id, csv_directory):
    """Loads CSV files into the corresponding BigQuery tables."""
    dataset_ref = client.dataset(dataset_id)
    for filename in os.listdir(csv_directory):
        if filename.endswith(".csv"):
            table_name = filename.split("__")[1]
            table_ref = dataset_ref.table(table_name)
            job_config = bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.CSV,
                skip_leading_rows=1,
                autodetect=True,
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            )
            file_path = os.path.join(csv_directory, filename)
            try:
                with open(file_path, "rb") as source_file:
                    load_job = client.load_table_from_file(source_file, table_ref, job_config=job_config)
                load_job.result()
            except Exception as e:
                print(e)
            print(f"Loaded {filename} into {table_name}")

def load_csv_to_bigquery(project_id, dataset_id, csv_directory, location="US"):
    """Main function to orchestrate the loading process."""
    client = bigquery.Client(project=project_id)

    # Dataset Creation (if not exists)
    try:
        client.get_dataset(client.dataset(dataset_id))
        print(f"Dataset {dataset_id} already exists.")
    except NotFound:
        print(f"Dataset {dataset_id} not found, creating it...")
        dataset = bigquery.Dataset(client.dataset(dataset_id))
        dataset.location = location
        dataset = client.create_dataset(dataset)
        print(f"Created dataset {dataset_id} in {location}.")

    # Truncate tables before loading
    truncate_tables(client, project_id, dataset_id, csv_directory)

    # Load CSV files
    load_csv_files(client, project_id, dataset_id, csv_directory)

def load_csv_to_postgres(csv_directory, postgres_connection_string, dbschema):
    """Loads CSV files into the specified PostgreSQL database."""
    # dbschema='schema_compare' # Searches left-to-right
    engine = create_engine(postgres_connection_string, connect_args={'options': '-csearch_path={}'.format(dbschema)})
    # engine = create_engine(postgres_connection_string)

    # Base.metadata.create_all(engine)

    # Create schema if it doesn't exist
    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {dbschema}"))
        # Retrieve a list of tables in the schema
        result = conn.execute(text(f"""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = '{dbschema}'
        """))
        tables = [row[0] for row in result.fetchall()]

        # Drop tables in a loop
        for table in tables:
            conn.execute(text(f"DROP TABLE IF EXISTS {dbschema}.{table}"))
            print(f"Dropping already existing table in schema {dbschema}.{table}")
        print(f"All tables in schema '{dbschema}' have been dropped.")


    Session = sessionmaker(bind=engine)
    session = Session()
    

    for filename in os.listdir(csv_directory):
        if filename.endswith(".csv") and (not  ("defines" in filename or "eoj" in filename)):
            file_path = os.path.join(csv_directory, filename)
            table_name = filename.split("__")[1]
            try:
                # Attempt to read with comma delimiter first
                df = pd.read_csv(file_path, sep='|')
                # # Convert columns to lowercase
                df.columns = df.columns.str.lower()
                # print(df)

                result = df.to_sql(table_name, engine, if_exists='append', index=False)
                print(f"Rows loaded: {result}")
                print(f"Loaded {filename} into PostgreSQL.")
            except Exception as e:
                print(e)

def delete_files_in_directory(directory):
    """Deletes all files in the specified directory."""

    archives_dir = os.path.join(directory, 'archives')
    
    # Create the 'archives' directory if it doesn't exist
    if not os.path.exists(archives_dir):
        os.makedirs(archives_dir)

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                if filename.endswith('.zip'):
                    # Move zip files to the 'archives' directory
                    archived_file = os.path.join(archives_dir,filename)
                    if os.path.isfile(archived_file):
                        os.remove(archived_file)
                    shutil.move(file_path, archives_dir)
                    print(f"Moved file: {filename} to archives")
                else:
                    # Delete other files
                    os.remove(file_path)
                    print(f"Deleted file: {filename}")
        except OSError as e:
            print(f"Error moving or deleting file {filename}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Load CSV files into BigQuery or PostgreSQL tables.")
    parser.add_argument("--project_id", help="Your Google Cloud Project ID (for BigQuery). Use this if the staging area is BigQuery.")
    parser.add_argument("--dataset_id", help="The BigQuery dataset name. Use this if the staging area is BigQuery.")
    parser.add_argument("--csv_directory", default="extracts", help="Directory containing CSV files.")
    parser.add_argument("--zip_directory", default="extracts", help="Directory containing ZIP files.")
    parser.add_argument("--location", default="US", help="Geographic location for the dataset (default: US). Use this if the staging area is BigQuery.")
    parser.add_argument("--postgres_connection_string", help="Connection string for your PostgreSQL database. Use this if the staging area is a postgres db. format: 'postgresql://username:pwd@ip_address/db_name'.")
    parser.add_argument("--schema", default="schema_compare",help="Schema for your PostgreSQL database. Use this if the staging area is a postgres db.")
    
    args = parser.parse_args()
    # postgres_connection_string = resolve_password(args.postgres_connection_string)

     # Resolve the PostgreSQL connection string, replacing the password with the GCP secret if needed
    postgres_connection_string = resolve_postgres_connection_string(args.postgres_connection_string)

    unzip_all_files(args.zip_directory)

    if args.project_id and args.dataset_id:
        load_csv_to_bigquery(args.project_id, args.dataset_id, args.csv_directory, args.location)

    if args.postgres_connection_string:
        load_csv_to_postgres(args.csv_directory, postgres_connection_string, args.schema)

    # Delete files after successful import
    delete_files_in_directory(args.csv_directory)

if __name__ == "__main__":
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
    # main()