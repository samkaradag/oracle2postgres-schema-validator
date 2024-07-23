Example bigquery usage:

python reporter_pg.py --project_id your_project_id --dataset_name your_dataset_name --table_name your_table_name --format html

Example Postgres usage:

python reporter_pg.py --db_type postgres --postgres_host your_postgres_host --postgres_port your_postgres_port --postgres_user your_postgres_user --postgres_password your_postgres_password --postgres_database your_postgres_database 

python reporter_pg.py --db_type postgres --postgres_host your_postgres_host --postgres_port your_postgres_port --postgres_user your_postgres_user --postgres_password your_postgres_password --postgres_database your_postgres_database 
python reporter_pg.py --db_type postgres --postgres_host 35.204.159.2 --postgres_port 5432 --postgres_user db-compare --postgres_password db-compare --postgres_database db-compare --schema_name schema_compare --format html

python importer_pg.py --csv_directory ./extracts --postgres_connection_string postgresql://db-compare:db-compare@35.204.159.2/db-compare

python reporter_pg.py --db_type postgres --postgres_host 35.204.159.2 --postgres_port 5432 --postgres_user db-compare --postgres_password db-compare --postgres_database db-compare --schema_name schema_compare --format html --schemas_to_compare 'SAMET'