import csv
import io
import boto3
import os
from chalicelib.models import add_reading

LOCALSTACK_URL = os.getenv('LOCALSTACK_URL', 'http://localhost:4566')

s3 = boto3.client(
    's3',
    endpoint_url=LOCALSTACK_URL,
    region_name='us-east-1',
    aws_access_key_id='test',
    aws_secret_access_key='test'
)


def process_csv(bucket: str, key: str) -> dict:
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response['Body'].read().decode('utf-8')

    reader = csv.DictReader(io.StringIO(content))

    processed = 0
    errors = 0

    for row in reader:
        try:
            add_reading(
                site_id=row['site_id'],
                output_kw=float(row['output_kw'])
            )
            processed += 1
        except Exception as e:
            print(f"Error processing row {row}: {e}")
            errors += 1

    return {
        'processed': processed,
        'errors': errors
    }