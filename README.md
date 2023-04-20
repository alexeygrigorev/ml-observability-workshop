# ML Observability workshop

Creating an end-to-end observability platform 


## Plan

* Introduction to MLOps and how it helps with the entire ML project lifecycle
* Discuss the ride duration prediction use case, discuss the overall architecture, show the notebook with the solution, show the script with training it (do not implement it live - to save time, and refer to Lightweight MLOps Zoomcamp for details)
* Implement a simple Flask application for serving the model
* Log the predictions to a Kinesis stream and save them in a data lake (s3)
* Set up a batch job for pulling the data from S3 and analyzing it 
* Analyze the data with Evidently, generate a simple visual report (Data Drift / Data Quality)
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
```

## MLOps

Introduction to MLOps and how it helps with the entire ML project lifecycle

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
  "preduction": {
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


## Data drift report

* Analyze the data with Evidently, generate a simple visual report (Data Drift / Data Quality).

## Data checks

* Automate data checks as part of the prediction pipeline. Design a custom test suite for data quality, data drift and prediction drift.

## Model quality checks

* Model quality checks. Generate the report on model performance once you receive the ground truth.

## Alerting

* Setting up slack/email alerts 


## Summary

* Wrapping up: summarizing key takeaways and reviewing recommended practices



