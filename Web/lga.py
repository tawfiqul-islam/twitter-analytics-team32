import configparser
from ast import literal_eval
import couchdb
import json
import re
import sys
from shapely.geometry import Point, shape
from math import radians, cos, sin, asin, sqrt
# import couchdb


config = configparser.ConfigParser()
config.read('../Web/config_web.ini')

COUCHDB_URL = config['couchdb']['ip_address'] + ':' + config['couchdb']['port']
COUCHDB_NAME = config['couchdb']['db_name_aurin']

# TODO change 'lga_code' to COUCHDB_KEY
# rows from different AURIN data are joined based on this key
COUCHDB_KEY = config['couchdb']['key']

# https://data.gov.au/dataset/vic-local-government-areas-psma-administrative-boundaries
FILENAME_LGA = config['geojson_file']['lga']
LGA_GEOJSON_DOC_TYPE = config['geojson_file']['doc_type']

# needed to get the lga area code
FILENAME_INTERNET_ACCESS = config['aurin_json_files']['internet_access']

D_DOC_LGA = literal_eval(config['couchdb']['d_doc_lga'])


# TODO read from couchdb
def read_lga_file(keep_unincorporated=False):
    """ Preprocess lga name and combine coordinates of features with the same
    lga name """
    with open(FILENAME_LGA) as f:
        lga_geojson_dict = json.load(f)

    # key: lga name, value: index in array
    lga_name_to_index_dict = {}

    # geojson with preprocessed lga name (unincorporated is always kept)
    # and feature with the same lga name is combined
    lga_geojson_dict2 = {}
    for key, value in lga_geojson_dict.items():
        # copy key and values except 'features'
        if key == 'features':
            continue
        lga_geojson_dict2[key] = value
    lga_geojson_dict2['features'] = []

    i = 0
    for feature in lga_geojson_dict['features']:
        curr_name = feature['properties']['vic_lga__3'].lower().title()
        if curr_name in lga_name_to_index_dict:
            # add coordinates to the relevant feature
            curr_coordinates = feature['geometry']['coordinates']
            j = lga_name_to_index_dict[curr_name]
            assert(lga_geojson_dict2['features'][j]['properties']['lga_name'] ==
                   curr_name)
            existing_coordinates = \
                lga_geojson_dict2['features'][j]['geometry']['coordinates']
            existing_coordinates += curr_coordinates
        else:
            # feature with the same name does not exist, so add it
            assert(len(lga_geojson_dict2['features']) == i)
            lga_geojson_dict2['features'].append(feature)
            lga_geojson_dict2['features'][i]['properties']['lga_name'] = \
                curr_name
            lga_name_to_index_dict[curr_name] = i
            i += 1
    lga_geojson_dict2['totalFeatures'] = len(lga_geojson_dict2['features'])

    # generate list of lga name
    lga_list = []
    for feature in lga_geojson_dict2['features']:
        curr_name = feature['properties']['vic_lga__3']
        if (('(UNINC)' in curr_name) and not keep_unincorporated):
            # skip unincorporated area
            continue
        lga_list.append(feature['properties']['lga_name'])

    return lga_geojson_dict2, lga_list


# TODO read from couchdb
def read_internet_access(keep_unincorporated=False):
    with open(FILENAME_INTERNET_ACCESS) as f:
        internet_access = json.load(f)
    lga_list_internet_access = []
    lga_name_to_code_dict = {}
    for feature in internet_access['features']:
        curr_name = feature['properties']['area_name']

        # preprocess area name
        # use space instead of '-' so 'colac-otway' becomes 'colac otway'
        if curr_name == 'Unincorporated Vic':
            if not keep_unincorporated:
                # skip unincorporated
                continue
        else:
            # remove ' (C)', ' (S)', etc.
            curr_name = re.match('(.*) \(.*\)', curr_name).group(1)

        curr_name = curr_name.lower().replace('-', ' ').title()
        lga_list_internet_access.append(curr_name)
        lga_name_to_code_dict[curr_name] = feature['properties']['area_code']

    return lga_name_to_code_dict, lga_list_internet_access


def merge_lga_code_and_polygons(lga_name_to_code_dict, lga_geojson_dict):
    """Add lga code to 'lga_geojson_dict' and generate a dict where
    each lga name has its code and shape.
    One area might contain more than one polygon.
    Assumes that the keys in the two dictionaries are the same.
    """
    lga_dict = {}
    for feature in lga_geojson_dict['features']:
        lga_name = feature['properties']['lga_name']
        lga_dict[lga_name] = {}
        if lga_name in lga_name_to_code_dict:
            lga_code = lga_name_to_code_dict[lga_name]
        else:
            # code does not exist
            lga_code = 0
        lga_dict[lga_name]['lga_code'] = lga_code
        feature['properties']['lga_code'] = lga_code
        lga_dict[lga_name]['shape'] = shape(feature['geometry'])
    return lga_dict


def get_lga_geojson():
    """Combine coordinates with the same name and add lga code to each feature.
    """
    lga_geojson_dict, lga_list = read_lga_file()

    lga_name_to_code_dict, lga_list_internet_access = read_internet_access()

    diff = set(lga_list).symmetric_difference(set(lga_list_internet_access))
    if (len(diff) != 0):
        print('Error, lga name in "%s" and "%s" does not match' %
              (FILENAME_LGA, FILENAME_INTERNET_ACCESS))
        sys.exit(1)

    # put lga code in each feature
    for feature in lga_geojson_dict['features']:
        lga_name = feature['properties']['lga_name']
        if lga_name in lga_name_to_code_dict:
            lga_code = lga_name_to_code_dict[lga_name]
        else:
            # code does not exist
            lga_code = 0
        feature['properties']['lga_code'] = lga_code
    return lga_geojson_dict


# TODO receive db as arg
def upload_lga_geojson(db):
    lga_geojson_dict = get_lga_geojson()
    for feature in lga_geojson_dict['features']:
        curr_doc = {}
        curr_doc['doc_type'] = LGA_GEOJSON_DOC_TYPE
        curr_doc[COUCHDB_KEY] = feature['properties'][COUCHDB_KEY]
        curr_doc['columns'] = {}
        curr_doc['columns']['properties'] = {}
        curr_doc['columns']['properties']['lga_name'] = feature['properties']['lga_name']
        curr_doc['columns']['geometry'] = feature['geometry']
        db.save(curr_doc)


# copied from
# http://stackoverflow.com/questions/15736995/how-can-i-quickly-estimate-the-distance-between-two-latitude-longitude-points
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km


def read_lga_geojson_from_couchdb():
    """Similar to read_lga_file(), but with three differences. First, this reads
    from couchdb instead of file. Second no need to do some preprocessing.
    Third, only return one variable"""
    couch = couchdb.Server(COUCHDB_URL)
    db = couch[COUCHDB_NAME]

    lga_geojson_dict = {}
    lga_geojson_dict['features'] = []
    lga_geojson_dict['type'] = 'FeatureCollection'
    feature_count = 0

    for row in db.view('%s/_view/%s' % (D_DOC_LGA['_id'], 'features-view')):
        row['value']['properties'][COUCHDB_KEY] = row['key']
        row['value']['type'] = 'Feature'
        lga_geojson_dict['features'].append(row['value'])
        feature_count += 1
        # TODO delete
        if feature_count > 20:
            break

    lga_geojson_dict['totalFeatures'] = feature_count
    return lga_geojson_dict


class LGA:
    def __init__(self):
        # key: lga code, value: lga name
        self.lga_code_to_name_dict = {}

        # key: lga name, value: lga code
        self.lga_name_to_code_dict = {}

        # key: 'lga_name', value: dict with 2 keys: 'lga_code' and 'shape'
        self.lga_dict = {}

        self.lga_geojson_dict = {}

        self.lga_geojson_dict = read_lga_geojson_from_couchdb()

        # create name_to_code and code_to_name dict excluding unincorporated
        # areas
        for feature in self.lga_geojson_dict['features']:
            lga_name = feature['properties']['lga_name']
            lga_code = feature['properties']['lga_code']
            if 'Uninc' in lga_name:
                # dont want to store code-name and name-code mapping for
                # unincorporated areas because they all share the same code (0)
                continue
            self.lga_name_to_code_dict[lga_name] = lga_code
            self.lga_code_to_name_dict[lga_code] = lga_name

        self.lga_dict = merge_lga_code_and_polygons(self.lga_name_to_code_dict,
                                                    self.lga_geojson_dict)

    def get_code_from_coordinates(self, longitude, lattitude):
        """Returns an int representing the relevant lga code.
        Returns 0 if the given longitude and lattitude is not in any
        of Victoria's LGA. Unincorporated areas are excluded.
        """
        curr_point = Point(longitude, lattitude)
        for key, value in self.lga_dict.items():
            for polygon in value['shape']:
                if polygon.contains(curr_point):
                    return value['lga_code']
        # none of the given area
        return 0

    def code_to_name(self, lga_code):
        """Return the relevant lga name. If lga_code is not valid, return
        None"""
        if lga_code in self.lga_code_to_name_dict:
            return self.lga_code_to_name_dict[lga_code]
        else:
            return None

    def is_code_valid(self, lga_code):
        """Return True if the given LGA code is valid"""
        return lga_code in self.lga_code_to_name_dict.keys()

    def get_centre_coord_and_radius(self):
        """Returns a dictionary with key: LGA name, value: d2. Where d2 is a
        dictionary with three keys: 'lga_code', 'centre_coord', 'radius'. Radius
        is in km. Coordinate is a list [long, lat]"""

        result = {}
        for lga_name in self.lga_dict:
            shape = self.lga_dict[lga_name]['shape']
            lga_code = self.lga_dict[lga_name][COUCHDB_KEY]

            curr = {}
            curr[COUCHDB_KEY] = lga_code
            minx, miny, maxx, maxy = shape.bounds
            curr['centre_coord'] = [(minx+maxx)/2, (miny+maxy)/2]
            curr['radius'] = haversine(curr['centre_coord'][0],
                                       curr['centre_coord'][1],
                                       minx,
                                       miny)
            result[lga_name] = curr
        return result
