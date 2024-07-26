How to Use:

Login to GCP:
gcloud auth application-default login

BigQuery as Staging Environment:
python importer.py --project_id your-project_id --dataset_id your-dataset-id

Postgres as Staging Environment:
python importer_pg.py --csv_directory ./extracts --postgres_connection_string postgresql://db-compare:db-compare@35.204.159.2/db-compare

