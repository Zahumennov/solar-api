from chalice import Chalice

app = Chalice(app_name='solar-api')


@app.route('/')
def index():
    return {'hello': 'world'}
