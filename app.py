from chalice import Chalice, Rate
from chalicelib.resolvers import schema
from chalicelib.csv_processor import process_csv
from chalicelib.models import get_all_sites, get_readings

app = Chalice(app_name='solar-api')


@app.route('/graphql', methods=['POST'])
def graphql():
    request = app.current_request
    body = request.json_body
    result = schema.execute_sync(
        body.get('query', ''),
        variable_values=body.get('variables'),
    )
    errors = [str(e) for e in result.errors] if result.errors else None
    return {
        'data': result.data,
        'errors': errors
    }


@app.on_s3_event(bucket='solar-readings', events=['s3:ObjectCreated:*'])
def handle_csv_upload(event):
    bucket = event.bucket
    key = event.key

    if not key.endswith('.csv'):
        print(f"Skipping non-CSV file: {key}")
        return {'status': 'skipped'}

    print(f"Processing CSV: {bucket}/{key}")
    result = process_csv(bucket, key)
    print(f"Result: {result}")
    return result


@app.schedule(Rate(1, unit=Rate.HOURS))
def aggregate_metrics(event):
    sites = get_all_sites()
    for site in sites:
        readings = get_readings(site['site_id'], limit=100)
        if not readings:
            continue
        outputs = [float(r['output_kw']) for r in readings]
        summary = {
            'site_id': site['site_id'],
            'total_output_kw': sum(outputs),
            'avg_output_kw': sum(outputs) / len(outputs),
            'max_output_kw': max(outputs),
        }
        print(f"Metrics for {site['name']}: {summary}")
    return {'status': 'ok'}