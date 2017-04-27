import json
import re
import sys
from shapely.geometry import Point, shape
# import couchdb

# TODO store data in couchdb
# DATA_PATH = './static/resources/data/'
# DATA_PATH = './twitter-analytics-team32/Web/static/resources/data/'
DATA_PATH = '../Web/static/resources/data/'

# https://data.gov.au/dataset/vic-local-government-areas-psma-administrative-boundaries
FILENAME_LGA = 'vic-lga.json'

# from aurin
FILENAME_INTERNET_ACCESS = 'LGA11_Internet_Access_at_Home.json'

# TODO delete
# COUCHDB_URL = 'http://127.0.0.1:5984/'


# TODO read from couchdb
def read_lga_file(keep_unincorporated=False):
    """ Preprocess lga name and combine coordinates of features with the same
    lga name """
    with open(DATA_PATH + FILENAME_LGA) as f:
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
        curr_name = feature['properties']['vic_lga__3']
        if '(UNINC)' in curr_name:
            # remove ' (UNINC)'
            curr_name = re.match('(.*) \(.*\)', curr_name).group(1)
        curr_name = curr_name.lower().title()
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
    with open(DATA_PATH + FILENAME_INTERNET_ACCESS) as f:
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
    """ Combine coordinates with the same name and add lga code to each feature.
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


class LGA:
    def __init__(self):
        # key: lga code, value: lga name
        self.lga_code_to_name_dict = {}

        # key: lga name, value: lga code
        self.lga_name_to_code_dict = {}

        # key: 'lga_name', value: dict with 2 keys: 'lga_code' and 'shape'
        self.lga_dict = {}

        lga_geojson_dict, lga_list = read_lga_file()

        self.lga_name_to_code_dict, lga_list_internet_access = \
            read_internet_access()

        diff = set(lga_list).symmetric_difference(set(lga_list_internet_access))
        if (len(diff) != 0):
            print('Error, lga name in "%s" and "%s" does not match' %
                  (FILENAME_LGA, FILENAME_INTERNET_ACCESS))
            sys.exit(1)

        for lga_name, lga_code in self.lga_name_to_code_dict.items():
            self.lga_code_to_name_dict[lga_code] = lga_name

        self.lga_dict = merge_lga_code_and_polygons(self.lga_name_to_code_dict,
                                                    lga_geojson_dict)

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


# TODO delete
ans = ['east gippsland', 'towong', 'bass coast', 'bass coast']
ls = [(147.949, -37.585), (147.534, -36.562), (145.22, -38.48), (145.6, -38.5)]
