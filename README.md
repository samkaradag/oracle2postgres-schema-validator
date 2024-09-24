# Oracle to Postgres Database Comparison Utility

This utility streamlines the process of comparing the schemas and code objects of Oracle and Postgres databases. This utility can be useful for heterogenous migrations from Oracle to Postgres or vice-versa to check whether all the objects i.e: PLSQL, tables, columns, data types, indexes, views, columns, sequences are migrated. It can leverage Google BigQuery or any Postgres database as a staging environment to load analyze metadata.

## Key Features

* **Metadata Collection:**  Extracts comprehensive schema metadata (tables, views, functions, procedures, etc.) from Oracle and Postgres databases.
* **BigQuery Integration:** Seamlessly imports collected metadata into Google BigQuery for centralized analysis.
* **Detailed Comparison Reports:** Generates clear, text and html based reports highlighting differences in:
    * Object counts (tables, views, etc.)
    * Missing objects in either database
    * Discrepancies in PLSQL and plpgsql (procedures, functions)
    * Column differences
    * Index differences
    * Other customizable comparison metrics

## Prerequisites

* **Oracle Database Access:** Credentials for Oracle database.
* **Postgres Database Access:** Credentials for Postgres database.
* **Staging Database** BigQuery or Postgres database is needed to stage extracted metadata
    * BigQuery as Staging:
        * **Google Cloud Project:**  A Google Cloud project with BigQuery enabled.
    * Postgres as Staging:
        * **Postgres Database** A Postgres database (maybe CloudSQL), database and username that create tables in the database.

## Installation

1. **Install pip package:**
   ```bash
   pip install oracle2postgres_schema_validator
   
2. **Set Up Environment:**

    ## Client environment requirements:

    * python3.9
    * Shell environment (CLI) and an empty directory to run python from.
    * Network connectivity to Oracle, Postgres instances and BigQuery APIs.

    Optional: Grant required access to Oracle catalog views which are the all_* views highlighted below. If you just want to get objects of the connected user you can skip this step and set --view_type to user.

    Please replace oracle_db_user with your database user.
    Option 1:
        ```sql
        Grant select any dictionary to oracle_db_user;

    Option 2:
        ```sql
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

## Usage

There are two ways to run ora2pg compare. The first is a single callable ora2pg compare command. The second is a more controlled way to run by running collectors, importer and reporter.

### Single Command

#### Postgres as a staging database to load metadata

Single command example, anonymized parameters:
```bash
compare \
--oracle_host oracle_host_name_or_ip \
--oracle_user database_user \
--oracle_password database_password \
--oracle_service oracle_service_name \
--oracle_view_type <user or all> \
--postgres_host postgres_host_name_or_ip \
--postgres_database database_name \
--postgres_user database_user \
--postgres_password database_password \
--staging_postgres_connection_string "postgresql://database_user:database_password@database_password/database_name" \
--staging_schema schema_compare \
--format html
```

Filter by specific schema
```bash
ora2pg-compare \
--oracle_host oracle_host_name_or_ip \
--oracle_user database_user \
--oracle_password database_password \
--oracle_service oracle_service_name \
--oracle_view_type <user or all> \
--postgres_host postgres_host_name_or_ip \
--postgres_database database_name \
--postgres_user database_user \
--postgres_password database_password \
--staging_postgres_connection_string "postgresql://database_user:database_password@database_password/database_name" \
--staging_schema schema_compare \
--format html
--schemas_to_compare 'SCHEMA1, SCHEMA2, SCHEMA3' \
```

#### Staging to Bigquery
```bash
ora2pg-compare \
--oracle_host oracle_host_name_or_ip \
--oracle_user database_user \
--oracle_password database_password \
--oracle_service oracle_service_name \
--oracle_view_type <user or all> \
--postgres_host postgres_host_name_or_ip \
--postgres_database database_name \
--postgres_user database_user \
--postgres_password database_password \
--staging_project_id gcp_project_id \
--staging_dataset_id dataset_name \
--format html
```


### Controlled execution:

#### 1. Collect Metadata:
* **Oracle Collect:**
        
        Execute the following command by putting your db connection settings. If you want to get all_* views use --view_type all, if you want to get user_* views use --view_type user:
            ```bash 
            oracollector --host oracle_ip_address --user db_user --password db_passwd --service oracle_service_name --view_type all

* **Postgres Collect:**
        ```bash 
        pgcollector --host pg_ip_address --database db_name --user user_name --password db_pwd
        
    Collectors will create a directory named "extracts" and output 2 zip files under extracts folder.

#### 2. Import:
* **Import to BigQuery:**
        ```bash 
        importer --project_id your_project_id --dataset_id your_dataset_name 

    You can specify an empty dataset otherwise dataset will be created if not exists.This command will unzip all the zip files under the extracts folder.

* **Import to Postgres:**
        
        ```bash
        importer --postgres_connection_string "postgresql://db-user:db-pwd@db_ip/db_name" --schema schema_compare

#### 3. Generate Report:
    In order to generate comparison report you need to run "reporter". Please use "--format html" flag to generate html report. You can use --format text to print output as text on the screen.

* **BigQuery as Staging Area:**
        ```bash 
        reporter --project_id your_project_id --dataset_id your_dataset_name --table_name instances --format html

* **Postgres as Staging Area:**
        ```bash 
        reporter --db_type postgres --postgres_host your_postgres_host --postgres_port your_postgres_port --postgres_user your_postgres_user --postgres_password your_postgres_password --postgres_database your_postgres_database --schema_name schema_compare --format html

    * Filter Schemas:
        ```bash
        reporter --db_type postgres --postgres_host your_postgres_host --postgres_port your_postgres_port --postgres_user your_postgres_user --postgres_password your_postgres_password --postgres_database your_postgres_database --schemas_to_compare 'SCHEMA1','SCHEMA2','SCHEMA3' --format html


## Report Output
The generated html report will be saved in the reports directory. 


## Contributing
Contributions are welcome! Please feel free to open issues or submit pull requests.

**Clone the Repository:**
```bash
git clone https://github.com/samkaradag/oracle2postgres-schema-validator


## License
This project is licensed under the Google License.


