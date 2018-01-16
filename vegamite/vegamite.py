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

@app.route("/")
def hello():
    return 'Hello World'


class Pair:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return 'Pair({0.x!r}, {0.y!r})'.format(self)

    def __str__(self):
        return '{0.x!s}, {0.y!s}'.format(self)



if __name__ == '__main__':
    app.run(debug=True)



