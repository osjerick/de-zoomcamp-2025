# Module 2 Homework: Workflow Orchestration

##  Prepare Postgres

1. Run the Postgres database, pgAdmin, and Kestra with Docker Compose
   ([compose.yaml](compose.yaml)):
   ```shell
   docker-compose up -d
   ```

2. Data ingestion:

   :information_source: The following steps use the Kestra API; the operations can also be
   executed from the Kestra UI.

   - Load the data ingestion flow,
     [flows/taxi_trips_data_ingestion.yaml](./flows/taxi_trips_data_ingestion.yaml) into
     Kestra:
     ```shell
     curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@flows/taxi_trips_data_ingestion.yaml
     ```
   - Run the data ingestion flow with backfills:
     - `yellow` taxi data:
       ```shell
       curl -XPUT http://localhost:8080/api/v1/triggers -H 'Content-Type: application/json' \
       -d '{
         "backfill": {
           "start": "2019-01-01T00:00:00.000Z",
           "end": "2021-07-31T00:00:00.000Z",
           "inputs": {
             "taxi": "yellow"
           },
           "labels": [
             {
               "key": "backfill",
               "value": "true"
             }
           ]
         },
         "flowId": "taxi_trips_data_ingestion",
         "namespace": "taxi_trips",
         "triggerId": "yellow_schedule"
       }'
       ```
     - `green` taxi data:
       ```shell
       curl -XPUT http://localhost:8080/api/v1/triggers -H 'Content-Type: application/json' \
       -d '{
         "backfill": {
           "start": "2019-01-01T00:00:00.000Z",
           "end": "2021-07-31T00:00:00.000Z",
           "inputs": {
             "taxi": "green"
           },
           "labels": [
             {
               "key": "backfill",
               "value": "true"
             }
           ]
         },
         "flowId": "taxi_trips_data_ingestion",
         "namespace": "taxi_trips",
         "triggerId": "green_schedule"
       }'
       ```

3. Generate answers:

   :information_source: This workflow produces all the answer for the present homework
   question; however, questions can be solved by other alternatives.

   - Load the answers flow,
     [flows/workflow_orchestration_answers.yaml](./flows/workflow_orchestration_answers.yaml)
     into Kestra:
     ```shell
     curl -X POST http://localhost:8080/api/v1/flows/import -F fileUpload=@flows/workflow_orchestration_answers.yaml
     ```
   - Run the answers flow:
     ```shell
     curl -X POST http://localhost:8080/api/v1/executions/homeworks/workflow-orchestration-answers
     ```

## Question 1

Within the execution for `Yellow` Taxi data for the year `2020` and month `12`: what is
the uncompressed file size (i.e. the output file `yellow_tripdata_2020-12.csv` of the
`extract` task)?

- `128.3 MB`
- `134.5 MB`
- `364.7 MB`
- `692.6 MB`

### Answer

We can monitor the outputs of the `extract` task. There we can see the file size in `MiB`,
which is **`128.3 MiB`**; however, the possible answers are in `MB`, so the correct answer
is **`134.5 MB`**. Although this is correct, monitoring the output is required to be done
in real time, since the task `purge_files` will remove everythin.

Another approach is to add a `size` task, which will output the size of the file in bytes:
```yaml
- id: size
  type: io.kestra.plugin.core.storage.Size
  uri: "{{render(vars.data)}}"
```

So the output is **`134,481,400 bytes`**, then the answer is **`134.5 MB`**.

In the answers flow,
[flows/workflow_orchestration_answers.yaml](./flows/workflow_orchestration_answers.yaml),
we have the `question_01` task, which logs the size of the file in bytes with `ls -l`:
```yaml
- id: question_01
  type: io.kestra.plugin.scripts.shell.Commands
  outputFiles:
    - "*.csv"
  taskRunner:
    type: io.kestra.plugin.core.runner.Process
  commands:
    - wget -qO- https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2020-12.csv.gz | gunzip > output.csv && ls -l output.csv
```
Whose output also is **`134,481,400 bytes`**, then the answer is **`134.5 MB`**.

## Question 2

What is the rendered value of the variable `file` when the inputs `taxi` is set to
`green`, `year` is set to `2020`, and `month` is set to `04` during execution?

- `{{inputs.taxi}}_tripdata_{{inputs.year}}-{{inputs.month}}.csv`
- `green_tripdata_2020-04.csv`
- `green_tripdata_04_2020.csv`
- `green_tripdata_2020.csv`

### Answer

The value of the `file` variable is
`"{{inputs.taxi}}_tripdata_{{trigger.date | date('yyyy-MM')}}.csv"`. For `taxi = "green"`
and `date = "2020-04-01"`, which is the date at which the backfill execution will run,
the rendered value of the `file` variable is **`green_tripdata_2020-04.csv`**.

We can also check this in the backfill execution labels for the date `2020-04-01`, since
we add a the label `file` in the `set_label` task. It shows
**`filed: green_tripdata_2020-04.csv`**

In the answers flow,
[flows/workflow_orchestration_answers.yaml](./flows/workflow_orchestration_answers.yaml),
we have the `question_02` task, which logs the rendered string
`"{{vars.question_02_taxi}}_tripdata_{{vars.question_02_date | date('yyyy-MM')}}.csv"`
where `question_02_taxi = "green"` and `question_02_date = "2020-04-01"`:
```yaml
- id: question_02
  type: io.kestra.plugin.core.log.Log
  message: "{{vars.question_02_taxi}}_tripdata_{{vars.question_02_date | date('yyyy-MM')}}.csv"
```

The answer is **`green_tripdata_2020-04.csv`**.

## Question 3

How many rows are there for the `Yellow` Taxi data for all CSV files in the year 2020?

- `13,537.299`
- `24,648,499`
- `18,324,219`
- `29,430,127`

### Answer

We can query the `yellow_tripdata` table to count the number of rows for which the
`filename` follows the pattern `yellow_tripdata_2020-<month>.csv`:
```sql
SELECT COUNT(*)
FROM yellow_tripdata
WHERE filename LIKE 'yellow_tripdata_2020-%.csv';
```

This returns a table that shows the count of rows from all the CSV files in the year 2020,
which is **`24,648,499`**

In the answers flow,
[flows/workflow_orchestration_answers.yaml](./flows/workflow_orchestration_answers.yaml),
we have the `question_03` task; which also runs this query:
```yaml
- id: question_03
  type: io.kestra.plugin.jdbc.postgresql.Queries
  sql: |
    SELECT COUNT(*)
    FROM yellow_tripdata
    WHERE filename LIKE 'yellow_tripdata_2020-%.csv';
  fetchType: FETCH_ONE
```

And the output is `{ "row": { "count": 24648499 }, "size": 1 }`, so the answer is
**`24,648,499`**.

## Question 4

How many rows are there for the `Green` Taxi data for all CSV files in the year 2020?

- `5,327,301`
- `936,199`
- `1,734,051`
- `1,342,034`

### Answer

We can query the `green_tripdata` table to count the number of rows for which the
`filename` follows the pattern `green_tripdata_2020-<month>.csv`:
```sql
SELECT COUNT(*)
FROM green_tripdata
WHERE filename LIKE 'green_tripdata_2020-%.csv';
```

This returns a table that shows the count of rows from all the CSV files in the year 2020,
which is **`1,734,051`**

In the answers flow,
[flows/workflow_orchestration_answers.yaml](./flows/workflow_orchestration_answers.yaml),
we have the `question_04` task; which also runs this query:
```yaml
- id: question_04
  type: io.kestra.plugin.jdbc.postgresql.Queries
  sql: |
    SELECT COUNT(*)
    FROM green_tripdata
    WHERE filename LIKE 'green_tripdata_2020-%.csv';
  fetchType: FETCH_ONE
```

And the output is `{ "row": { "count": 1734051 }, "size": 1 }`, so the answer is
**`1,734,051`**.

## Question 5

How many rows are there for the `Yellow` Taxi data for the March 2021 CSV file?

- `1,428,092`
- `706,911`
- `1,925,152`
- `2,561,031`

### Answer

We can query the `yellow_tripdata` table to count the number of rows for which the
`filename` is `yellow_tripdata_2021-03.csv`:
```sql
SELECT COUNT(*)
FROM green_tripdata
WHERE filename LIKE 'yellow_tripdata_2021-03.csv';
```

This returns a table that shows the count of rows from CSV file in the March 2021,
which is **`1,925,152`**

In the answers flow,
[flows/workflow_orchestration_answers.yaml](./flows/workflow_orchestration_answers.yaml),
we have the `question_05` task; which also runs this query:
```yaml
- id: question_05
  type: io.kestra.plugin.jdbc.postgresql.Queries
  sql: |
    SELECT COUNT(*)
    FROM yellow_tripdata
    WHERE filename = 'yellow_tripdata_2021-03.csv';
  fetchType: FETCH_ONE
```

And the output is `{ "row": { "count": 1925152 }, "size": 1 }`, so the answer is
**`1,925,152`**.

## Question 6

How would you configure the timezone to New York in a Schedule trigger?

- Add a `timezone` property set to `EST` in the `Schedule` trigger configuration
- Add a `timezone` property set to `America/New_York` in the `Schedule` trigger
  configuration
- Add a `timezone` property set to `UTC-5` in the `Schedule` trigger configuration
- Add a `location` property set to `New_York` in the `Schedule` trigger configuration

### Answer

According to the
[Schedule Trigger](https://kestra.io/docs/workflow-components/triggers/schedule-trigger)
documentation, to add New York as a timezone for the trigger, we can set the `timezone`
property to `America/New_York`, for example:
```yaml
triggers:
  - id: daily
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "@daily"
    timezone: America/New_York
```
