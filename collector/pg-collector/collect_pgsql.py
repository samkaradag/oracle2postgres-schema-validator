import yaml
import psycopg2
import csv
import os
import zipfile
import argparse

def extract_queries_to_csv(db_host, db_name, db_user, db_password, config_file):
    """
    Extracts data from a Postgres database based on queries and connection settings
    provided as input arguments. Writes each query's output to a separate CSV file,
    and then zips all the CSV files.

    Args:
        db_host: The hostname of the Postgres database.
        db_name: The name of the Postgres database.
        db_user: The username for the Postgres database.
        db_password: The password for the Postgres database.
        config_file: Path to the YAML configuration file.
    """

    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    # Connect to the database
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )

    # Create a cursor object
    cur = conn.cursor()

    # Loop through each query in the configuration file
    for i, query in enumerate(config['queries']):
        # Execute the query
        cur.execute(query["query"])

        # Fetch all rows from the query result
        rows = cur.fetchall()

        # Get the query name from the YAML (assuming it's a key in the query dict)
        query_name = config['queries'][i].get('name', f"query_{i+1}")

        # Create a CSV file for the query results
        csv_file = f"{query_name}.csv"

        with open(csv_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter='|')

            # Write the column headers (optional, can be customized)
            writer.writerow([desc[0] for desc in cur.description])

            # Write the data rows
            writer.writerows(rows)

    # Zip all the CSV files
    zip_file = "extracted_data.zip"
    with zipfile.ZipFile(zip_file, 'w') as z:
        for filename in os.listdir():
            if filename.endswith(".csv"):
                z.write(filename)
                os.remove(filename)

    # Close the cursor and connection
    cur.close()
    conn.close()

    print(f"Extracted data and saved to {zip_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract data from a Postgres database')
    parser.add_argument('host', type=str, help='Hostname of the Postgres database')
    parser.add_argument('database', type=str, help='Name of the Postgres database')
    parser.add_argument('user', type=str, help='Username for the Postgres database')
    parser.add_argument('password', type=str, help='Password for the Postgres database')
    parser.add_argument('config_file', type=str, help='Path to the YAML configuration file')
    args = parser.parse_args()

    extract_queries_to_csv(args.host, args.database, args.user, args.password, args.config_file)