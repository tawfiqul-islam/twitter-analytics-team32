import sys
import configparser


DATA_PATH = './static/resources/data/'

MAP_GEOJSON = \
    '''function (doc) {
        if (doc.doc_type == 'lga_geojson_feature') {
            emit(doc.lga_code, doc.columns);
            }
        }
    '''

MAP_AURIN_ALL = \
    '''function (doc) {
        if (doc.lga_code == 0 || doc.doc_type == 'columns_info') {
            // skip these
            return
        }
        var v;
        if (doc.doc_type == 'lga_geojson_feature') {
            // only want LGA name
            scenarios = [1,2,3,4];
            v = {'lga_name': doc.columns.properties.lga_name};
            for (var i=0; i<scenarios.length; i++) {
                emit([scenarios[i], doc.lga_code, doc.doc_type], v);
            }
        } else {
            for (var c in doc.columns) {
                v = {}
                v[c] = doc.columns[c].value;
                for (var i=0; i<doc.columns[c].scenarios.length; i++) {
                    emit([doc.columns[c].scenarios[i], doc.lga_code, doc.doc_type], v);
                }
                }
            }
        }
    '''

MAP_COLUMNS_INFO = \
    '''function (doc) {
        if (doc.doc_type == 'columns_info') {
            for (var f in doc.columns_info) {
                for (var c in doc.columns_info[f]) {
                    for (var i=0; i<doc.columns_info[f][c]['scenarios'].length; i++) {
                        var s = doc.columns_info[f][c]['scenarios'][0]
                        emit([s, c], doc.columns_info[f][c]);
                    }
                }
            }
        }
    }
    '''

MAP_TWEETS_LABEL = \
    '''function (doc) {
        if (doc.lga_code && doc.label != 5) {
            emit(doc.lga_code, doc.label);
        }
    }
    '''

REDUCE_TWEETS_LABEL = \
    '''function (keys, values, rereduce) {
        var result = {'unhappy': 0, 'neutral': 0, 'happy': 0};
        if (rereduce) {
            for (var i=0; i < values.length; i++) {
                result['unhappy'] += values[i]['unhappy'];
                result['neutral'] += values[i]['neutral'];
                result['happy'] += values[i]['happy'];
            }
        } else {
            for (var i=0; i < values.length; i++) {
                if (values[i] == -1) {
                    result['unhappy'] += 1;
                } else if (values[i] == 0) {
                    result['neutral'] += 1;
                } else if (values[i] == 1) {
                    result['happy'] += 1;
                }
            }
        }
        return result;
    }
    '''

MAP_TWEETS_TAG_FOOD = \
    '''function (doc) {
        if (doc.lga_code && doc.tag_food) {
            emit(doc.lga_code, 1);
        }
    }
    '''

MAP_TWEETS_COUNT = \
    '''function (doc) {
        if (doc.lga_code) {
            emit(doc.lga_code, 1);
        }
    }
    '''


def main():
    if (len(sys.argv) != 3):
        print("Please provide couchdb's ip address and port number separated by space, e.g. 'http://127.0.0.1 5984'")
        sys.exit(1)

    ip_address = sys.argv[1]

    port = sys.argv[2]

    config = configparser.ConfigParser()

    config['couchdb'] = {'port': port,
                         'ip_address': ip_address,
                         'db_name_aurin': 'aurin',
                         # TODO
                         'db_name_tweets': 'target_data',
                         # 'db_name_tweets': 'temp_target_data',
                         'key': 'lga_code',  # an emitted key from a map function should at least have this value
                         'exclude_lga_code': [29399],  # this is the code for unincorporated areas
                         'd_doc_lga': {'_id': '_design/lga',
                                       'views': {'features-view': {'map': MAP_GEOJSON}
                                                 }
                                       },
                         'd_doc_scenario': {'_id': '_design/scenario',
                                            'views': {'collation-view': {'map': MAP_AURIN_ALL},
                                                      'columns-view': {'map': MAP_COLUMNS_INFO}
                                                      }
                                            },
                         'd_doc_tweets': {'_id': '_design/tweets',
                                          'views': {'tweets-label-count': {'map': MAP_TWEETS_LABEL,
                                                                           'reduce': REDUCE_TWEETS_LABEL},
                                                    'tweets-tag-food': {'map': MAP_TWEETS_TAG_FOOD,
                                                                        'reduce': '_count'},
                                                    'tweets-count': {'map': MAP_TWEETS_COUNT,  # to get the total number of tweets harvested from each area
                                                                     'reduce': '_count'}
                                                    }
                                          },
                         'scenarios': [1, 2]
                         }

    config['geojson_file'] = {'lga': DATA_PATH + 'vic-lga.json',
                              'doc_type': 'lga_geojson_feature'}

    config['aurin_json_files'] = {'internet_access': DATA_PATH + 'LGA11_Internet_Access_at_Home.json',
                                  'profiles_data': DATA_PATH + 'Local_Government_Area__LGA__profiles_data_2015_for_VIC.json'}

    config['aurin_columns'] = {'internet_access': {'columns': [['internet_tt_3_percent_6_11_6_11', 'Internet Access', 'Percentage of Private Dwellings with Internet Connections']],
                                                   'actions': [['group', 3]],
                                                   'scenarios': [[2]]},
                               # the value in key 'columns' is an array of size three that shows the property name in json file, a short detail, and a longer detail
                               'profiles_data': {'columns': [['ppl_aged_over_18_who_are_current_smokers_perc', 'Smokers', 'Percentage of people aged over 18 who are current smokers'],
                                                             ['ppl_reporting_being_obese_perc', 'Obesity', 'Percentage of people reported being obese'],
                                                             ['ppl_who_are_members_of_a_sports_grp_perc', 'Sports Group', 'Percentage of members of a sports group'],
                                                             ['ppl_drink_sugar_sweetened_soft_drink_every_day_perc', 'Soft Drink', 'Percentage of people who drink sugar-sweetened soft drink every day'],
                                                             ['ppl_who_speak_a_lang_other_english_at_home_perc', 'Non-English Speakers', 'Percentage of people who speak a language other than English at home'],
                                                             ['ppl_who_rated_their_cmty_as_a_pleasant_env_perc', 'Pleasant Environment', 'Percentage of people who rated their community as a pleasant environment'],
                                                             ['ppl_who_are_members_of_a_religious_grp_perc', 'Religous Group', 'Percentage of people who are members of a religious group']
                                                             ],
                                                 # preprocessing action
                                                 'actions': [['group', 3],
                                                             ['group', 3],
                                                             ['group', 3],
                                                             ['group', 3],
                                                             ['group', 3],
                                                             ['group', 3],
                                                             ['group', 3]
                                                             ],
                                                 # which scenarios the column
                                                 # belong to
                                                 'scenarios': [[2],
                                                               [2],
                                                               [2],
                                                               [2],
                                                               [1],
                                                               [1],
                                                               [1]
                                                               ]
                                                 }
                               }

    config['preprocessing'] = {'decimal_places': 2}  # the accuracy of the values that will be shown in the web

    # same format as 'aurin_columns', but without scenario
    config['tweet_columns'] = {'sentiment': {'columns': [['happy', 'Happy', 'Percentage of tweets classified as happy'],
                                                         ['neutral', 'Neutral', 'Percentage of tweets classified as neutral'],
                                                         ['unhappy', 'Unhappy', 'Percentage of tweets classified as unhappy']],
                                             'actions': [['group', 3],
                                                         ['group', 3],
                                                         ['group', 3]]
                                             },
                               'fast_food': {'columns': [['fast_food', 'Fast Food Tweets', 'Percentage of tweets classified as related to fast food']],
                                             'actions': [['group', 3]]
                                             }
                               }

    with open('config_web.ini', 'w') as configfile:
        config.write(configfile)


if __name__ == "__main__":
    main()
