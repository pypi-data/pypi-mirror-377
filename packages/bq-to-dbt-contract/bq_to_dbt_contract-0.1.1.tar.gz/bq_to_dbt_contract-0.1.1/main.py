from google.cloud import bigquery
import google.auth
import sys

def inspect_table(project_id, dataset_name, table_id):
    client = bigquery.Client(project=project_id)
    table_path = f'{project_id}.{dataset_name}.{table_id}'
    print('table path: ' + table_path)
    table = client.get_table(table_path)
    # View table properties
    print(
        "Got table '{}.{}.{}'.".format(table.project, table.dataset_id, table.table_id)
    )
    print("Table schema: {}".format(table.schema))
    print("Table description: {}".format(table.description))
    print("Table has {} rows".format(table.num_rows))

# Perform a query.
#QUERY = ( 'SELECT name FROM `bigquery-public-data.usa_names.usa_1910_2013` ' 'WHERE state = "TX" ' 'LIMIT 100')
#query_job = client.query(QUERY)  # API request
#rows = query_job.result()  # Waits for query to finish
#for row in rows:
    #print(row.name)

def main():
    print("Hello from bq-to-dbt-contract!")
    project_id = sys.argv[1]
    dataset_name = sys.argv[2]
    table_id = sys.argv[3]
    print('Project: ' + project_id)
    print('Dataset: ' + dataset_name)
    print('Table: ' + table_id)
    inspect_table(project_id, dataset_name, table_id)

if __name__ == "__main__":
    main()
