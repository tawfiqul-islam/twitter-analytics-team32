import sys
from ast import literal_eval
import configparser
import couchdb
from aurin_data import upload_all_aurin_data
from lga import upload_lga_geojson
from lga import create_view


config = configparser.ConfigParser()
config.read('./config_web.ini')

COUCHDB_URL = config['couchdb']['ip_address'] + ':' + config['couchdb']['port']
COUCHDB_NAME_AURIN = config['couchdb']['db_name_aurin']
COUCHDB_NAME_TWEETS = config['couchdb']['db_name_tweets']

VIEW_TWEETS_LABEL_COUNT = literal_eval(config['couchdb']['view_tweets_label_count'])


if __name__ == '__main__':
    couch = couchdb.Server(COUCHDB_URL)
    try:
        db = couch.create(COUCHDB_NAME_AURIN)
    except couchdb.PreconditionFailed:
        # database with that name exists
        # delete that and create a fresh one
        # TODO delete
        couch.delete(COUCHDB_NAME_AURIN)
        db = couch.create(COUCHDB_NAME_AURIN)
        # print('Error, database with name %s exists' % (COUCHDB_NAME))
        # sys.exit(1)
        # pass

    upload_all_aurin_data(db)

    upload_lga_geojson(db)

    db = couch[COUCHDB_NAME_TWEETS]

    try:
        create_view(db,
                    VIEW_TWEETS_LABEL_COUNT['docid'],
                    VIEW_TWEETS_LABEL_COUNT['view_name'],
                    VIEW_TWEETS_LABEL_COUNT['map_func'],
                    VIEW_TWEETS_LABEL_COUNT['reduce_func'])
    except couchdb.http.ResourceConflict:
        pass

    # TODO delete
    # for row in db.view('%s/_view/%s' % (VIEW_TWEETS_LABEL_COUNT['docid'], VIEW_TWEETS_LABEL_COUNT['view_name']),
                       # group=True,
                       # reduce=True):
    # print row['key'], row['value']
