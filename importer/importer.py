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
                except NotFound as e:
                    print(f"Table {table_id} not found. Skipping drop operation.")
                truncated_tables.add(table_name)  # Mark as truncated

def load_csv_files(client, project_id, dataset_id, csv_directory):
    """Loads CSV files into the corresponding BigQuery tables."""
    dataset_ref = client.dataset(dataset_id)
    for filename in os.listdir(csv_directory):
        if filename.endswith(".csv"):
            table_name = filename.split("__")[1]
            table_id = f"{project_id}.{dataset_id}.{table_name}"
            table_ref = dataset_ref.table(table_name)
            job_config = bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.CSV,
                skip_leading_rows=1,
                autodetect=True,
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            )
            file_path = os.path.join(csv_directory, filename)
            with open(file_path, "rb") as source_file:
                load_job = client.load_table_from_file(source_file, table_ref, job_config=job_config)
            load_job.result()
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load CSV files into BigQuery tables.")
    parser.add_argument("--project_id", help="Your Google Cloud Project ID.")
    parser.add_argument("--dataset_id", help="The BigQuery dataset name.")
    parser.add_argument("--csv_directory", default="./extracts", help="Directory containing CSV files.")
    parser.add_argument("--zip_directory", default="./extracts", help="Directory containing CSV files.")
    parser.add_argument("--location", default="US", help="Geographic location for the dataset (default: US)")
    args = parser.parse_args()

    unzip_all_files(args.zip_directory)

    load_csv_to_bigquery(args.project_id, args.dataset_id, args.csv_directory, args.location)
