import configparser
from ast import literal_eval
import couchdb
from aurin_data import generate_groups


config = configparser.ConfigParser()
config.read('../Web/config_web.ini')

COUCHDB_URL = config['couchdb']['ip_address'] + ':' + config['couchdb']['port']
COUCHDB_NAME_TWEETS = config['couchdb']['db_name_tweets']

# rows from different AURIN data are joined based on this key
COUCHDB_KEY = config['couchdb']['key']

TWEET_COLUMNS = dict(config['tweet_columns'])
for key in TWEET_COLUMNS:
    TWEET_COLUMNS[key] = literal_eval(TWEET_COLUMNS[key])

DECIMAL_PLACES = int(config['preprocessing']['decimal_places'])
ACCURATE_TO = 10 ** -DECIMAL_PLACES

D_DOC_TWEETS = literal_eval(config['couchdb']['d_doc_tweets'])

DECIMAL_PLACES = int(config['preprocessing']['decimal_places'])


def construct_column_infos(key, rows):
    column_infos = {}
    for i in range(len(TWEET_COLUMNS[key]['columns'])):
        label = TWEET_COLUMNS[key]['columns'][i][0]
        curr_col = {}
        curr_col['title'] = TWEET_COLUMNS[key]['columns'][i][1]
        curr_col['detail'] = TWEET_COLUMNS[key]['columns'][i][2]
        if (TWEET_COLUMNS[key]['actions'][i][0] == 'group'):
            # generate list of values
            list_of_values = []
            for lga_code in rows:
                list_of_values.append(rows[lga_code][label])
            curr_col['groups'] = generate_groups(list_of_values,
                                                 TWEET_COLUMNS[key]['actions'][i][1])
        column_infos[label] = curr_col
    return column_infos


def read_sentiment_from_couchdb(db):
    result = {'rows': {}}

    # 'rows' is a dict instead of a list so that merging with aurin data is easy
    # 'rows' has key: LGA code, value: a dict containing the percentage of each
    # label (happy, neutral, unhappy)
    for row in db.view('%s/_view/%s' % (D_DOC_TWEETS['_id'], 'tweets-label-count'),
                       group=True,
                       reduce=True):
        # get total of each key
        total = float(sum(row['value'].values()))

        # get percentage
        result['rows'][row['key']] = {}
        for label in row['value']:
            result['rows'][row['key']][label] = round(row['value'][label] / total * 100.0,
                                                      DECIMAL_PLACES)

        # get average sentiment (happy = +1, unhappy = -1, neutral = 0)
        average_sentiment = (row['value']['happy'] - row['value']['unhappy']) / total
        result['rows'][row['key']]['average_sentiment'] = round(average_sentiment,
                                                                DECIMAL_PLACES)

    # 'column_infos' contains title, detail and groups
    result['column_infos'] = construct_column_infos('sentiment', result['rows'])
    return result


def read_count_from_couchdb(db):
    result = {'rows': {}}

    for row in db.view('%s/_view/%s' % (D_DOC_TWEETS['_id'], 'tweets-count'),
                       group=True,
                       reduce=True):
        lga_code = row['key']
        result['rows'][lga_code] = {}
        # row has only one column
        col_name = TWEET_COLUMNS['tweet_count']['columns'][0][0]
        result['rows'][lga_code][col_name] = row['value']
    result['column_infos'] = construct_column_infos('tweet_count', result['rows'])
    return result


def read_total_tweets_from_couchdb(db):
    '''Reads total tweet count of each LGA area'''
    result = {}
    for row in db.view('%s/_view/%s' % (D_DOC_TWEETS['_id'], 'tweets-count'),
                       group=True,
                       reduce=True):
        result[row['key']] = row['value']
    return result


def read_fast_food_from_couchdb(db):

    result = {'column_infos': {}, 'rows': {}}

    count_dict = read_total_tweets_from_couchdb(db)

    for row in db.view('%s/_view/%s' % (D_DOC_TWEETS['_id'], 'tweets-tag-food'),
                       group=True,
                       reduce=True):
        lga_code = row['key']
        result['rows'][lga_code] = {}
        # row has only one column
        col_name = TWEET_COLUMNS['fast_food']['columns'][0][0]

        food_count = float(row['value'])
        total_count = count_dict[lga_code]
        result['rows'][lga_code][col_name] = round(food_count / total_count * 100.0,
                                                   DECIMAL_PLACES)

    # 'column_infos' contains title, detail and groups
    result['column_infos'] = construct_column_infos('fast_food', result['rows'])
    return result


def read_tweet_scenario_from_couchdb(n):

    couch = couchdb.Server(COUCHDB_URL)
    db = couch[COUCHDB_NAME_TWEETS]

    if n == 1:
        return read_sentiment_from_couchdb(db)
    elif n == 2:
        return read_fast_food_from_couchdb(db)
    return None
