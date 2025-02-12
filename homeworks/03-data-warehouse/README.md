# Module 3 Homework: Data Warehouse and BigQuery

## Prepare Infrastructure and Data

- Login to Google Cloud with Application Default Credentials:
  ```shell
  gcloud auth application-default login
  ```

- Create infrastructure with terraform (`cd terraform`):
  ```shell
  terraform init
  terraform apply
  ```

- Load the data into the GCS bucket (a Python environment with `google-cloud-storage`) is
  required:
  ```shell
  ./load_yellow_taxi_data.py "< your bucket name >"
  ```

- Create an external table in the BigQuery dataset created (from the BQ console):
  ```sql
  CREATE OR REPLACE EXTERNAL TABLE `< your project ID >.< your dataset ID >.external_yellow_tripdata`
  OPTIONS (
    format = 'PARQUET',
    uris = ['gs://< your bucket name >/yellow_tripdata_2024-*.parquet']
  );
  ```

- Create a non-partitioned regular table in the BigQuery dataset created (from the BQ
  console and using the external table):
  ```sql
  CREATE OR REPLACE TABLE `< your project ID >.< your dataset ID >.yellow_tripdata_non_partitioned` AS
  SELECT * FROM `< your project ID>.< your dataset ID >.external_yellow_tripdata`;
  ```

## Question 1

What is count of records for the 2024 Yellow Taxi Data?

- `65,623`
- `840,402`
- `20,332,093`
- `85,431,289`

### Answer

In the table `yellow_tripdata_non_partitioned` details tab, we can see the number of
records is **`20,332,093`**.

We can also see it by inspecting the tables with a query:
```sql
SELECT COUNT(*)
FROM `< table ID>`;
```
Which also shows **`20,332,093`**.

## Question 2

Write a query to count the distinct number of PULocationIDs for the entire dataset on both
the tables.

What is the **estimated amount** of data that will be read when this query is executed on
the External Table and the Table?

- `18.82 MB` for the External Table and `47.60 MB` for the Materialized Table
- `0 MB` for the External Table and `155.12 MB` for the Materialized Table
- `2.14 GB` for the External Table and `0MB` for the Materialized Table
- `0 MB` for the External Table and `0 MB` for the Materialized Table

### Answer

```sql
SELECT COUNT(DISTINCT PULocationID) FROM `< table ID >`;
```

The BigQuery console shows:

- **`O B` for the external table**.
- **`155.12 MB` for the materialized table**.


## Question 3

Write a query to retrieve the `PULocationID` from the table (not the external table) in
BigQuery. Now write a query to retrieve the `PULocationID` and `DOLocationID` on the same
table. Why are the estimated number of Bytes different?

- BigQuery is a columnar database, and it only scans the specific columns requested in the
  query. Querying two columns (`PULocationID`, `DOLocationID`) requires reading more data
  than querying one column (`PULocationID`), leading to a higher estimated number of bytes
  processed.
- BigQuery duplicates data across multiple storage partitions, so selecting two columns
  instead of one requires scanning the table twice, doubling the estimated bytes
  processed.
- BigQuery automatically caches the first queried column, so adding a second column
  increases processing time but does not affect the estimated bytes scanned.
- When selecting multiple columns, BigQuery performs an implicit join operation between
  them, increasing the estimated bytes processed.

### Answer

```sql
SELECT PULocationID FROM `< table ID >`;
```
```sql
SELECT PULocationID, DOLocationID FROM `< table ID >`;
```

The answer is:
> BigQuery is a columnar database, and it only scans the specific columns requested in the
query. Querying two columns (`PULocationID`, `DOLocationID`) requires reading more data
than querying one column (`PULocationID`), leading to a higher estimated number of bytes
processed.

## Question 4

How many records have a `fare_amount` of `0`?

- `128,210`
- `546,578`
- `20,188,016`
- `8,333`

### Answer

```sql
SELECT COUNT(*)
FROM `< table ID >`
WHERE fare_amount = 0;
```

The answer is: **8,333** records.

## Question 5

What is the best strategy to make an optimized table in BigQuery if your query will
always filter based on `tpep_dropoff_datetime` and order the results by `VendorID`?

(Create a new table with this strategy)

- Partition by `tpep_dropoff_datetime` and Cluster on `VendorID`
- Cluster on by `tpep_dropoff_datetime` and Cluster on `VendorID`
- Cluster on `tpep_dropoff_datetime` Partition by `VendorID`
- Partition by `tpep_dropoff_datetime` and Partition by `VendorID`

### Answer

The best strategy is **partition by `tpep_dropoff_datetime` and cluster on `VendorID`**.

To create the table we can run the following query (using the materialized table):

```sql
CREATE OR REPLACE TABLE `< your project ID >.< your dataset ID >.yellow_tripdata_partitioned`
PARTITION BY
  DATE(tpep_dropoff_datetime)
  CLUSTER BY VendorID AS
SELECT * FROM `< your project ID >.< your dataset ID >.yellow_tripdata_non_partitioned`;
```

## Question 6

Write a query to retrieve the distinct `VendorID`s between `tpep_dropoff_datetime`
`2024-03-01` and `2024-03-15` (inclusive)

Use the materialized table you created earlier in your from clause and note the estimated
bytes. Now change the table in the from clause to the partitioned table you created for
question 5 and note the estimated bytes processed. What are these values?

Choose the answer which most closely matches.

- `12.47 MB` for non-partitioned table and `326.42 MB` for the partitioned table
- `310.24 MB` for non-partitioned table and `26.84 MB` for the partitioned table
- `5.87 MB` for non-partitioned table and `0 MB` for the partitioned table
- `310.31 MB` for non-partitioned table and `285.64 MB` for the partitioned table

### Answer

```sql
SELECT DISTINCT VendorID
FROM `< table ID >`
WHERE tpep_dropoff_datetime BETWEEN '2024-03-01' AND '2024-03-15';
```

The answer is: **`310.24 MB` for non-partitioned table and `26.84 MB` for the partitioned
table**.

## Question 7

Where is the data stored in the External Table you created?

- Big Query
- Container Registry
- GCP Bucket
- Big Table

### Answer

The data for the external table is stored in a **Google Cloud Storage Bucket**.

## Question 8

It is best practice in Big Query to always cluster your data:

- True
- False

### Answer

The answer is **True**; it's a best practice to use clustered and partitioned tables for
cost reduction and query performance.

## (Bonus: Not worth points) Question 9

No Points: Write a `SELECT count(*)` query FROM the materialized table you created.

How many bytes does it estimate will be read? Why?

### Answer

It says `0 B`. The reason is that the data is stored outside BigQuery and the amount of
data processed can't be determined until the actual query completes.
