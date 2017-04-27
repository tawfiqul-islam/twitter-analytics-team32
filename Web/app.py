from flask import Flask
from flask import render_template
from flask import jsonify
# from flask import Response
from lga import read_lga_file


# TODO config file
DATA_PATH = './static/resources/data/'
FILENAME_LGA = 'vic-lga.json'

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/data/vic-lga')
def get_data():
    # return Response(data, status=200, mimetype='application/json')
    preprocessed_lga_geojson, _ = read_lga_file()
    return jsonify(preprocessed_lga_geojson)


if __name__ == '__main__':
    # TODO debug=False
    app.run(host='0.0.0.0', port=5000, debug=True)
