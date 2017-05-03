import sys
import configparser
import couchdb
from aurin_data import upload_all_aurin_data
from lga import upload_lga_geojson


config = configparser.ConfigParser()
config.read('./config_web.ini')

COUCHDB_URL = config['couchdb']['ip_address'] + ':' + config['couchdb']['port']
COUCHDB_NAME = config['couchdb']['db_name_aurin']


if __name__ == '__main__':
    couch = couchdb.Server(COUCHDB_URL)
    try:
        db = couch.create(COUCHDB_NAME)
    except couchdb.PreconditionFailed:
        # database with that name exists
        # delete that and create a fresh one
        # TODO delete
        couch.delete(COUCHDB_NAME)
        db = couch.create(COUCHDB_NAME)
        # print('Error, database with name %s exists' % (COUCHDB_NAME))
        # sys.exit(1)

    upload_all_aurin_data(db)

    upload_lga_geojson(db)
