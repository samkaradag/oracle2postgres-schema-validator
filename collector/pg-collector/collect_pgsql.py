import yaml
import psycopg2
import csv
import os
import zipfile

def extract_queries_to_csv(config_file):
    """
    Extracts data from a Postgres database based on queries and connection settings
    defined in a YAML file and writes each query's output to a separate CSV file.
    Finally, it zips all the CSV files.

    Args:
        config_file: Path to the YAML configuration file.
    """

    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    # Database connection settings
    db_host = config['database']['host']
    db_name = config['database']['name']
    db_user = config['database']['user']
    db_password = config['database']['password']

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
        # print(query)
        cur.execute(query["query"])

        # Fetch all rows from the query result
        rows = cur.fetchall()

       # Get the query name from the YAML (assuming it's a key in the query dict)
        query_name = config['queries'][i].get('name', f"query_{i+1}")

        # Create a CSV file for the query results
        csv_file = f"{query_name}.csv"
        

        with open(csv_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

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
    config_file = "config.yaml"  # Replace with your actual YAML file path
    extract_queries_to_csv(config_file)