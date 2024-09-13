# Copyright 2024 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
import yaml
from google.cloud import bigquery
from tabulate import tabulate
import datetime
import psycopg2
import re


# Configuration
DEFAULT_PROJECT_ID = "your_project_id"
DEFAULT_DATASET_NAME = "your_dataset_name"
DEFAULT_TABLE_NAME = "instances"
DEFAULT_SCHEMA_NAME = "schema_compare"
CONFIG_FILE = "query_config.yaml"
QUERIES_FOLDER = "queries"

# Global variables for database connections
client = None  # BigQuery client
cursor = None  # Postgres cursor
conn = None   # Postgres connection

def get_script_path():
    """Returns the absolute path of the currently executing script."""
    return os.path.dirname(os.path.abspath(__file__))

def replace_instance_id(query_file, instance_1_name, instance_2_name, schemas_to_compare, dataset_name, schema_name):
    """Replaces placeholders in SQL queries."""
    with open(os.path.join(get_script_path(), QUERIES_FOLDER, query_file), "r") as f:
        query = f.read()
        query = query.replace('<instance_1_id>', instance_1_name)
        query = query.replace('<instance_2_id>', instance_2_name)
        
        if schemas_to_compare:
            query = query.replace('<w_schema_filter>', f'WHERE OWNER in ({schemas_to_compare})')
            query = query.replace('<a_schema_filter>', f'AND a.OWNER in ({schemas_to_compare})')
            query = query.replace('<schema_filter>', f'AND i1.OWNER in ({schemas_to_compare})')
        else:
            query = query.replace('<w_schema_filter>', '')
            query = query.replace('<a_schema_filter>', '')
            query = query.replace('<schema_filter>', '')
        
        if db_type == "bigquery":
            query = query.replace('<dataset_name>', dataset_name)
        elif db_type == "postgres":
            query = query.replace('<dataset_name>', schema_name)
        return query

def execute_queries(config, instance_1_name, instance_2_name, schemas_to_compare, dataset_name, schema_name):
    """Executes SQL queries from configuration."""
    results = []
    for section, query_file in config.items():
        print("Checking: ", section)
        query = replace_instance_id(query_file, instance_1_name, instance_2_name, schemas_to_compare, dataset_name, schema_name)
        results.append(execute_query(query))
    return results

def execute_query(query):
    """Executes a single SQL query."""
    global client, cursor
    if db_type == "bigquery":
        query_job = client.query(query)
        results = list(query_job.result())
    elif db_type == "postgres":
        cursor.execute(query)
        headers = [desc[0] for desc in cursor.description]
        results = [dict(zip(headers, row)) for row in cursor.fetchall()]
    return results

def generate_text_report(config, results, instance_1_name, instance_2_name):
    """Generates a text report."""
    report = "## Database Comparison Report\n\n"
    for i, (section, query_file) in enumerate(config.items()):
        report += f"### {section}\n"
        table_data = results[i]
        if table_data:
            report += tabulate(table_data, headers="keys", tablefmt="github") + "\n\n"
        else:
            report += "No results found.\n\n"
    return report

def generate_html_report(config, results, instance_1_name, instance_2_name):
    """Generates an HTML report."""
    report = """
    <!DOCTYPE html>
    <html>
    <head>
    <title>Database Comparison Report</title>
    <style>
    body {
        font-family: 'Arial', sans-serif;
        background-color: #f4f4f4;
        color: #333;
        line-height: 1.6;
        margin: 0;
        padding: 20px;
      }
      
      h2 {
        color: #2980b9;
        text-align: center;
        margin-bottom: 1em;
      }
      
      h3 {
        color: #3498db;
        margin-top: 2em;
        margin-bottom: 1em;
      }
      
      ul {
        list-style-type: none;
        padding: 0;
        margin: 0;
        text-align: center;
        margin-bottom: 2em;
      }
      
      li {
        display: inline-block;
        margin: 0 1em;
      }
      
      a {
        color: #2980b9;
        text-decoration: none;
      }
      
      a:hover {
        text-decoration: underline;
      }
      
      table {
        border-collapse: collapse;
        width: 100%;
        margin-bottom: 2em;
        background-color: #fff;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
      }
      
      th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
      }
      
      th {
        background-color: #f0f0f0;
        font-weight: bold;
      }
      
      tr:nth-child(even) {
        background-color: #f9f9f9;
      }
      
      tr:hover {
        background-color: #e0e0e0;
      }
      
      .missing {
        color: #c0392b;
        font-weight: bold;
      }
      
      .present {
        color: #2ecc71;
        font-weight: bold;
      }
      .back-to-top {
        position: fixed;
        bottom: 20px;
        right: 20px;
        display: none; /* Hidden by default */
        background-color: #007bff; /* Blue background */
        color: white;
        padding: 10px;
        border-radius: 50%;
        cursor: pointer;
    }
    .back-to-top:hover {
        background-color: #0056b3;
    }
    .back-to-top i { /* Style the arrow icon */
        font-size: 1.2em;
        line-height: 1;
    }
    </style>
    </head>
    <body>
    <h2>Database Comparison Report</h2>
    <ul>
    """
    for i, (section, query_file) in enumerate(config.items()):
        report += f"<li><a href='#{section.replace(' ', '_')}'>{section}</a></li>"

    report += "</ul>"

    for i, (section, query_file) in enumerate(config.items()):
        report += f"<h3><a name='{section.replace(' ', '_')}'></a>{section}</h3>"
        table_data = results[i]
        if table_data:
            report += "<table><thead><tr>"
            for header in table_data[0].keys():
                report += f"<th>{header}</th>"
            report += "</tr></thead><tbody>"
            for row in table_data:
                report += "<tr>"
                for value in row.values():
                    report += f"<td>{value}</td>"
                report += "</tr>"
            report += "</tbody></table>"
        else:
            report += "<p>No results found.</p>"

    report += """
    <button class="back-to-top"><i class="fas fa-arrow-up"></i></button>
    <script>
        // Get the button element
        const backToTopButton = document.querySelector(".back-to-top");

        // When the user scrolls down 20px from the top of the document, show the button
        window.onscroll = function() {
            if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
                backToTopButton.style.display = "block";
            } else {
                backToTopButton.style.display = "none";
            }
        };

        // When the user clicks on the button, scroll to the top of the document
        backToTopButton.addEventListener("click", function() {
            document.body.scrollTop = 0;
            document.documentElement.scrollTop = 0;
        });
    </script>
    </body>
    </html>
    """
    return report

def get_instance_names(dataset_name, schema_name, table_name):
    """Retrieves distinct instance names from the database."""
    global client, cursor
    if db_type == "bigquery":
        instances = client.query(f"SELECT DISTINCT PKEY FROM {dataset_name}.{table_name}").result()
        instance_names = [row[0] for row in instances]
    elif db_type == "postgres":
        cursor.execute(f"SELECT DISTINCT PKEY FROM {schema_name}.{table_name}")
        instance_names = [row[0] for row in cursor.fetchall()]
    return instance_names

def main():
    """Main function to execute the script."""
    global client, cursor, conn, db_type, project_id, dataset_name, table_name, schema_name, schemas_to_compare, report_format

    parser = argparse.ArgumentParser(description="Generate database comparison report.")
    parser.add_argument("--dataset_id", help="BigQuery dataset name.")
    parser.add_argument("--table_name", help="BigQuery table name.")
    parser.add_argument("--format", default="text", choices=["text", "html"], help="Report format (text or html).")
    parser.add_argument("--db_type", default="bigquery", choices=["bigquery", "postgres"], help="Database type.")
   
    group = parser.add_mutually_exclusive_group(required=True)  # Ensure one is chosen
    group.add_argument("--postgres_connection_string", help="Connection string for your PostgreSQL database. Use this if the staging area is a postgres db. format: 'postgresql://username:pwd@ip_address/db_name'.")
    group.add_argument("--postgres_host", help="Postgres host. Either use postgres_host or postgres_connection_string")
    group.add_argument("--project_id", help="Google Cloud project ID.")
    
    parser.add_argument("--postgres_port", type=int, help="Postgres port.")
    parser.add_argument("--postgres_user", help="Postgres user.")
    parser.add_argument("--postgres_password", help="Postgres password.")
    parser.add_argument("--postgres_database", help="Postgres database name.")
    parser.add_argument("--schema_name", help="Postgres schema name.")
    parser.add_argument("--schemas_to_compare", help="Schemas to be compared (comma-separated).")
    args = parser.parse_args()

    # Get configuration
    project_id = args.project_id or os.environ.get("PROJECT_ID") or DEFAULT_PROJECT_ID
    dataset_name = args.dataset_id or os.environ.get("DATASET_NAME") or DEFAULT_DATASET_NAME
    table_name = args.table_name or os.environ.get("TABLE_NAME") or DEFAULT_TABLE_NAME
    schema_name = args.schema_name or os.environ.get("SCHEMA_NAME") or DEFAULT_SCHEMA_NAME
    schemas_to_compare = args.schemas_to_compare or os.environ.get("SCHEMAS_TO_COMPARE")
    if schemas_to_compare:
        schemas_to_compare = ",".join([f"'{item.strip()}'" for item in schemas_to_compare.split(',')])
    report_format = args.format
    db_type = args.db_type

    # Initialize database connection
    if db_type == "bigquery":
        client = bigquery.Client(project=project_id)
    elif db_type == "postgres":
        if args.postgres_connection_string:
            match = re.match(r"postgresql://([^:]+):([^@]+)@([^/]+)/(.+)", args.postgres_connection_string)
            if match:
                postgres_user, postgres_password, postgres_host, postgres_database = match.groups()
                conn = psycopg2.connect(
                    host=postgres_host,
                    user=postgres_user,
                    password=postgres_password,
                    database=postgres_database,
                )
        elif args.postgres_host:
            conn = psycopg2.connect(
                host=args.postgres_host,
                port=args.postgres_port,
                user=args.postgres_user,
                password=args.postgres_password,
                database=args.postgres_database,
            )
        cursor = conn.cursor()

    # Get instance names
    instance_names = get_instance_names(dataset_name, schema_name, table_name)

    if len(instance_names) >= 2:
        instance_1_name, instance_2_name = instance_names[:2]
        print("Instance 1:", instance_1_name)
        print("Instance 2:", instance_2_name)

        # Load configuration and execute queries
        with open(os.path.join(get_script_path(), CONFIG_FILE), "r") as f:
            config = yaml.safe_load(f)
        results = execute_queries(config, instance_1_name, instance_2_name, schemas_to_compare, dataset_name, schema_name)

        # Generate report
        if report_format == "text":
            report = generate_text_report(config, results, instance_1_name, instance_2_name)
            print(report)
        elif report_format == "html":
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file_name = f"database_comparison_report_{timestamp}.html"
            report = generate_html_report(config, results, instance_1_name, instance_2_name)
            with open(report_file_name, "w") as f:
                f.write(report)
            print(f"HTML report generated: {report_file_name}")
    else:
        print("Not enough instances found in the table.")

    # Close database connection if necessary
    if db_type == "postgres":
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()