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
import logging
import os
import subprocess
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

def main():
    """Main function for the schema comparison utility."""
    parser = argparse.ArgumentParser(description='Oracle to Postgres Database Comparison Utility')

    # Comparison Mode
    mode_group = parser.add_argument_group('Comparison Mode', 'Choose the database comparison mode.')
    mode_options = mode_group.add_mutually_exclusive_group(required=True)
    mode_options.add_argument('--oracle_to_postgres', action='store_true', help='Compare Oracle to Postgres')
    mode_options.add_argument('--oracle_to_oracle', action='store_true', help='Compare Oracle to Oracle')
    mode_options.add_argument('--postgres_to_postgres', action='store_true', help='Compare Postgres to Postgres')


    # Oracle arguments (required for oracle comparisons)
    oracle_group = parser.add_argument_group('Oracle Arguments', 'Provide these if comparing Oracle databases.')
    oracle_group.add_argument('--oracle_host1', help='Oracle database 1 hostname')
    oracle_group.add_argument('--oracle_user1', help='Oracle database 1 username')
    oracle_group.add_argument('--oracle_password1', help='Oracle database 1 password or Google Secret Manager name for Oracle database password (e.g., gcp-secret:my-secret)')
    oracle_group.add_argument('--oracle_port1', default='1521', type=str, help='Oracle database 1 port')
    oracle_group.add_argument('--oracle_service1', help='Oracle database 1 service name (optional)')
    oracle_group.add_argument('--oracle_protocol1',default='tcp', help='Oracle database 1 protocol (tcp or tcps) (optional)')
    oracle_group.add_argument('--oracle_tns1', help='TNS name (alias) (alternative to --host, --port, --service)')
    oracle_group.add_argument('--oracle_tns_path1', help='Path to tnsnames.ora file (alternative to --host, --port, --service)')
    oracle_group.add_argument('--oracle_host2', help='Oracle database 2 hostname (required for oracle_to_oracle)')
    oracle_group.add_argument('--oracle_user2', help='Oracle database 2 username (required for oracle_to_oracle)')
    oracle_group.add_argument('--oracle_password2', help='Oracle database 2 password (required for oracle_to_oracle) or Google Secret Manager name (e.g., gcp-secret:my-secret)')
    oracle_group.add_argument('--oracle_port2', default='1521', type=str, help='Oracle database 2 port (required for oracle_to_oracle)')
    oracle_group.add_argument('--oracle_service2', help='Oracle database 2 service name (optional, for oracle_to_oracle)')
    oracle_group.add_argument('--oracle_tns2', help='TNS name (alias) (alternative to --host, --port, --service)')
    oracle_group.add_argument('--oracle_tns_path2', help='Path to tnsnames.ora file (alternative to --host, --port, --service)')
    oracle_group.add_argument('--oracle_protocol2' , default='tcp' , help='Oracle database 2 protocol (tcp or tcps) (optional)')
    oracle_group.add_argument('--oracle_view_type', default='dba', choices=['user', 'all', 'dba'], help='Type of views to collect (user or all or dba)')



    # Postgres arguments (required for postgres comparisons)
    postgres_group = parser.add_argument_group('Postgres Arguments', 'Provide these if comparing Postgres databases.')
    postgres_group.add_argument('--postgres_host1', help='Postgres database 1 hostname')
    postgres_group.add_argument('--postgres_database1', help='Postgres database 1 name')
    postgres_group.add_argument('--postgres_user1', help='Postgres database 1 username')
    postgres_group.add_argument('--postgres_password1', help='Postgres database 1 password or Google Secret Manager name for Postgres database (e.g., gcp-secret:my-secret)')
    postgres_group.add_argument('--postgres_port1', default='5432', type=int, help='Postgres database 1 port')
    postgres_group.add_argument('--postgres_host2',  help='Postgres database 2 hostname (required for postgres_to_postgres)')
    postgres_group.add_argument('--postgres_database2', help='Postgres database 2 name (required for postgres_to_postgres)')
    postgres_group.add_argument('--postgres_user2', help='Postgres database 2 username (required for postgres_to_postgres)')
    postgres_group.add_argument('--postgres_password2', help='Postgres database 2 password (required for postgres_to_postgres) or Google Secret Manager name (e.g., gcp-secret:my-secret)')
    postgres_group.add_argument('--postgres_port2', default='5432', type=int, help='Postgres database 2 port (required for postgres_to_postgres)')


    # # Oracle arguments
    # parser.add_argument('--oracle_host', required=True, help='Oracle database hostname')
    # parser.add_argument('--oracle_user', required=True, help='Oracle database username')
    # parser.add_argument('--oracle_password', required=True, help='Oracle database password')
    # parser.add_argument('--oracle_port', default='1521', type=str, help='Oracle database port')
    # parser.add_argument('--oracle_service', help='Oracle database service name (optional)')
    # parser.add_argument('--oracle_view_type', default='user', choices=['user', 'all'], help='Type of views to collect (user or all)')

    # # Postgres arguments
    # parser.add_argument('--postgres_host', required=True, help='Postgres database hostname')
    # parser.add_argument('--postgres_database', required=True, help='Postgres database name')
    # parser.add_argument('--postgres_user', required=True, help='Postgres database username')
    # parser.add_argument('--postgres_password', required=True, help='Postgres database password')
    # parser.add_argument('--postgres_port', default='5432', type=int, help='Postgres database port') 

    # Staging Database 
   
    group = parser.add_mutually_exclusive_group(required=True)  # Ensure one is chosen
    group.add_argument("--staging_project_id", help="Your Google Cloud Project ID (for BigQuery). Use this if the staging area is BigQuery.")
    group.add_argument("--staging_postgres_connection_string", help="Connection string for your PostgreSQL database. Use this if the staging area is a postgres db. format: 'postgresql://username:pwd@ip_address/db_name' or Google Secret Manager name containing the full connection string (e.g., gcp-secret:my-secret).")
    
    # Common import arguments
    parser.add_argument("--staging_dataset_id", help="The BigQuery dataset name. Use this if the staging area is BigQuery.")
    parser.add_argument("--staging_location", default="US", help="Geographic location for the dataset (default: US). Use this if the staging area is BigQuery.")
    parser.add_argument("--staging_schema", default="schema_compare",help="Schema for your PostgreSQL database. Use this if the staging area is a postgres db.")
  

    # Report options
    parser.add_argument('--schemas_to_compare', help='Comma-separated list of schemas to compare')
    parser.add_argument("--schema_mapping", help="Schema mapping i.e: 'SCHEMA_1/SCHEMA_2' (Only one mapping is allowed).")
    
    parser.add_argument('--format', default='html', choices=['html', 'text'], help='Report output format')

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Resolve passwords using Google Secret Manager if needed
    oracle_password1 = resolve_password(args.oracle_password1)
    # oracle_password2 = resolve_password(args.oracle_password2) if args.oracle_password2 else None
    postgres_password1 = resolve_password(args.postgres_password1)
    # postgres_password2 = resolve_password(args.postgres_password2) if args.postgres_password2 else None
    staging_postgres_connection_string = resolve_password(args.staging_postgres_connection_string)
    
    if args.oracle_to_postgres:
        print("Extracting Oracle metadata...")
        # Call oracollector
        for i in [1]:
            if getattr(args, f"oracle_tns{i}"):
                arguments = ["--tns", getattr(args, f"oracle_tns{i}"), "--tns_path", getattr(args, f"oracle_tns_path{i}")]
            else:
                arguments = ["--host", getattr(args, f"oracle_host{i}"), "--port", str(getattr(args, f"oracle_port{i}")),  #Convert port to string
                            "--service", getattr(args, f"oracle_service{i}")] # Removed redundant --protocol

            command = ["python", "-m", "oracollector", "--user", args.oracle_user1, "--password", oracle_password1]
            command.extend(arguments)  # Add arguments to the main command list
            command.extend(["--view_type", args.oracle_view_type])

            try:
                subprocess.run(command, check=True) #check=True raises exception on error, capture_output for better error messages
                print("Oracle metadata extraction successful.")
            except subprocess.CalledProcessError as e:
                print(f"Error extracting Oracle metadata: {e.stderr}")
                return

        print("Extracting Postgres metadata...")
        
        # Call pgcollector
        subprocess.run(["python", "-m", "pgcollector", "--host", args.postgres_host1, "--database", args.postgres_database1,
                        "--user", args.postgres_user1, "--password", postgres_password1], check=True)
        
    
    elif args.oracle_to_oracle:
        #  Oracle to Oracle comparison
        for i in [1, 2]:
            try:
                if getattr(args, f"oracle_tns{i}"):
                    arguments = ["--tns", getattr(args, f"oracle_tns{i}"), "--tns_path", getattr(args, f"oracle_tns_path{i}")]
                else:
                    arguments = ["--host", getattr(args, f"oracle_host{i}"), "--port", str(getattr(args, f"oracle_port{i}")), "--service", getattr(args, f"oracle_service{i}")] # Removed redundant --protocol
                oracle_password = resolve_password(getattr(args, f"oracle_password{i}"))
                
                command = ["python", "-m", "oracollector",
                        "--user", getattr(args, f"oracle_user{i}"),
                        "--password", oracle_password,
                        "--view_type", args.oracle_view_type]
                command.extend(arguments)

                result = subprocess.run(command, check=True)
                # Print the captured output
                print(result.stdout)
                # print(f"Oracle metadata extraction successful for connection {i}.")

            except AttributeError as e:
                print(f"Missing argument for connection {i}: {e}")
                return
            except subprocess.CalledProcessError as e:
                print(f"Error extracting Oracle metadata for connection {i}: {e.stderr}")
                return

    elif args.postgres_to_postgres:
         # Postgres to Postgres comparison
        for i in [1, 2]:
            pg_password = resolve_password(getattr(args, f"postgres_password{i}"))
            subprocess.run(["python", "-m", "pgcollector", "--host", getattr(args, f"postgres_host{i}"), "--database", getattr(args, f"postgres_database{i}"),
                          "--user", getattr(args, f"postgres_user{i}"), "--password", pg_password, "--port", getattr(args, f"postgres_port{i}")], check=True)
    
    print("Loading metadata into staging area...")
    # Call importer
    if args.staging_project_id:
        subprocess.run(["python", "-m", "importer", "--project_id", args.staging_project_id, "--dataset_id", args.staging_dataset_id], check=True)
    elif args.staging_postgres_connection_string:
        subprocess.run(["python", "-m", "importer", "--postgres_connection_string", staging_postgres_connection_string,
                      "--schema", args.staging_schema], check=True)
    else:
        logging.error('Please specify either staging_project_id and staging_dataset_id for BigQuery or staging_postgres_connection_string for Postgres')
        return
    print("Generating the comparison report...")
    
    # Call reporter
    if args.staging_project_id:
        subprocess.run(["python", "-m", "reporter", "--db_type", "bigquery", "--project_id", args.staging_project_id,
                      "--dataset_id", args.staging_dataset_id, "--schemas_to_compare", args.schemas_to_compare or "", "--schema_mapping", args.schema_mapping or "", "--format", args.format], check=True)
    elif args.staging_postgres_connection_string:
        subprocess.run(["python", "-m", "reporter", "--db_type", "postgres", "--postgres_connection_string", staging_postgres_connection_string,
                      "--schema_name", args.staging_schema, "--schemas_to_compare", args.schemas_to_compare or "", "--schema_mapping", args.schema_mapping or "", "--format", args.format], check=True)
    else:
        logging.error('Please specify either project_id and dataset_id for BigQuery or connection_string for Postgres')
        return

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
    # main()