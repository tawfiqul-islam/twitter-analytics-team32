import configparser
import sys
import json
import couchdb


config = configparser.ConfigParser()
config.read('./config_web.ini')

COUCHDB_URL = config['couchdb']['ip_address'] + ':' + config['couchdb']['port']
COUCHDB_NAME = config['couchdb']['db_name_aurin']

# rows from different AURIN data are joined based on this key
COUCHDB_KEY = config['couchdb']['key']

FILENAMES_AURIN = config['aurin_json_files']


def read_json(filename):
    with open(filename) as f:
        json_dict = json.load(f)
    return json_dict


def get_key(metadata_filename):
    metadata_json_dict = read_json(metadata_filename)
    return metadata_json_dict['key']


def upload_aurin_data(db, json_dict, doc_type, key):
    # relevant data are in features[i].properties
    for feature in json_dict['features']:
        curr_doc = feature['properties']
        curr_doc['doc_type'] = doc_type  # use to differentiate aurin data

        # store doc's key using uniform name
        curr_key = curr_doc[key]  # store key first
        curr_doc.pop(key)  # remove key
        curr_doc[COUCHDB_KEY] = curr_key  # store key using uniform name

        db.save(curr_doc)


def upload_all_aurin_data():
    couch = couchdb.Server(COUCHDB_URL)
    try:
        db = couch.create(COUCHDB_NAME)
    except couchdb.PreconditionFailed:
        # database with that name exists
        # delete that and create a fresh one
        couch.delete(COUCHDB_NAME)
        db = couch.create(COUCHDB_NAME)

    for aurin_data_title, aurin_data_filename in FILENAMES_AURIN.items():
        json_dict = read_json(aurin_data_filename)

        if (aurin_data_filename[-5:] != '.json'):
            print('Error on reading %s' % aurin_data_filename)
            print('AURIN JSON files should have the extension .json')
            sys.exit(1)
        metadata_filename = aurin_data_filename[:-5] + '_metadata.json'
        key = get_key(metadata_filename)
        upload_aurin_data(db, json_dict, aurin_data_title, key)
