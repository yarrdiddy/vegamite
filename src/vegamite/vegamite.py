import time
import redis

from flask import Flask, request, jsonify
from celery.signals import worker_ready
from numpy import int64
from vegamite.config import config
from vegamite.tasks import make_celery


app = Flask(__name__)


app.config.update(
    CELERY_BROKER_URL=config.celery.broker_url,
    result_backend=config.celery.result_backend
)

celery = make_celery(app)

@app.route("/", methods=['GET', 'POST'])
def test_success():
    return jsonify({'success': True}), 200, {'ContentType':'application/json'}

@app.route("/search", methods=['GET', 'POST'])
def search():
    print(request)
    print(request.data)

@app.route("/query", methods=['GET', 'POST'])
def query():
    print(request)
    print(request.data)

@app.route("/annotations", methods=['GET', 'POST'])
def annotations():
    print(request)
    print(request.data)

if __name__ == '__main__':
    app.run(debug=True)



