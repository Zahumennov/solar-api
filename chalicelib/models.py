import boto3
from datetime import datetime, timezone
import uuid
import os
from typing import Optional

# LocalStack endpoint
LOCALSTACK_URL = os.getenv('LOCALSTACK_URL', 'http://localhost:4566')

dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=LOCALSTACK_URL,
    region_name='us-east-1',
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

SITES_TABLE = 'SolarSites'
READINGS_TABLE = 'EnergyReadings'


def get_sites_table():
    return dynamodb.Table(SITES_TABLE)


def get_readings_table():
    return dynamodb.Table(READINGS_TABLE)


# --- Solar Sites ---

def create_site(name: str, location: str, capacity: float) -> dict:
    table = get_sites_table()
    site = {
        'site_id': str(uuid.uuid4()),
        'name': name,
        'location': location,
        'capacity': str(capacity),
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    table.put_item(Item=site)
    return site


def get_site(site_id: str) -> Optional[dict]:
    table = get_sites_table()
    response = table.get_item(Key={'site_id': site_id})
    return response.get('Item')


def get_all_sites() -> list:
    table = get_sites_table()
    response = table.scan()
    return response.get('Items', [])


# --- Energy Readings ---

def add_reading(site_id: str, output_kw: float) -> dict:
    table = get_readings_table()
    reading = {
        'site_id': site_id,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'output_kw': str(output_kw)
    }
    table.put_item(Item=reading)
    return reading


def get_readings(site_id: str, limit: int = 10) -> list:
    table = get_readings_table()
    response = table.query(
        KeyConditionExpression='site_id = :sid',
        ExpressionAttributeValues={':sid': site_id},
        ScanIndexForward=False,
        Limit=limit
    )
    return response.get('Items', [])