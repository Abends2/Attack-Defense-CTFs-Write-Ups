from flask import Flask, request
import json
import time
from util import gen_flag
app = Flask(__name__)


BASE_PORT = 11000


@app.route('/')
def index():
    return "This service is basically unhackable since it does basically nothing"  # noqa: E501


@app.route('/flags.json')
def flags():
    port = int(request.environ['SERVER_PORT'])
    team = port - BASE_PORT
    flags = [gen_flag(1, team, int(time.time()-t)).decode() for t in range(4)]
    return json.dumps({
        "flags": flags,
    })


if __name__ == '__main__':
    app.run()
