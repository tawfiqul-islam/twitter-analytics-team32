from ast import literal_eval
import configparser
import couchdb
from aurin_data import upload_all_aurin_data
from lga import upload_lga_geojson


config = configparser.ConfigParser()
config.read('./config_web.ini')

COUCHDB_URL = config['couchdb']['ip_address'] + ':' + config['couchdb']['port']
COUCHDB_NAME_AURIN = config['couchdb']['db_name_aurin']
COUCHDB_NAME_TWEETS = config['couchdb']['db_name_tweets']

D_DOC_LGA = literal_eval(config['couchdb']['d_doc_lga'])
D_DOC_SCENARIO = literal_eval(config['couchdb']['d_doc_scenario'])
D_DOC_TWEETS = literal_eval(config['couchdb']['d_doc_tweets'])


def create_view(db, design_doc):
    try:
        db.save(design_doc)
    except couchdb.http.ResourceConflict:
        print('Warning, the following design doc already exists in %s' % (db))
        print(design_doc)


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

    create_view(db, D_DOC_SCENARIO)
    create_view(db, D_DOC_LGA)

    try:
        db = couch[COUCHDB_NAME_TWEETS]
    except couchdb.http.ResourceNotFound:
        db = couch.create(COUCHDB_NAME_TWEETS)

    create_view(db, D_DOC_TWEETS)

    # TODO delete
    # for row in db.view('%s/_view/%s' % (VIEW_TWEETS_LABEL_COUNT['docid'], VIEW_TWEETS_LABEL_COUNT['view_name']),
    # group=True,
    # reduce=True):
    # print row['key'], row['value']
