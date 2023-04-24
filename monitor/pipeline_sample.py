from datetime import datetime

import pandas as pd

from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

from prefect import flow, task


# configure via os.getenv
REFERENCE_DATA = 'data/2022/01/2022-01-full.parquet'


@task
def load_trips(year: int, month: int, day: int) -> pd.DataFrame:
    trips_file = f'data/{year:04d}/{month:02d}/{year:04d}-{month:02d}-{day:02d}.parquet'
    df_trips = pd.read_parquet(trips_file)

    return df_trips


@task
def load_logs(year: int, month: int, day: int) -> pd.DataFrame:
    logs_file = f'data/{year:04d}/{month:02d}/{year:04d}-{month:02d}-{day:02d}-predictions.jsonl'

    df_logs = pd.read_json(logs_file, lines=True)

    df_predictions = pd.DataFrame()
    df_predictions['ride_id'] = df_logs['ride_id']
    df_predictions['prediction'] = df_logs['prediction'].apply(lambda p: p['prediction']['duration'])

    return df_predictions


@task
def load_merged_data(year: int, month: int, day: int) -> pd.DataFrame:
    df_trips = load_trips(year, month, day)
    df_predictions = load_merged_data(year, month, day)

    df = df_trips.merge(df_predictions, on='ride_id')
    return df


@task
def create_drift_report(df_reference: pd.DataFrame, df_target: pd.DataFrame) -> Report:
    report = Report(metrics=[
        DataDriftPreset(columns=['PULocationID', 'DOLocationID', 'trip_distance'], ), 
    ])

    report.run(reference_data=df_reference, current_data=df_target)
    return report


@flow
def generate_drift_report(year: int, month: int, day: int):
    df_reference = pd.read_parquet(REFERENCE_DATA)
    df_reference_sample = df_reference.sample(n=10000, replace=False)

    df_target = load_trips(year, month, day)

    report_name = f'reports/report-{year:04d}-{month:02d}-{day:02d}.html'
    report = create_drift_report(df_reference_sample, df_target)
    report.save_html(report_name)


@flow
def run(date: datetime):
    generate_drift_report(date.year, date.month, date.day)


if __name__ == '__main__':
    date = datetime(year=2023, month=1, day=2)
    run(date)
