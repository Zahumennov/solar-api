import json
from chalice import Chalice, Rate
from chalicelib.resolvers import schema

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


@app.schedule(Rate(1, unit=Rate.HOURS))
def aggregate_metrics(event):
    from chalicelib.models import get_all_sites, get_readings
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