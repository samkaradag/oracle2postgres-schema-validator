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
import oracledb
import csv
import os
import zipfile
import argparse
import pathlib

def extract_queries_to_csv(db_user, db_password, db_host, db_port, db_service, config_file, view_type='all', protocol='tcp'):
    """
    Extracts data from an Oracle database based on queries and connection settings
    provided as input arguments. Writes each query's output to a separate CSV file,
    and then zips all the CSV files.

    Args:
        db_user: The username for the Oracle database.
        db_password: The password for the Oracle database.
        db_host: The hostname of the Oracle database.
        db_port: The port number of the Oracle database.
        db_service: The service name of the Oracle database.
        config_file: Path to the YAML configuration file.
    """

    # Load Configuration (Handle missing file gracefully)
    # Get the absolute path to the script's directory
    script_dir = pathlib.Path(__file__).parent.resolve()
    # Join the script's directory path with the relative path to config.yaml
    config_file_path = script_dir / config_file  
    with open(config_file_path, 'r') as f:
        config = yaml.safe_load(f)

    # Construct the connection string
    dsn = oracledb.makedsn(host=db_host, port=db_port, service_name=db_service)

    # Connect to the database
    conn = oracledb.connect(
        user=db_user,
        password=db_password,
        dsn=dsn,
        protocol=protocol
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
        sql = query["query"].replace("<view_type>", view_type).replace("<db-name>",db_host_alpha)
        if (view_type == 'user'):
            sql = sql.replace('owner,\n', "'" + db_user + "' as owner,\n").replace("WHERE owner NOT IN ('SYS', 'SYSTEM')\n","").replace("GROUP BY owner, ",f"GROUP BY '{db_user}', ")
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

    # Delete existing files starting with "orcl-extract-"
    for filename in os.listdir(extracts_dir):
        if filename.startswith("orcl-extract-"):
            os.remove(os.path.join(extracts_dir, filename))


    # Zip all the CSV files in the "extracts" directory
    zip_file = os.path.join(extracts_dir, f"orcl-extract-{db_host}.zip")
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
    parser = argparse.ArgumentParser(description='Extract data from an Oracle database')
    parser.add_argument('--user', type=str, help='Username for the Oracle database')
    parser.add_argument('--password', type=str, help='Password for the Oracle database')
    parser.add_argument('--host', type=str, help='Hostname of the Oracle database')
    parser.add_argument('--port', default='1521', type=str, help='Port number of the Oracle database')
    parser.add_argument('--service', type=str, help='Service name of the Oracle database')
    parser.add_argument('--view_type', type=str, help='Type of catalog views either "all or "user"')
    parser.add_argument('--protocol', default='tcp', type=str, help='Protocol either "tcp" or "tcps"')
    # parser.add_argument('config_file', type=str, help='Path to the YAML configuration file')
    args = parser.parse_args()

    extract_queries_to_csv(args.user, args.password, args.host, args.port, args.service, "./config_oracle.yaml", args.view_type, args.protocol)

if __name__ == "__main__":
    main()
