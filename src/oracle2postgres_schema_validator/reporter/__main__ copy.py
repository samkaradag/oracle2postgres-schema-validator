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
import pathlib

# Configuration
DEFAULT_PROJECT_ID = "your_project_id"
DEFAULT_DATASET_NAME = "your_dataset_name"
DEFAULT_TABLE_NAME = "instances"
DEFAULT_SCHEMA_NAME = "schema-compare"
CONFIG_FILE = "query_config.yaml"
QUERIES_FOLDER = "queries"



def replace_instance_id(query_file, schemas_to_compare, db_type):
    # Replace instance id placeholders in the queries
    # Replace schema filters
    # print (f"Schemas to compare:{schemas_to_compare}")
    if (schemas_to_compare):
        w_schema_filter = f'WHERE OWNER in ({schemas_to_compare})'
        a_schema_filter = f'AND a.OWNER in ({schemas_to_compare})'
        schema_filter = f'AND i1.OWNER in ({schemas_to_compare})'
    else:
        w_schema_filter = ''
        a_schema_filter = ''
        schema_filter = ''
    with open(f"{QUERIES_FOLDER}/{query_file}", "r") as f:
        query = f.read()
        query = query.replace('<instance_1_id>', instance_1_name)
        query = query.replace('<instance_2_id>', instance_2_name)
        query = query.replace('<w_schema_filter>', w_schema_filter)
        query = query.replace('<a_schema_filter>', a_schema_filter)
        query = query.replace('<schema_filter>', schema_filter)
        if db_type == "bigquery":
            query = query.replace('<dataset_name>', dataset_name)
        elif db_type == "postgres":
            query = query.replace('<dataset_name>', schema_name)
        return query

# Function to load and execute queries from files
def execute_queries(config, schemas_to_compare, db_type,project_id, cursor):
    results = []
    for section, query_file in config.items():
        print("Checking: ", section)
        with open(f"{QUERIES_FOLDER}/{query_file}", "r"):
            query = replace_instance_id(query_file, schemas_to_compare, db_type)
            results.append(execute_query(query, db_type,project_id, cursor))
    return results

def execute_query(query, db_type,project_id, cursor):
    if db_type == "bigquery":
        client = bigquery.Client(project=project_id)
        query_job = client.query(query)
        results = query_job.result()
        # Convert BigQuery Row objects to dictionaries
        results = [dict(row) for row in results]  # Convert to dictionaries
    elif db_type == "postgres":
        cursor.execute(query)
        headers = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        # Convert Postgres tuples to dictionaries (using headers from first tuple)
        if results:  # Check if results is not empty
            results = [dict(zip(headers, row)) for row in results]
    return results

# Function to generate text report
def generate_text_report(config, results, instance_1_name, instance_2_name):
    report = "## Database Comparison Report\n\n"

    for i, (section, query_file) in enumerate(config.items()):
        report += f"### {section}\n"

        table_data = results[i]

        if table_data:  # Check if result set is not empty
            report += tabulate(table_data, headers="keys", tablefmt="github") + "\n\n"
        else:
            report += "No results found.\n\n"

    return report

# Function to generate HTML report
def generate_html_report(config, results, instance_1_name, instance_2_name):
    report = """
    <!DOCTYPE html>
    <html>
    <head>
    <link rel="stylesheet" href="report.css">
    <title>Database Comparison Report</title>
    <style>
    body {
    font-family: sans-serif;
    }
    h2, h3 {
    margin-top: 2em;
    }
    table {
    border-collapse: collapse;
    width: 100%;
    }
    th, td {
    border: 1px solid #ddd;
    padding: 8px;
    }
    th {
    text-align: left;
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

    report += """
    </ul>
    """

    for i, (section, query_file) in enumerate(config.items()):
        report += f"<h3><a name='{section.replace(' ', '_')}'></a>{section}</h3>"

        table_data = results[i]

        if table_data:  # Check if result set is not empty
            report += "<table>\n<thead>\n<tr>\n"
            for header in table_data[0].keys():
                report += f"<th>{header}</th>\n"
            report += "</tr>\n</thead>\n<tbody>\n"
            for row in table_data:
                report += "<tr>\n"
                for value in row.values():
                    report += f"<td>{value}</td>\n"
                report += "</tr>\n"
            report += "</tbody>\n</table>\n\n"
        else:
            report += "<p>No results found.</p>\n\n"

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

def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description="Generate database comparison report.")
    parser.add_argument("--project_id", help="Google Cloud project ID.")
    parser.add_argument("--dataset_name", help="BigQuery dataset name.")
    parser.add_argument("--table_name", help="BigQuery table name.")
    parser.add_argument("--format", default="text", choices=["text", "html"], help="Report format (text or html).")
    parser.add_argument("--db_type", default="bigquery", choices=["bigquery", "postgres"], help="Database type.")
    parser.add_argument("--postgres_host", help="Postgres host.")
    parser.add_argument("--postgres_port", type=int, help="Postgres port.")
    parser.add_argument("--postgres_user", help="Postgres user.")
    parser.add_argument("--postgres_password", help="Postgres password.")
    parser.add_argument("--postgres_database", help="Postgres database name.")
    parser.add_argument("--schema_name", help="Postgres schema name.")
    parser.add_argument("--schemas_to_compare", help="Schemas to be compared.")
    args = parser.parse_args()

    # Get configuration from environment variables or command-line arguments
    project_id = args.project_id or os.environ.get("PROJECT_ID") or DEFAULT_PROJECT_ID
    dataset_name = args.dataset_name or os.environ.get("DATASET_NAME") or DEFAULT_DATASET_NAME
    table_name = args.table_name or os.environ.get("TABLE_NAME") or DEFAULT_TABLE_NAME
    schema_name = args.schema_name or os.environ.get("SCHEMA_NAME") or DEFAULT_SCHEMA_NAME
    schemas_to_compare = args.schemas_to_compare or os.environ.get("SCHEMAS_TO_COMPARE")
    if(schemas_to_compare):
        schemas_to_compare = schemas_to_compare.split(',')
        schemas_to_compare = [f"'{item.strip()}'" for item in schemas_to_compare]
        schemas_to_compare = ','.join(schemas_to_compare)

    report_format = args.format
    db_type = args.db_type

    # Initialize database connection
    if db_type == "bigquery":
        client = bigquery.Client(project=project_id)
    elif db_type == "postgres":
        postgres_host = args.postgres_host
        postgres_port = args.postgres_port
        postgres_user = args.postgres_user
        postgres_password = args.postgres_password
        postgres_database = args.postgres_database
        conn = psycopg2.connect(
            host=postgres_host,
            port=postgres_port,
            user=postgres_user,
            password=postgres_password,
            database=postgres_database,
        )
        cursor = conn.cursor()

    # Get instance names
    if db_type == "bigquery":
        instances = client.query("SELECT DISTINCT PKEY FROM " + dataset_name + "." + table_name).result()
        # Convert instances to a list
        instance_names = [row[0] for row in instances]
    elif db_type == "postgres":
        cursor.execute(f"SELECT DISTINCT PKEY FROM {schema_name}.{table_name}")
        instance_names = [row[0] for row in cursor.fetchall()]

    # Assign instance names
    if len(instance_names) >= 2:
        instance_1_name = instance_names[0]
        instance_2_name = instance_names[1]
        print("Instance 1:", instance_1_name)
        print("Instance 2:", instance_2_name)
    else:
        print("Not enough instances found in the table.")

    # Load configuration and execute queries
    script_dir = pathlib.Path(__file__).parent.resolve()
    # Join the script's directory path with the relative path to config.yaml
    config_file_path = script_dir / CONFIG_FILE  
    with open(config_file_path, 'r') as f:
        config = yaml.safe_load(f)
    
    results = execute_queries(config, schemas_to_compare, db_type, project_id, cursor)

    # Generate report based on format
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

    # Close postgres connection if used
    if db_type == "postgres":
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()