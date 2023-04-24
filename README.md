# ML Observability workshop

Creating an end-to-end observability platform 


## Plan

* Introduction to MLOps and how it helps with the entire ML project lifecycle
* Discuss the ride duration prediction use case, discuss the overall architecture, show the notebook with the solution, show the script with training it (do not implement it live - to save time, and refer to Lightweight MLOps Zoomcamp for details)
* Implement a simple Flask application for serving the model
* Log the predictions to a Kinesis stream and save them in a data lake (s3)
* Set up a batch job for pulling the data from S3 and analyzing it 
* Analyze the data with Evidently, generate a simple visual report (Data Drift / Data Quality)
* Create a Prefect pipeline
* Automate data checks as part of the prediction pipeline. Design a custom test suite for data quality, data drift and prediction drift
* Model quality checks. Generate the report on model performance once you receive the ground truth
* Setting up slack/email alerts 
* Wrapping up: summarizing key takeaways and reviewing recommended practices


## Prerequisites

* Knowledge of Python (see [this article](https://mlbookcamp.com/article/python) for a refresher)
* Basic knowledge of ML (see [this course](http://mlzoomcamp.com) for a refresher)
* AWS account ([instructions how to create an account](https://mlbookcamp.com/article/aws))


## Preparation

* Install Python 3.9 (e.g. with [Anaconda](https://www.anaconda.com/download#downloads) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html))
* Install pipenv (`pip install -U pipenv`)
* Install the dependencies:

```bash
(cd train && pipenv install)
(cd serve && pipenv install)
(cd monitor && pipenv install)
```

## MLOps

Introduction to MLOps and how it helps with the entire ML project lifecycle

* Article: https://datatalks.club/blog/mlops-10-minutes.html

## Use case

Discuss the ride duration prediction use case, discuss the overall architecture, show the notebook with the solution, show the script with training it (do not implement it live - to save time, and refer to Lightweight MLOps Zoomcamp for details)

```bash
cd train
```

Start jupyter

```bash
pipenv run jupyter notebook
``` 

If you have Anaconda, you can skip installing the packages and run the 
notebook:

```bash
jupyter notebook
```

Next, execute the code to get the model


## Serving the model

Implement a simple Flask application for serving the model

```bash
cd serve
```

Run the `serve_starter.py` file:

```bash
pipenv run python serve_starter.py
```

Send a request:

```bash
REQUEST='{
    "ride_id": "XYZ10",
    "ride": {
        "PULocationID": 100,
        "DOLocationID": 102,
        "trip_distance": 30
    }
}'
URL="http://localhost:9696/predict"

curl -X POST \
    -d "${REQUEST}" \
    -H "Content-Type: application/json" \
    ${URL}
```

Response:

```json
{
  "prediction": {
    "duration": 20.77956787473484
  }
}
```

## Logging the predictions

Log the predictions to a Kinesis stream and save them in a data lake (s3)

Now let's modify our `serve_starter.py` to add logging. We will log the
prediction to a kinesis stream, but you can use any other way of 
logging.

Create a kinesis stream, e.g. `duration_prediction_serve_logger`. 

Add logging:

```python
import json

PREDICTIONS_STREAM_NAME = 'duration_prediction_serve_logger'
kinesis_client = boto3.client('kinesis')

# in the serve function

prediction_event = {
    'ride_id': ride_id,
    'ride': ride,
    'features': features,
    'prediction': result 
}

print(f'logging {prediction_event} to {PREDICTIONS_STREAM_NAME}...')

kinesis_client.put_record(
    StreamName=PREDICTIONS_STREAM_NAME,
    Data=json.dumps(prediction_event) + "\n",
    PartitionKey=str(ride_id)
)
```

(Note `+ "\n"` - it's important)

Send a request:

```bash
REQUEST='{
    "ride_id": "XYZ10",
    "ride": {
        "PULocationID": 100,
        "DOLocationID": 102,
        "trip_distance": 30
    }
}'
URL="http://localhost:9696/predict"

curl -X POST \
    -d "${REQUEST}" \
    -H "Content-Type: application/json" \
    ${URL}
```

We can check the logs

```bash
KINESIS_STREAM_OUTPUT='duration_prediction_serve_logger'
SHARD='shardId-000000000000'

SHARD_ITERATOR=$(aws kinesis \
    get-shard-iterator \
        --shard-id ${SHARD} \
        --shard-iterator-type TRIM_HORIZON \
        --stream-name ${KINESIS_STREAM_OUTPUT} \
        --query 'ShardIterator' \
)

RESULT=$(aws kinesis get-records --shard-iterator $SHARD_ITERATOR)

echo ${RESULT} | jq -r '.Records[0].Data' | base64 --decode
```


## Getting data from S3

Set up a batch job for pulling the data from S3 and analyzing it 

* Create an s3 bucket "duration-prediction-serve-logs"
* Enable firehose
* No data transformation (explore yourself)
* No data converstion (explore yourself)
* Destination: "s3://duration-prediction-serve-logs"
* Look at the files in the bucket


We can't wait for long, so we simulated the traffic and put the 
data in the monitor/data folder. To generate it, run 
the `prepare-files.ipynb` notebook.


## Data drift report

* Analyze the data with Evidently, generate a simple visual report (Data Drift / Data Quality).

Our virtual enviorment already has evidently installed. But if you're
using your own environment, run 

```bash
pip install evidently
```

Let's use it to generate a simple visual report


First, load the reference data (data we used for training)

```python
df_reference = pd.read_parquet('data/2022/01/2022-01-full.parquet')
```

Evidently is quite slow when analyzing large datasets, so we should
take a sample:


```python
df_reference = pd.read_parquet('data/2022/01/2022-01-full.parquet')
```

Next, we load the "production" data. First, we load the trips:

```python
year = 2023
month = 1
day = 2

trips_file = f'data/{year:04d}/{month:02d}/{year:04d}-{month:02d}-{day:02d}.parquet'
df_trips = pd.read_parquet(trips_file)
```

Second, load the logs:

```python
logs_file = f'data/{year:04d}/{month:02d}/{year:04d}-{month:02d}-{day:02d}-predictions.jsonl'

df_logs = pd.read_json(logs_file, lines=True)

df_predictions = pd.DataFrame()
df_predictions['ride_id'] = df_logs['ride_id']
df_predictions['prediction'] = df_logs['prediction'].apply(lambda p: p['prediction']['duration'])
```

And merge them: 

```python
df = df_trips.merge(df_predictions, on='ride_id')
```

Now let's see if there's any drift. Import evidently:

```python
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
```

Build a simple drift report:

```python
report = Report(metrics=[
    DataDriftPreset(columns=['PULocationID', 'DOLocationID', 'trip_distance']), 
])

report.run(reference_data=df_reference_sample, current_data=df_trips)

report.show(mode='inline')
```

In this preset report, it uses Jensen-Shannon distance to measure
the descrepancies between reference and production. While it says
that drift is detected, we should be careful about it and 
check other months.

We can tune it:

```python
report = Report(metrics=[
    DataDriftPreset(
        columns=['PULocationID', 'DOLocationID', 'trip_distance'],
        cat_stattest='psi',
        cat_stattest_threshold=0.2
        num_stattest='ks',
        num_stattest_threshold=0.2,
    ), 
])

report.run(reference_data=df_reference_sample, current_data=df_trips)
report.show(mode='inline')
```

Save the report as HTML:

```python
report.save_html(f'reports/report-{year:04d}-{month:02d}-{day:02d}.html')
``` 

You can generate these reports in your automatic pipelines and then
send them e.g. over email.

Let's create this pipeline.


## Creating a pipeline with Prefect

Now we'll use Prefect to orchestrate the report generation.

We will take the code we created and put it into a Python script. 
See `pipeline_sample.py` for details. 

Run prefect server:

```bash
pipenv run prefect config set PREFECT_UI_API_URL=http://127.0.0.1:4200/api
pipenv run prefect server start
```

Run the pipeline:

```bash
pipenv run prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
pipenv run python pipeline_sample.py
```


## Data checks

* Automate data checks as part of the prediction pipeline. Design a custom test suite for data quality, data drift and prediction drift.

Now we want to automate our checks and have them as a part of our 
prediction pipeline. 

## Model quality checks

* Model quality checks. Generate the report on model performance once you receive the ground truth.

## Alerting

* Setting up slack/email alerts 


## Summary

* Wrapping up: summarizing key takeaways and reviewing recommended practices



