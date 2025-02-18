# Workshop 1 Homework: Data Ingestion with `dlt`

All the answers were produced with the included [homework](./homework.ipynb) notebook.

## Question 1: `dlt` Version

Answer: `dlt` version **`1.6.1`**.

## Question 2: Define & Run the Pipeline (NYC Taxi API)

How many tables were created?

- `2`
- `4`
- `6`
- `8`

Answer: **4 tables were created**: `_dlt_loads`, `_dlt_pipeline_state`, `_dlt_version`,
and `ny_taxi` (the actual data).

## Question 3: Explore the Loaded Data

What is the total number of records extracted?

- `2,500`
- `5,000`
- `7,500`
- `10,000`

Answer: **`10,000` records**.

## Question 4: Trip Duration Analysis

What is the average trip duration?

- `12.3049`
- `22.3049`
- `32.3049`
- `42.3049`

Answer: **`12.3049` minutes**.


# Additional

These scripts are used to load the Yellow Taxi Data (2024, Jan-Jun) into Google Cloud
Storage and BigQuery:

1. [`load_yellow_taxi_data_gcs_1.py`](./load_yellow_taxi_data_gcs_1.py): Uses the function
   `download_yellow_taxi_data()` to download all the data files in parallel into a
   temporary directory; then, it uses the `filesystem` resource plus the `read_parquet()`
   transformer to run a `dlt` pipeline that stores the normalized data in a Google Cloud
   Storage bucket.
2. [`load_yellow_taxi_data_gcs_2.py`](./load_yellow_taxi_data_gcs_2.py): Uses the
   `dlt.resource` decorator with the function `data_files()` function to download the
   data files into a temporary directory and yield `FileItemDict` instances, which are
   required by the `read_parquet()` transformer. A pipeline is run with this resource
   to store the normalized data in a GCS bucket.
3. [`load_yellow_taxi_data_bq.py`](./load_yellow_taxi_data_bq.py): Same extraction logic
   as the previous example but storing the normalized data in a Google BigQuery dataset.

All of these require Google Cloud credentials, `.dlt/secrets.toml`:
```toml
[destination.bigquery]
location = "US"

[destination.credentials]
project_id = "< your project ID >"
private_key = "< your service account private key >"
client_email = "< your service account client email >"
```

Or use environment variables.

:warning: Notes:

- I couldn't figure out how to download files in parallel while extracting
for approaches 2 and 3.
- `dlt` documentation is deficient; it has many typos and is not intuitive to follow.
Although it is a powerful tool, I wouldn't say I like the project's code structure and
philosophy.
