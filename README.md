# Oracle to Postgres Database Comparison Utility

This utility streamlines the process of comparing the schemas and code objects of Oracle and Postgres databases. This utility can be useful for heterogenous migrations from Oracle to Postgres or vice-versa to check whether all the objects i.e: PLSQL, tablec, indexes, views, columns, sequences are migrated. It leverages Google BigQuery for efficient data analysis and reporting.

## Key Features

* **Metadata Collection:**  Extracts comprehensive schema metadata (tables, views, functions, procedures, etc.) from Oracle and Postgres databases.
* **BigQuery Integration:** Seamlessly imports collected metadata into Google BigQuery for centralized analysis.
* **Detailed Comparison Reports:** Generates clear, text and html based reports highlighting differences in:
    * Object counts (tables, views, etc.)
    * Missing objects in either database
    * Discrepancies in PLSQL and plpgsql (procedures, functions)
    * Other customizable comparison metrics

## Prerequisites

* **Oracle Database Access:** Credentials for Oracle database.
* **Postgres Database Access:** Credentials for Postgres database.
* **Google Cloud Project:**  A Google Cloud project with BigQuery enabled.
* **Service Account:** A Google Cloud service account with BigQuery Data Editor and Job User roles.

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/samkaradag/oracle2postgres-schema-validator

2. **Set Up Environment:**
Install required Python packages:
pip install -r requirements.txt

Set environment variables (refer to config.py.example):
* ORACLE_CONN_STRING: Connection string for the Oracle database(s).
* GOOGLE_APPLICATION_CREDENTIALS: Use gcloud auth application-default login
* PROJECT_ID: Your Google Cloud project ID.
* DATASET_ID: The BigQuery dataset to use (created if it doesn't exist).

## Client requirements:

* Oracle client installed
* tns_names.ora file that includes the target db tns.
* python3
* Python dependencies installed (pip install -r requirements.txt)
* Google Cloud CLI (https://cloud.google.com/sdk/docs/install-sdk)
* Network connectivity to Oracle and Postgres instances and BigQuery APIs.

## Usage
* **Collect Metadata:**
    * Oracle Collect: 
        ```bash 
        cd collector/oracle-collector/
        ./collect_data.sh --connectionStr system/password@dbtns
        cp the zip files mentioned in the output under ../../importer/extracts/ folder

    * Postgres Collect: 
        ```bash 
        cd collector/pg-collector/
        python collect_pgsql.py ip_address db_name db_user passwd config.yaml
        cp extracted_data.zip ../../importer/extracts/

* **Import to BigQuery:**
    ```bash 
    cd ../../importer
    python importer.py --project_id your_project_id --dataset_id your_dataset_name 

You can specify an empty dataset otherwise dataset will be created if not exists.This command will unzip all the zip files underthe extracts folder.

* **Generate Reports:**
    ```bash 
    cd ../importer
    python reporter.py --project_id your_project_id --dataset_name your_dataset_name --table_name instances --format html

## Report Output
The generated reports will be saved in the reports directory.

## Customization
config.py: Adjust comparison parameters and reporting preferences.
generate_report.py: Extend or modify the types of comparisons and report formats.

## Contributing
Contributions are welcome! Please feel free to open issues or submit pull requests.

## License
This project is licensed under the Apache License.


