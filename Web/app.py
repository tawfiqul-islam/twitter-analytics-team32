from flask import Flask
from flask import render_template
from flask import jsonify
from flask import Response
from lga import read_lga_geojson_from_couchdb
from aurin_data import read_all_aurin_data_from_couchdb
import json


# TODO config file
DATA_PATH = './static/resources/data/'
FILENAME_LGA = 'vic-lga.json'

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/data/vic-lga')
def get_vic_lga():
    # return Response(data, status=200, mimetype='application/json')
    lga_geojson = read_lga_geojson_from_couchdb()
    # return jsonify(lga_geojson)
    # does not do any pretty print because
    # it increases the json file to 3x the original
    return Response(json.dumps(lga_geojson, separators=(',', ':')), status=200, mimetype='application/json')


@app.route('/data/scenario-1')
def get_scenario_1():
    aurin_list = read_all_aurin_data_from_couchdb()
    return jsonify(aurin_list)


if __name__ == '__main__':
    # TODO debug=False
    app.run(host='0.0.0.0', port=5000, debug=True)
