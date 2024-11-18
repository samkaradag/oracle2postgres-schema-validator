# Database Comparison Utility

This utility streamlines the process of comparing the schemas and code objects of Oracle and Postgres databases. This utility can be useful for homogenous and heterogenous migrations from Oracle to Postgres or vice-versa to check whether all the objects i.e: PLSQL, tables, columns, data types, indexes, views, columns, sequences are migrated. It can leverage Google BigQuery or any Postgres database as a staging environment to load analyze metadata.

Currently it supports following database types and comparison modes:

- **Oracle to Postgres:** Useful for heterogeneous migrations.
- **Oracle to Oracle:** Useful for comparing different Oracle environments (e.g., dev and prod) or validating migrations using export/import methods.
- **Postgres to Postgres:** Useful for comparing different Postgres environments or validating migrations.


## Key Features

* **Metadata Collection:**  Extracts comprehensive schema metadata (tables, views, functions, procedures, etc.) from Oracle and Postgres databases.
* **BigQuery Integration:** Imports collected metadata into Google BigQuery for centralized analysis.
* **Detailed Comparison Reports:** Generates clear, text and html based reports highlighting differences in:
    * Object counts (tables, views, etc.)
    * Missing objects in either database
    * Discrepancies in PLSQL and plpgsql (procedures, functions)
    * Column differences
    * Index differences
    * Other customizable comparison metrics

## Prerequisites
* **Database Access:**  Appropriate credentials for the databases you are comparing (Oracle and/or Postgres).
    * **Oracle Database Access:** Credentials for Oracle database.
    * **Postgres Database Access:** Credentials for Postgres database.
* **Staging Database:**  A BigQuery or Postgres database to stage the extracted metadata.
    * **BigQuery:**
        * A Google Cloud project with BigQuery enabled.
    * **Postgres:**
        * A Postgres database (e.g., CloudSQL) with a user that has permissions to create tables.
* **Python 3.9:**  The utility is written in Python and requires version 3.9 or higher.


## Installation

1. **Install pip package:**
   ```bash
   pip install db_compare
   
2. **Set Up Environment:**

    ## Client environment requirements:

    * python3.9
    * Shell environment (CLI) and an empty directory to run python from.
    * Network connectivity to Oracle, Postgres instances and BigQuery APIs.
    * **Oracle (Optional):** Grant access to Oracle catalog views (e.g., `dba_objects`, `dba_tables`, etc.) to the user you will use for the comparison. This is required if you want to collect metadata for all objects in the database. If you only need metadata for the connected user's objects, you can use the `--view_type user` option (default) and skip granting these permissions. See the "Usage" section for examples.


    Please replace oracle_db_user with your database user.

    Option 1:

        ```sql
        Grant select any dictionary to oracle_db_user;
        ```
    Option 2:

        ```sql
        GRANT SELECT ON dba_objects TO <db_user>;
        GRANT SELECT ON dba_synonyms TO <db_user>;
        GRANT SELECT ON dba_source TO <db_user>;
        GRANT SELECT ON dba_indexes TO <db_user>;
        GRANT SELECT ON dba_users TO <db_user>;
        GRANT SELECT ON dba_role_privs TO <db_user>;
        GRANT SELECT ON dba_roles TO <db_user>;
        GRANT SELECT ON dba_triggers TO <db_user>;
        GRANT SELECT ON dba_tab_columns TO <db_user>;
        GRANT SELECT ON dba_tables TO <db_user>;
        GRANT SELECT ON dba_constraints TO <db_user>;
        GRANT SELECT ON dba_tab_privs TO <db_user>;
        GRANT SELECT ON dba_sys_privs TO <db_user>;
        ```

## Usage

There are two ways to run ora2pg compare. The first is a single callable ora2pg compare command. The second is a more controlled way to run by running collectors, importer and reporter.

### Single Command (`compare`)
The `compare` command provides a streamlined way to run the entire comparison process. You must specify the comparison mode using one of the `--oracle_to_postgres`, `--oracle_to_oracle`, or `--postgres_to_postgres` flags.

**Example (Oracle to Postgres, Postgres staging):**

```bash
compare --oracle_to_postgres \
--oracle_host1 <oracle_host> --oracle_user1 <oracle_user> --oracle_password1 <oracle_password> --oracle_service1 <oracle_service> \
--postgres_host1 <postgres_host> --postgres_database1 <postgres_database> --postgres_user1 <postgres_user> --postgres_password1 <postgres_password> \
--staging_postgres_connection_string "postgresql://<staging_user>:<staging_password>@<staging_host>/<staging_database>" \
--staging_schema schema_compare --format html --schemas_to_compare 'SCHEMA1,SCHEMA2'
```

**Example Compare Different Schema Names (Oracle to Postgres, Postgres staging):**

```bash
compare --oracle_to_postgres \
--oracle_host1 <oracle_host> --oracle_user1 <oracle_user> --oracle_password1 <oracle_password> --oracle_service1 <oracle_service> \
--postgres_host1 <postgres_host> --postgres_database1 <postgres_database> --postgres_user1 <postgres_user> --postgres_password1 <postgres_password> \
--staging_postgres_connection_string "postgresql://<staging_user>:<staging_password>@<staging_host>/<staging_database>" \
--staging_schema schema_compare --format html  \
--schema_mapping 'SOURCE_SCHEMA/TARGET_SCHEMA'
```

**Example (Oracle to Oracle, Postgres Staging):**

(Please note that Staging environment can be postgres or bigquery independent of the comparison mode)

```bash
compare --oracle_to_oracle \
--oracle_host1 <oracle_host1> --oracle_user1 <oracle_user1> --oracle_password1 <oracle_password> --oracle_service1 <oracle_service> \
--oracle_host2 <oracle_host2> --oracle_user2 <oracle_user2> --oracle_password2 <oracle_password> --oracle_service2 <oracle_service> \
--staging_postgres_connection_string "postgresql://<staging_user>:<staging_password>@<staging_host>/<staging_database>" \
--staging_schema schema_compare --format html --schemas_to_compare 'SCHEMA1,SCHEMA2'
```

**Example (Oracle to Oracle, Postgres Staging, using tns):**
If you are using Oracle Client and tns please ensure that LD_LIBRARY_PATH is updated with the oracle_client path. i.e:

export LD_LIBRARY_PATH=~/oracle-client/instantclient_23_5:$LD_LIBRARY_PATH

```bash
compare --oracle_to_oracle \
--oracle_tns1 <oracle_tns_alias1> --oracle_tns_path1 <tnsnames.ora_path_1> \
--oracle_tns2 <oracle_tns_alias2> --oracle_tns_path2 <tnsnames.ora_path_2> \
--staging_postgres_connection_string "postgresql://<staging_user>:<staging_password>@<staging_host>/<staging_database>" \
--staging_schema schema_compare --format html --schemas_to_compare 'SCHEMA1,SCHEMA2'
```

**Example (Oracle to Oracle, BigQuery Staging):**
(Please note that Staging environment can be postgres or bigquery independent of the comparison mode)

```bash
compare --oracle_to_oracle \
--oracle_host1 <oracle_host1> --oracle_user1 <oracle_user1> --oracle_password1 <oracle_password> --oracle_service1 <oracle_service> \
--oracle_host2 <oracle_host2> --oracle_user2 <oracle_user2> --oracle_password2 <oracle_password> --oracle_service2 <oracle_service> \
--staging_project_id <gcp_project_id> --staging_dataset_id <dataset_name> --format html --schemas_to_compare 'SCHEMA1,SCHEMA2'
```

**Example (Postgres to Postgres, Postgres Staging):**

```bash
compare --oracle_to_oracle \
--postgres_host1 <postgres_host1> --postgres_database1 <postgres_database> \
--postgres_user1 <postgres_user1> --postgres_password1 <postgres_password> \
--postgres_host2 <postgres_host2> --postgres_database2 <postgres_database> \
--postgres_user2 <postgres_user2> --postgres_password2 <postgres_password> \
--staging_postgres_connection_string "postgresql://<staging_user>:<staging_password>@<staging_host>/<staging_database>" \
--staging_schema schema_compare --format html --schemas_to_compare 'SCHEMA1,SCHEMA2'
```

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

#### Use Google Secret Manager instead of plain passwords
export GOOGLE_CLOUD_PROJECT=project-id

compare --oracle_to_postgres --oracle_host1 oracle_ip --oracle_user1 SYSTEM --oracle_password1 gcp-secret:sct_oracle_pwd  --oracle_service1 orcl_service_name --oracle_view_type all                         --postgres_host1 postgres_ip --postgres_database1 pg_db_name --postgres_user1 dms-test --postgres_password1 gcp-secret:sct_pg_pwd   --staging_postgres_connection_string gcp-secret:sct_pg_staging_pwd --staging_schema schema_compare --format html --schemas_to_compare MOCKSCHEMA --oracle_protocol1 tcps 

You can use gcp_secret instaging_postgres_connection_string i.e:"postgresql://user:gcp-secret:secret_name@ip/dbname"


### Controlled execution:

#### 1. Collect Metadata:
* **Oracle Collect:** 
        
Execute the following command by putting your db connection settings. If you want to get dba_* views use --view_type all, if you want to get user_* views use --view_type user:

```bash 
oracollector --host oracle_ip_address --user db_user --password db_passwd --service oracle_service_name --view_type all
```

If comparison mode is oracle to oracle, run oracollector for 2 environments that you want to compare.

* **Postgres Collect:**

```bash 
pgcollector --host pg_ip_address --database db_name --user user_name --password db_pwd
```

If comparison mode is postgres to postgres, run pgcollector for 2 environments that you want to compare.    

Collectors will create a directory named "extracts" and output 2 zip files under extracts folder.

#### 2. Import:
* **Import to BigQuery:**
```bash 
importer --project_id your_project_id --dataset_id your_dataset_name 
```

You can specify an empty dataset otherwise dataset will be created if not exists.This command will unzip all the zip files under the extracts folder.

* **Import to Postgres:**
        
```bash
importer --postgres_connection_string "postgresql://db-user:db-pwd@db_ip/db_name" --schema schema_compare
```

#### 3. Generate Report:
In order to generate comparison report you need to run "reporter". Please use "--format html" flag to generate html report. You can use --format text to print output as text on the screen.

* **BigQuery as Staging Area:**
```bash 
reporter --project_id your_project_id --dataset_id your_dataset_name --table_name instances --format html
```
* **Postgres as Staging Area:**
```bash 
reporter --db_type postgres --postgres_host your_postgres_host --postgres_port your_postgres_port --postgres_user your_postgres_user --postgres_password your_postgres_password --postgres_database your_postgres_database --schema_name schema_compare --format html
```

* Filter Schemas:
```bash
reporter --db_type postgres --postgres_host your_postgres_host --postgres_port your_postgres_port --postgres_user your_postgres_user --postgres_password your_postgres_password --postgres_database your_postgres_database --schemas_to_compare 'SCHEMA1','SCHEMA2','SCHEMA3' --format html
```

## Report Output
The generated html report will be saved in the reports directory. 


## Contributing
Contributions are welcome! Please feel free to open issues or submit pull requests.

**Clone the Repository:**
```bash
git clone https://github.com/samkaradag/oracle2postgres-schema-validator


## License
This project is licensed under the Google License.


