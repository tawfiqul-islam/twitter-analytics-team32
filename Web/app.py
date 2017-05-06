from flask import Flask
from flask import render_template
from flask import jsonify
from flask import Response
from lga import read_lga_geojson_from_couchdb
from aurin_data import read_scenario_from_couchdb
import json
import configparser
from ast import literal_eval


config = configparser.ConfigParser()
config.read('../Web/config_web.ini')

SCENARIOS = literal_eval(config['couchdb']['scenarios'])


app = Flask(__name__)


def is_valid_scenario(n):
    if n in SCENARIOS:
        return True
    return False


@app.route('/scenario_map/<n>')
def index(n):
    n = int(n)
    if (is_valid_scenario(n)):
        data = {'which_scenario': n}
        return render_template('scenario_map.html', data=data)
    return 'TODO handle error'


@app.route('/scenario_graphs/<n>')
def scenario_graphs(n):
    n = int(n)
    if (is_valid_scenario(n)):
        data = {'which_scenario': n}
        return render_template('scenario_graphs.html', data=data)
    return 'TODO handle error'


@app.route('/scenario_graphs_bar/<n>')
def scenario_graphs_bar(n):
    n = int(n)
    if (is_valid_scenario(n)):
        data = {'which_scenario': n, 'type': 'bar'}
        return render_template('scenario_graphs_bar.html', data=data)
    return 'TODO handle error'


@app.route('/data/vic-lga')
def data_vic_lga():
    # return Response(data, status=200, mimetype='application/json')
    lga_geojson = read_lga_geojson_from_couchdb()
    # return jsonify(lga_geojson)
    # does not do any pretty print because
    # it increases the json file to 3x the original
    return Response(json.dumps(lga_geojson, separators=(',', ':')), status=200, mimetype='application/json')


@app.route('/data/scenario/<n>')
def data_scenario(n):
    n = int(n)
    if (is_valid_scenario(n)):
        aurin_list = read_scenario_from_couchdb(n)
        return jsonify(aurin_list)
    return 'TODO handle error'


if __name__ == '__main__':
    # TODO debug=False
    app.run(host='0.0.0.0', port=5000, debug=True)
