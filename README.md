# Oracle to Postgres Database Comparison Utility

This utility streamlines the process of comparing the schemas and code objects of Oracle and Postgres databases. This utility can be useful for heterogenous migrations from Oracle to Postgres or vice-versa to check whether all the objects i.e: PLSQL, tablec, indexes, views, columns, sequences are migrated. It can leverage Google BigQuery or any Postgres database as a staging environment for efficient data analysis and reporting.

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
* **Staging Database** BigQuery or Postgres database is needed to stage extracted metadata
    * BigQuery as Staging:
        * **Google Cloud Project:**  A Google Cloud project with BigQuery enabled.
        * **Service Account:** A Google Cloud service account with BigQuery Data Editor and Job User roles.
    * Postgres as Staging:
        * **Postgres Database** A Postgres database (maybe CloudSQL), database and username that create tables in the database.

## Installation

1. **Install pip package:**
   ```bash
   pip install oracle2postgres_schema_validator
   
2. **Set Up Environment:**

    ## Client environment requirements:

    * python3.9
    * Shell environment (CLI) to run python scripts.
    * Network connectivity to Oracle and Postgres instances and BigQuery APIs.

## Usage
* **Collect Metadata:**
    * Oracle Collect: 
        Optional: Grant required access to metadata views which are the all_* views highlighted below. If you just want to get objects of the connected user you can skip this step and set --view_type to user.

        Please replace oracle_db_user with your database user.
        ```sql
            Option 1:
            Grant select any dictionary to oracle_db_user;

            Option 2:
            GRANT SELECT ON all_objects TO <db_user>;
            GRANT SELECT ON all_synonyms TO <db_user>;
            GRANT SELECT ON all_source TO <db_user>;
            GRANT SELECT ON all_indexes TO <db_user>;
            GRANT SELECT ON all_users TO <db_user>;
            GRANT SELECT ON all_role_privs TO <db_user>;
            GRANT SELECT ON all_roles TO <db_user>;
            GRANT SELECT ON all_triggers TO <db_user>;
            GRANT SELECT ON all_tab_columns TO <db_user>;
            GRANT SELECT ON all_tables TO <db_user>;
            GRANT SELECT ON all_constraints TO <db_user>;
            GRANT SELECT ON all_tab_privs TO <db_user>;
            GRANT SELECT ON all_sys_privs TO <db_user>;

        Execute the following command by putting your db connection settings. If you want to get all_* views use --view_type all, if you want to get user_* views use --view_type user:
            ```bash 
            oracollector --host oracle_ip_address --user db_user --password db_passwd --service oracle_service_name --view_type all

    * Postgres Collect: 
        ```bash 
        pgcollector --host pg_ip_address --database db_name --user user_name --password db_pwd
        
    Collector files will output 2 zip files. These needs to be moved under extracts directory before running importer.

* **Import**
    * **Import to BigQuery:**
        ```bash 
        mkdir extracts
        cp *.zip extracts/
        importer --project_id your_project_id --dataset_id your_dataset_name 

        You can specify an empty dataset otherwise dataset will be created if not exists.This command will unzip all the zip files underthe extracts folder.

    * **Import to Postgres:**
        
        ```bash
        importer --postgres_connection_string "postgresql://db-user:db-pwd@db_ip/db_name" --schema schema_compare

* **Generate Reports:**
    * BigQuery as Staging Area:
        ```bash 
        reporter --project_id your_project_id --dataset_name your_dataset_name --table_name instances --format html

    * Postgres as Staging Area:
        ```bash 
        reporter --db_type postgres --postgres_host your_postgres_host --postgres_port your_postgres_port --postgres_user your_postgres_user --postgres_password your_postgres_password --postgres_database your_postgres_database --schema_name schema_compare

    * Filter Schemas:
        ```bash
        reporter --db_type postgres --postgres_host your_postgres_host --postgres_port your_postgres_port --postgres_user your_postgres_user --postgres_password your_postgres_password --postgres_database your_postgres_database --schemas_to_compare 'SCHEMA1','SCHEMA2','SCHEMA3'


## Report Output
The generated reports will be saved in the reports directory.


## Contributing
Contributions are welcome! Please feel free to open issues or submit pull requests.

   **Clone the Repository:**
    ```bash
    git clone https://github.com/samkaradag/oracle2postgres-schema-validator


## License
This project is licensed under the Google License.


