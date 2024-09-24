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


def main():
    """Main function for the schema comparison utility."""
    parser = argparse.ArgumentParser(description='Oracle to Postgres Database Comparison Utility')

    # Oracle arguments
    parser.add_argument('--oracle_host', required=True, help='Oracle database hostname')
    parser.add_argument('--oracle_user', required=True, help='Oracle database username')
    parser.add_argument('--oracle_password', required=True, help='Oracle database password')
    parser.add_argument('--oracle_port', default='1521', type=str, help='Oracle database port')
    parser.add_argument('--oracle_service', help='Oracle database service name (optional)')
    parser.add_argument('--oracle_view_type', default='user', choices=['user', 'all'], help='Type of views to collect (user or all)')

    # Postgres arguments
    parser.add_argument('--postgres_host', required=True, help='Postgres database hostname')
    parser.add_argument('--postgres_database', required=True, help='Postgres database name')
    parser.add_argument('--postgres_user', required=True, help='Postgres database username')
    parser.add_argument('--postgres_password', required=True, help='Postgres database password')
    parser.add_argument('--postgres_port', default='5432', type=int, help='Postgres database port') 

    # Staging Database 
   
    group = parser.add_mutually_exclusive_group(required=True)  # Ensure one is chosen
    group.add_argument("--staging_project_id", help="Your Google Cloud Project ID (for BigQuery). Use this if the staging area is BigQuery.")
    group.add_argument("--staging_postgres_connection_string", help="Connection string for your PostgreSQL database. Use this if the staging area is a postgres db. format: 'postgresql://username:pwd@ip_address/db_name'.")
    
    # Common import arguments
    parser.add_argument("--staging_dataset_id", help="The BigQuery dataset name. Use this if the staging area is BigQuery.")
    parser.add_argument("--staging_location", default="US", help="Geographic location for the dataset (default: US). Use this if the staging area is BigQuery.")
    parser.add_argument("--staging_schema", default="schema_compare",help="Schema for your PostgreSQL database. Use this if the staging area is a postgres db.")
  

    # Report options
    parser.add_argument('--schemas_to_compare', help='Comma-separated list of schemas to compare')
    parser.add_argument('--format', default='html', choices=['html', 'text'], help='Report output format')

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("Extracting Oracle metadata...")
    # Call oracollector
    subprocess.run(["python", "-m", "oracollector", "--user", args.oracle_user, "--password", args.oracle_password,
                      "--host", args.oracle_host, "--port", args.oracle_port, "--service", args.oracle_service, 
                      "--view_type", args.oracle_view_type])
    print("Extracting Postgres metadata...")
    
    # Call pgcollector
    subprocess.run(["python", "-m", "pgcollector", "--host", args.postgres_host, "--database", args.postgres_database,
                      "--user", args.postgres_user, "--password", args.postgres_password])
    print("Loading metadata into staging area...")
    
    # Call importer
    if args.staging_project_id:
        subprocess.run(["python", "-m", "importer", "--project_id", args.staging_project_id, "--dataset_id", args.staging_dataset_id])
    elif args.staging_postgres_connection_string:
        subprocess.run(["python", "-m", "importer", "--postgres_connection_string", args.staging_postgres_connection_string,
                      "--schema", args.staging_schema])
    else:
        logging.error('Please specify either staging_project_id and staging_dataset_id for BigQuery or staging_postgres_connection_string for Postgres')
        return
    print("Generating the comparison report...")
    
    # Call reporter
    if args.staging_project_id:
        subprocess.run(["python", "-m", "reporter", "--db_type", "bigquery", "--project_id", args.staging_project_id,
                      "--dataset_id", args.staging_dataset_id, "--schemas_to_compare", args.schemas_to_compare or "", "--format", args.format])
    elif args.staging_postgres_connection_string:
        subprocess.run(["python", "-m", "reporter", "--db_type", "postgres", "--postgres_connection_string", args.staging_postgres_connection_string,
                      "--schema_name", args.staging_schema, "--schemas_to_compare", args.schemas_to_compare or "", "--format", args.format])
    else:
        logging.error('Please specify either project_id and dataset_id for BigQuery or connection_string for Postgres')
        return

if __name__ == '__main__':
    main()