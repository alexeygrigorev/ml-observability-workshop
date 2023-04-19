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



## MLOps

* Introduction to MLOps and how it helps with the entire ML project lifecycle

## Use case

* Discuss the ride duration prediction use case, discuss the overall architecture, show the notebook with the solution, show the script with training it (do not implement it live - to save time, and refer to Lightweight MLOps Zoomcamp for details)

Install depencencies 

```bash
cd train

pip install -U pipenv 
pipenv instal 
pipenv shell
```

Start jupyter

```bash
jupyter notebook
``` 

And execute the code to get the model

Deactivate the env (ctr+C)

## Serving the model

* Implement a simple Flask application for serving the model


Install depencencies 

```bash
cd serve
 
pipenv instal 
pipenv shell
```

Run the `serve_starter.py` file:

```bash
python serve_starter.py
```

Send a request:

```bash
REQUEST='{
    "PULocationID": 100,
    "DOLocationID": 102,
    "trip_distance": 30
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

* Log the predictions to a Kinesis stream and save them in a data lake (s3)

Now let's modify our `serve_starter.py` to add logging. We will log the
prediction to a kinesis stream, but you can use any other way of 
logging.


## Getting data from S3

* Set up a batch job for pulling the data from S3 and analyzing it 

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



