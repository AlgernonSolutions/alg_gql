import logging

import boto3


def query_s3_csv(bucket_name, file_key, expression):
    results = []
    client = boto3.client('s3')
    response = client.select_object_content(
        Bucket=bucket_name,
        Key=file_key,
        ExpressionType='SQL',
        Expression=expression,
        InputSerialization={'CSV': {"FileHeaderInfo": "Use"}},
        OutputSerialization={'CSV': {}},
    )
    for event in response['Payload']:
        if 'Records' in event:
            records = event['Records']['Payload'].decode('utf-8')
            results.append(records)
        elif 'Stats' in event:
            details = event['Stats']['Details']
            logging.debug(f"Stats details bytesScanned: {details['BytesScanned']}")
            logging.debug(f"Stats details bytesProcessed: {details['BytesProcessed']}")
    return results
