# __init__.py 폴더에서 가장 먼저 실행

from . import openai_query, make_cypher_query
from flask import jsonify,  Flask, request, redirect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cublickdigital'

app.register_blueprint(openai_query.openAI)
app.register_blueprint(make_cypher_query.makecypher)

@app.route("/")
def hello():
    return "Cublick Digital"