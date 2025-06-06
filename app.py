from flask import Flask, jsonify, request, g
from pymongo import MongoClient
import os
from fluent import handler
from datetime import datetime
import logging

fluent_host = os.getenv("FLUENTD_HOST", "localhost")
fluent_port = int(os.getenv("FLUENTD_PORT", 24224))

app_name = "flask-mauro"

fluent_handler = handler.FluentHandler(app_name, host=fluent_host, port=fluent_port)
formatter = handler.FluentRecordFormatter({
    'job': app_name,
    'host': '%(hostname)s',
    'where': '%(module)s.%(funcName)s',
    'path': '%(path)s',
    'request': '%(request)s',
    'ip': '%(ip)s',
    'message': '%(message)s'
})

fluent_handler.setFormatter(formatter)

logger = logging.getLogger('flask')
logger.setLevel(logging.INFO)
logger.addHandler(fluent_handler)

app = Flask(__name__)

mongo_user = os.getenv("MONGO_USER", "user")
mongo_pass = os.getenv("MONGO_PASS", "password") 
mongo_host = os.getenv("MONGO_HOST", "localhost")
mongo_port = os.getenv("MONGO_PORT", "27017")
mongo_db = os.getenv("MONGO_DB", "db-mauro")

mongo_uri = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}/{mongo_db}?authSource=admin"
client = MongoClient(mongo_uri)
db = client[mongo_db]

@app.route('/')
def home():
    logger.info("Request a /", extra=g.log_extra)
    return jsonify({"message": "Hello from Flask!"})

@app.route('/health')
def health():
    logger.info("Health check OK", extra=g.log_extra)
    return jsonify({"status": "healthy"}), 200

@app.route('/echo', methods=['POST'])
def echo():
    data = request.get_json()
    logger.info(f"Received JSON", extra=g.log_extra)
    return jsonify(data)

@app.route('/mongo')
def mongo_data():
    try:
        items = list(db["example"].find({}, {"_id": 0}))
        logger.info("Data fetched from MongoDB", extra=g.log_extra)
        return jsonify(items)
    except Exception as e:
        logger.error(f"Error accessing MongoDB: {e}", extra=g.log_extra)
        return jsonify({"error": "MongoDB access error"}), 500

@app.before_request
def log_request():
    if request.method == 'GET':
        request_data = request.args.to_dict()
    elif request.is_json:
        request_data = request.get_json(silent=True)
    else:
        request_data = None

    g.log_extra = {
        'ip': request.remote_addr,
        'request': request_data,
        'path': request.path
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
