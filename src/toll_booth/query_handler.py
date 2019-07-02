import logging

from algernon.aws import lambda_logged
from algernon import ajson, rebuild_event

from toll_booth.tasks.query_s3_csv import query_s3_csv


@lambda_logged
def handler(event, context):
    event = rebuild_event(event)
    logging.info(f'received a call to run a query_s3_csv command: event/context: {event}/{context}')
    function_payload = {
        'bucket_name': event['bucket_name'],
        'file_key': event['file_key'],
        'expression': event['expression']
    }
    results = query_s3_csv(**function_payload)
    logging.info(f'completed a call to run a query_s3_csv command: results: {results}')
    return ajson.dumps(results)
