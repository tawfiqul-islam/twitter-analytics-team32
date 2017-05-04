import configparser
from ast import literal_eval
import sys
import json
import couchdb
from bisect import bisect_right
from lga import create_view


config = configparser.ConfigParser()
config.read('./config_web.ini')

COUCHDB_URL = config['couchdb']['ip_address'] + ':' + config['couchdb']['port']
COUCHDB_NAME = config['couchdb']['db_name_aurin']

# rows from different AURIN data are joined based on this key
COUCHDB_KEY = config['couchdb']['key']

EXCLUDE_LGA_CODE = literal_eval(config['couchdb']['exclude_lga_code'])

FILENAMES_AURIN = config['aurin_json_files']

AURIN_COLUMNS = dict(config['aurin_columns'])
for key in AURIN_COLUMNS:
    AURIN_COLUMNS[key] = literal_eval(AURIN_COLUMNS[key])

DECIMAL_PLACES = int(config['aurin_preprocessing']['decimal_places'])
ACCURATE_TO = 10 ** -DECIMAL_PLACES

VIEW_AURIN_ALL = literal_eval(config['couchdb']['view_aurin_all'])
VIEW_COLUMNS_INFO = literal_eval(config['couchdb']['view_columns_info'])


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
    list
    """
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


def generate_docs(json_dict, doc_type, key, columns, actions, scenarios):
    """Returns list of docs to be stored in couchdb. The first element is the
    'columns_info' and the rest are rows."""

    # store two type of data: a 'columns_info' and rows
    docs = []

    # generate groups for each column that needs to be grouped
    assert (len(columns) == len(actions) == len(scenarios)), 'Length of columns, actions and scenarios should be the same in file %d' % doc_type
    columns_info = {'doc_type': 'columns_info', 'columns_info': {doc_type: {}}}
    for i in range(len(columns)):
        curr_column_name = columns[i][0]
        if actions[i][0] != 'group':
            continue

        # convert numerical values to categorical
        # generate list of values for a particular column
        curr_values = []
        for feature in json_dict['features']:
            curr_doc = feature['properties']
            if curr_doc[key] in EXCLUDE_LGA_CODE:
                # skip row
                continue
            curr_values.append(curr_doc[curr_column_name])
        curr_values = [round(x, DECIMAL_PLACES) for x in curr_values]
        curr_groups = generate_groups(curr_values, actions[i][1])
        for g in range(len(curr_groups)):
            curr_groups[g] = (round(curr_groups[g][0], DECIMAL_PLACES), round(curr_groups[g][1], DECIMAL_PLACES))
        curr_column_info = {}
        curr_column_info['groups'] = curr_groups
        curr_column_info['title'] = columns[i][1]
        curr_column_info['detail'] = columns[i][2]
        curr_column_info['scenarios'] = scenarios[i]
        columns_info['columns_info'][doc_type][curr_column_name] = curr_column_info
    docs.append(columns_info)

    # build list of rows
    for feature in json_dict['features']:
        curr_property = feature['properties']
        if curr_property[key] in EXCLUDE_LGA_CODE:
            # skip row
            continue
        curr_doc = {}
        curr_doc[COUCHDB_KEY] = curr_property[key]  # store doc's key using uniform name
        curr_doc['doc_type'] = doc_type  # use to differentiate aurin data
        curr_doc['columns'] = {}  # store preprocessed values here

        for i in range(len(columns)):
            curr_col_name = columns[i][0]
            curr_doc['columns'][curr_col_name] = {}
            curr_doc['columns'][curr_col_name]['value'] = curr_property[curr_col_name]
            curr_doc['columns'][curr_col_name]['scenarios'] = scenarios[i]
        docs.append(curr_doc)

    return docs


def upload_aurin_data(db, json_dict, doc_type, key):
    # relevant data are in features[i].properties
    docs = generate_docs(json_dict, doc_type, key,
                         AURIN_COLUMNS[doc_type]['columns'],
                         AURIN_COLUMNS[doc_type]['actions'],
                         AURIN_COLUMNS[doc_type]['scenarios'])

    # store preprocessed docs into couchdb
    for curr_doc in docs:
        db.save(curr_doc)


def upload_all_aurin_data(db):
    for aurin_data_title, aurin_data_filename in FILENAMES_AURIN.items():
        json_dict = read_json(aurin_data_filename)

        if (aurin_data_filename[-5:] != '.json'):
            print('Error on reading %s' % aurin_data_filename)
            print('AURIN JSON files should have the extension .json')
            sys.exit(1)
        metadata_filename = aurin_data_filename[:-5] + '_metadata.json'
        key = get_key(metadata_filename)
        upload_aurin_data(db, json_dict, aurin_data_title, key)
    create_view(db, VIEW_AURIN_ALL['docid'], VIEW_AURIN_ALL['view_name'], VIEW_AURIN_ALL['map_func'])
    create_view(db, VIEW_COLUMNS_INFO['docid'], VIEW_COLUMNS_INFO['view_name'], VIEW_COLUMNS_INFO['map_func'])


def read_scenario_from_couchdb(which_scenario):
    """Join all AURIN data by LGA code to form a dictionary with two keys:
        'rows' and 'column_titles'. Unincorporated areas are excluded.
    """
    couch = couchdb.Server(COUCHDB_URL)
    db = couch[COUCHDB_NAME]

    result = {}
    result['rows'] = []
    curr_lga_code = -1
    for row in db.view('%s/_view/%s' % (VIEW_AURIN_ALL['docid'], VIEW_AURIN_ALL['view_name']),
                       startkey=[which_scenario],
                       endkey=[which_scenario+1]):
        if curr_lga_code != row['key'][1]:
            # encounters a new LGA code
            curr_lga_code = row['key'][1]
            curr_group = {}
            curr_group[COUCHDB_KEY] = row['key'][1]
            result['rows'].append(curr_group)
        assert (len(row['value']) == 1), "The property 'value' must have only one property"
        curr_column_name = row['value'].keys()[0]
        assert (curr_column_name not in curr_group), "Column name must be unique"
        curr_group[curr_column_name] = row['value'][curr_column_name]

    result['column_infos'] = {}
    for row in db.view('%s/_view/%s' % (VIEW_COLUMNS_INFO['docid'], VIEW_COLUMNS_INFO['view_name']),
                       startkey=[which_scenario],
                       endkey=[which_scenario+1]):
        curr_column_name = row['key'][1]
        assert (curr_column_name not in result['column_infos']),  "Column name must be unique"
        result['column_infos'][curr_column_name] = row['value']
    return result
