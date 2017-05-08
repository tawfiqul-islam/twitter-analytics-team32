from flask import Flask
from flask import render_template
from flask import jsonify
from flask import Response
from lga import read_lga_geojson_from_couchdb
from aurin_data import read_scenario_from_couchdb
from tweet_data import read_tweet_scenario_from_couchdb
import json
import configparser
from ast import literal_eval


config = configparser.ConfigParser()
config.read('../Web/config_web.ini')

# rows from different AURIN data are joined based on this key
COUCHDB_KEY = config['couchdb']['key']

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
        aurin_dict = read_scenario_from_couchdb(n)
        tweet_dict = read_tweet_scenario_from_couchdb(n)

        # join the two data into 'aurin_dict'
        # join 'rows'
        for row in aurin_dict['rows']:
            lga_code = row[COUCHDB_KEY]
            if lga_code in tweet_dict['rows']:
                for tweet_col in tweet_dict['rows'][lga_code]:
                    row[tweet_col] = tweet_dict['rows'][lga_code][tweet_col]

        # join 'column_infos'
        for c in tweet_dict['column_infos']:
            aurin_dict['column_infos'][c] = tweet_dict['column_infos'][c]

        return jsonify(aurin_dict)
    return 'TODO handle error'


if __name__ == '__main__':
    # TODO debug=False
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
