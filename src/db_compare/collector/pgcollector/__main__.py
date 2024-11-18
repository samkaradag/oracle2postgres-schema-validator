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

import yaml
import psycopg2
import csv
import os
import zipfile
import argparse
import pathlib
import re
import sys
from google.cloud import secretmanager


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

def extract_queries_to_csv(db_host, db_name, db_user, db_password, config_file):
    """
    Extracts data from a Postgres database based on queries and connection settings
    provided as input arguments. Writes each query's output to a separate CSV file,
    and then zips all the CSV files.

    Args:
        db_host: The hostname of the Postgres database.
        db_name: The name of the Postgres database.
        db_user: The username for the Postgres database.
        db_password: The password for the Postgres database.
        config_file: Path to the YAML configuration file.
    """
    # Load Configuration (Handle missing file gracefully)
    # Get the absolute path to the script's directory
    script_dir = pathlib.Path(__file__).parent.resolve()
    # Join the script's directory path with the relative path to config.yaml
    config_file_path = script_dir / config_file  
    with open(config_file_path, 'r') as f:
        config = yaml.safe_load(f)

    # Connect to the database
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )

    # Create a cursor object
    cur = conn.cursor()

    # Create the "extracts" directory if it doesn't exist
    extracts_dir = os.path.join("./", "extracts")
    os.makedirs(extracts_dir, exist_ok=True)
    db_host_alpha = ''.join(c for c in db_host if c.isalpha()) 
    # Loop through each query in the configuration file
    for i, query in enumerate(config['queries']):
        # Execute the query
        sql = query["query"].replace("<db-name>",db_host_alpha)
        
        print(f"Extracting: {query['name']}")
        cur.execute(sql)

        # Fetch all rows from the query result
        rows = cur.fetchall()

        # Get the query name from the YAML (assuming it's a key in the query dict)
        query_name = config['queries'][i].get('name', f"query_{i+1}")

        # Create a CSV file for the query results
        csv_file = os.path.join(extracts_dir, f"{query_name}.csv")

        with open(csv_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter='|')

            # Write the column headers (optional, can be customized)
            writer.writerow([desc[0] for desc in cur.description])

            # Write the data rows
            writer.writerows(rows)

    # # Zip all the CSV files
    # zip_file = f"pg-extract-{db_host}.zip"
    # with zipfile.ZipFile(zip_file, 'w') as z:
    #     for filename in os.listdir():
    #         if filename.endswith(".csv"):
    #             z.write(filename)
    #             os.remove(filename)

    # Delete existing files starting with "orcl-extract-"
    for filename in os.listdir(extracts_dir):
        if filename.startswith("pg-extract-"):
            os.remove(os.path.join(extracts_dir, filename))


    # Zip all the CSV files in the "extracts" directory
    zip_file = os.path.join(extracts_dir, f"pg-extract-{db_host}.zip")
    with zipfile.ZipFile(zip_file, 'w') as z:
        for filename in os.listdir(extracts_dir):
            if filename.endswith(".csv"):
                z.write(os.path.join(extracts_dir, filename), filename)
                os.remove(os.path.join(extracts_dir, filename))

    # Close the cursor and connection
    cur.close()
    conn.close()

    print(f"Extracted data and saved to {zip_file}")

def main():
    parser = argparse.ArgumentParser(description='Extract data from a Postgres database')
    parser.add_argument('--host', type=str, help='Hostname of the Postgres database')
    parser.add_argument('--database', type=str, help='Name of the Postgres database')
    parser.add_argument('--user', type=str, help='Username for the Postgres database')
    parser.add_argument('--password', type=str, help='Password for the Postgres database')
    # parser.add_argument('config_file', type=str, help='Path to the YAML configuration file')
    args = parser.parse_args()

    password = resolve_password(args.password)

    extract_queries_to_csv(args.host, args.database, args.user, password,"./config.yaml")

if __name__ == "__main__":
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
    # main()