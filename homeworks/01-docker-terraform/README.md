# Module 1 Homework: Docker & SQL

## Question 1. Understanding docker first run

Run docker with the `python:3.12.8` image in an interactive mode, use the entrypoint
`bash`.

What's the version of `pip` in the image?

### Answer

Run in interactive mode with `bash`:
```shell
docker run -it python:3.12.8 bash
```

Then:
```shell
pip --version
```

StdOut:
```
pip 24.3.1 from /usr/local/lib/python3.12/site-packages/pip (python 3.12)
```

An alternative could be using `pip` as the entrypoint, run:
```shell
docker container run -it python:3.12.8 pip --version
```

StdOut:
```
pip 24.3.1 from /usr/local/lib/python3.12/site-packages/pip (python 3.12)
```

## Question 2. Understanding Docker networking and docker-compose

Given the following `docker-compose.yaml`, what is the `hostname` and `port` that
**pgadmin** should use to connect to the postgres database?

```yaml
services:
  db:
    container_name: postgres
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: 'postgres'
      POSTGRES_PASSWORD: 'postgres'
      POSTGRES_DB: 'ny_taxi'
    ports:
      - '5433:5432'
    volumes:
      - vol-pgdata:/var/lib/postgresql/data

  pgadmin:
    container_name: pgadmin
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: "pgadmin@pgadmin.com"
      PGADMIN_DEFAULT_PASSWORD: "pgadmin"
    ports:
      - "8080:80"
    volumes:
      - vol-pgadmin_data:/var/lib/pgadmin

volumes:
  vol-pgdata:
    name: vol-pgdata
  vol-pgadmin_data:
    name: vol-pgadmin_data
```

### Answer

There are two ways to connect to the Postgres server from pgAdmin:
1. `postgres:5432`
2. `db:5432`

##  Prepare Postgres

1. Run the Postgres database and pgAdmin with Docker Compose
   ([compose.yaml](compose.yaml)):
   ```shell
   docker-compose up -d
   ```
2. Data ingestion:
   A working Python environment is not necessary; we can do this using the provided
   [`Dockerfile`](./Dockerfile).

   Build the image:
   ```shell
   docker image build -t data_ingest:v1.0.0 .
   ```

   Run the ingest container twice:
   1. Green Taxi Trip (October 2019):
      ```shell
      docker container run -it --network taxi-trips-network data_ingest:v1.0.0 \
        --user=postgres \
        --password=postgres \
        --host=db \
        --port=5432 \
        --db=ny_taxi \
        --table_name=green_taxi_trips \
        --url=https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz \
        --data-kind=taxi
      ```
   2. Taxi Zones:
      ```shell
      docker container run -it --network taxi-trips-network data_ingest:v1.0.0 \
        --user=postgres \
        --password=postgres \
        --host=db \
        --port=5432 \
        --db=ny_taxi \
        --table_name=zones \
        --url=https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv \
        --data-kind=zones
      ```

## Question 3. Trip Segmentation Count

During the period of October 1st 2019 (inclusive) and November 1st 2019 (exclusive),
how many trips, **respectively**, happened:
1. Up to 1 mile
2. In between 1 (exclusive) and 3 miles (inclusive),
3. In between 3 (exclusive) and 7 miles (inclusive),
4. In between 7 (exclusive) and 10 miles (inclusive),
5. Over 10 miles

### Answers

All the following SQL queries return only one record, which is the result.

1. Up to 1 mile:
   ```sql
   SELECT COUNT(*)
   FROM green_taxi_trips
   WHERE lpep_pickup_datetime >= '2019-10-1'
     AND lpep_dropoff_datetime < '2019-11-1'
     AND trip_distance <= 1;
   ```
   **Result**: `104,802`
2. In between 1 (exclusive) and 3 miles (inclusive):
   ```sql
   SELECT COUNT(*)
   FROM green_taxi_trips
   WHERE lpep_pickup_datetime >= '2019-10-1'
     AND lpep_dropoff_datetime < '2019-11-1'
     AND trip_distance > 1
     AND trip_distance <= 3;
   ```
   **Result**: `198,924`
3. In between 3 (exclusive) and 7 miles (inclusive):
   ```sql
   SELECT COUNT(*)
   FROM green_taxi_trips
   WHERE lpep_pickup_datetime >= '2019-10-1'
     AND lpep_dropoff_datetime < '2019-11-1'
     AND trip_distance > 3
     AND trip_distance <= 7;
   ```
   **Result**: `109,603`
4. In between 7 (exclusive) and 10 miles (inclusive):
   ```sql
   SELECT COUNT(*)
   FROM green_taxi_trips
   WHERE lpep_pickup_datetime >= '2019-10-1'
     AND lpep_dropoff_datetime < '2019-11-1'
     AND trip_distance > 7
     AND trip_distance <= 10;
   ```
   **Result**: `27,678`
5. Over 10 miles:
   ```sql
   SELECT COUNT(*)
   FROM green_taxi_trips
   WHERE lpep_pickup_datetime >= '2019-10-1'
     AND lpep_dropoff_datetime < '2019-11-1'
     AND trip_distance > 10;
   ```
   **Result**: `35,189`

## Question 4. Longest trip for each day

Which was the pick up day with the longest trip distance? Use the pick up time for your
calculations.

Tip: For every day, we only care about one single trip with the longest distance.

### Answer

```sql
SELECT CAST(lpep_pickup_datetime AS DATE) AS trip_day,
       MAX(trip_distance) AS max_distance
FROM green_taxi_trips
GROUP BY trip_day
ORDER BY max_distance DESC
LIMIT 1;
```

This returns a table with the longest distance by a trip each day sorted from longest to
shortest and only the first record, which is the day for the longest trip:
**`2019-10-31`**.

## Question 5. Three biggest pickup zones

Which were the top pickup locations with over 13,000 in `total_amount` (across all trips)
for 2019-10-18?

Consider only `lpep_pickup_datetime` when filtering by date.

### Answer

```sql
SELECT "Zone",
       sum(total_amount) AS total_amount_per_location
FROM green_taxi_trips AS t
JOIN zones AS z ON t."PULocationID" = z."LocationID"
WHERE cast(t.lpep_pickup_datetime AS date) = '2019-10-18'
GROUP BY "Zone"
HAVING sum(total_amount) > 13000
ORDER BY total_amount_per_location DESC
LIMIT 3;
```

This returns a table with the total amount per pickup location accross all trips for
`2019-10-18` with a total amount over `13,000` and only the first three records, which are
the zones with the highest amounts: **`East Harlem North`, `East Harlem South`,
`Morningside Heights`**.

## Question 6. Largest tip

For the passengers picked up in October 2019 in the zone named "East Harlem North" which
was the drop off zone that had the largest tip?

Note: it's `tip` , not `trip`

We need the name of the zone, not the ID.

### Answer

```sql
SELECT zdo."Zone" AS do_zone,
       max(tip_amount) AS max_tip_amount
FROM green_taxi_trips AS t
JOIN zones AS zpu ON t."PULocationID" = zpu."LocationID"
JOIN zones AS zdo ON t."DOLocationID" = zdo."LocationID"
WHERE zpu."Zone" = 'East Harlem North'
GROUP BY do_zone
ORDER BY max_tip_amount DESC
LIMIT 1;
```

This returns a table with the dropoff zones and the largest trip tip for a passenger
picked up in "East Harlem North" and only the first record, which is the dropoff zone
with the largest tip: **`JFK Airport`**.

## Question 7. Terraform Workflow

Which of the following sequences, **respectively**, describes the workflow for:
1. Downloading the provider plugins and setting up backend,
2. Generating proposed changes and auto-executing the plan
3. Remove all resources managed by terraform`

Answers:
- terraform import, terraform apply -y, terraform destroy
- teraform init, terraform plan -auto-apply, terraform rm
- terraform init, terraform run -auto-approve, terraform destroy
- terraform init, terraform apply -auto-approve, terraform destroy
- terraform import, terraform apply -y, terraform rm

### Answer

**`terraform init`, `terraform apply -auto-approve`, `terraform destroy`**.
