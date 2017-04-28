import configparser
from ast import literal_eval
import sys
import json
import couchdb
from bisect import bisect_right


config = configparser.ConfigParser()
config.read('./config_web.ini')

COUCHDB_URL = config['couchdb']['ip_address'] + ':' + config['couchdb']['port']
COUCHDB_NAME = config['couchdb']['db_name_aurin']

# rows from different AURIN data are joined based on this key
COUCHDB_KEY = config['couchdb']['key']

FILENAMES_AURIN = config['aurin_json_files']

AURIN_COLUMNS = dict(config['aurin_columns'])
for key in AURIN_COLUMNS:
    AURIN_COLUMNS[key] = literal_eval(AURIN_COLUMNS[key])

DECIMAL_PLACES = int(config['aurin_preprocessing']['decimal_places'])
ACCURATE_TO = float(config['aurin_preprocessing']['accurate_to'])


def read_json(filename):
    with open(filename) as f:
        json_dict = json.load(f)
    return json_dict


def get_key(metadata_filename):
    metadata_json_dict = read_json(metadata_filename)
    return metadata_json_dict['key']


def generate_groups(list_of_ints, n):
    """Tries to divide the integers into n groups with same size. However fails
    when size of list is not divisible by n and/or there are duplicates in the
    list"""
    groups = []

    list_of_ints.sort()

    curr_index = 0
    lower_boundary = list_of_ints[0]
    size = len(list_of_ints) / n
    for i in range(n):
        start_index = curr_index
        if i == n-1:
            # last group
            last_index = len(list_of_ints) - 1
        else:
            last_index = start_index+size-1
        upper_boundary = list_of_ints[last_index]

        if (lower_boundary > upper_boundary):
            print('Error when trying to calculate groups.')
            print('List: %s' % str(list_of_ints))
            print('n: %d' % n)
            print('Boundaries so far: %s' % groups)
            sys.exit(1)

        groups.append((lower_boundary, upper_boundary))

        curr_index = bisect_right(list_of_ints, upper_boundary)
        lower_boundary = upper_boundary + ACCURATE_TO
    return groups


def get_group(groups, value):
    value = round(value, DECIMAL_PLACES)
    for group in groups:
        if group[0] <= value <= group[1]:
            return str(group[0]) + '-' + str(group[1])
    print('Error, value does not fall to any of the groups')
    print('Groups: %s' % groups)
    print('Value: %d' % value)
    sys.exit(1)


def preprocess_docs(json_dict, doc_type, key, columns, actions):
    """Returns docs that contains key, doctype, columns and preprocessed
    values. The columns and preprocessed values are in a dict stored as value to
    the key 'columns'"""

    preprocessed_docs = []

    # key: column name, value: list of groups (a group is a list of size two)
    groups_dict = {}

    # generate groups for each column that needs to be grouped
    assert (len(columns) == len(actions)), 'Length of columns and actions should be the same in file %d' % doc_type
    for i in range(len(columns)):
        if actions[i][0] != 'group':
            continue
        curr_values = []
        for curr_doc in json_dict['features']:
            curr_values.append(curr_doc['properties'][columns[i][0]])

        curr_values = [round(x, DECIMAL_PLACES) for x in curr_values]
        groups_dict[columns[i][0]] = generate_groups(curr_values, actions[i][1])

    for feature in json_dict['features']:
        curr_doc = feature['properties']
        p_doc = {}
        p_doc[COUCHDB_KEY] = curr_doc[key]  # store doc's key using uniform name
        p_doc['doc_type'] = doc_type  # use to differentiate aurin data
        p_doc['columns'] = {}  # store preprocessed values here

        for i in range(len(columns)):
            curr_column = columns[i][0]
            if actions[i][0] == 'group':
                # convert numerical to categorical
                p_doc['columns'][curr_column] = get_group(groups_dict[columns[i][0]], curr_doc[curr_column])
            elif actions[i][0] == 'relabel':
                p_doc['columns'][curr_column] = actions[i][1][curr_doc[curr_column]]
        preprocessed_docs.append(p_doc)

    return preprocessed_docs


def upload_aurin_data(db, json_dict, doc_type, key):
    # relevant data are in features[i].properties
    preprocessed_docs = preprocess_docs(json_dict, doc_type, key, AURIN_COLUMNS[doc_type]['columns'], AURIN_COLUMNS[doc_type]['actions'])

    # store preprocessed docs into couchdb
    for curr_doc in preprocessed_docs:
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
