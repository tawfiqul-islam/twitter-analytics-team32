import sys
import configparser


DATA_PATH = './static/resources/data/'

VIEW_GEOJSON_MAP = \
    '''function (doc) {
        if (doc.doc_type == 'lga_geojson_feature') {
            emit(doc.lga_code, doc.columns);
            }
        }
    '''

VIEW_AURIN_ALL_MAP = \
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

VIEW_COLUMNS_INFO_MAP = \
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


def main():
    if (len(sys.argv) != 2):
        print("Please provide couchdb's ip address without port number")
        sys.exit(1)

    ip_address = sys.argv[1]

    config = configparser.ConfigParser()

    config['couchdb'] = {'port': '5984',
                         'ip_address': ip_address,
                         'db_name_aurin': 'aurin',
                         'key': 'lga_code',
                         'exclude_lga_code': [29399],
                         'view_geojson': {'docid': '_design/lga',
                                          'view_name': 'features-view',
                                          'map_func': VIEW_GEOJSON_MAP},
                         'view_aurin_all': {'docid': '_design/aurin-all',
                                            'view_name': 'collation-view',
                                            'map_func': VIEW_AURIN_ALL_MAP},
                         'view_columns_info': {'docid': '_design/columns_info',
                                               'view_name': 'columns-info-view',
                                               'map_func': VIEW_COLUMNS_INFO_MAP}
                         }

    config['geojson_file'] = {'lga': DATA_PATH + 'vic-lga.json',
                              'doc_type': 'lga_geojson_feature'}

    config['aurin_json_files'] = {'internet_access': DATA_PATH + 'LGA11_Internet_Access_at_Home.json',
                                  'profiles_data': DATA_PATH + 'Local_Government_Area__LGA__profiles_data_2015_for_VIC.json'}

    config['aurin_columns'] = {'internet_access': {'columns': [['internet_tt_3_percent_6_11_6_11', 'Internet Access', 'Percentage of Private Dwellings with Internet Connections']],
                                                   'actions': [['group', 3]],
                                                   'scenarios': [[3]]},
                               'profiles_data': {'columns': [['ppl_aged_over_18_who_are_current_smokers_perc', 'Smokers', 'Percentage of people aged over 18 who are current smokers'],
                                                             ['ppl_reporting_being_obese_perc', 'Obesity', 'Percentage of people reported being obese'],
                                                             ['ppl_who_are_members_of_a_sports_grp_perc', 'Sports Group', 'Percentage of members of a sports group'],
                                                             ['ppl_drink_sugar_sweetened_soft_drink_every_day_perc', 'Soft Drink', 'Percentage of people who drink sugar-sweetened soft drink every day']
                                                             ],
                                                 # preprocessing action
                                                 'actions': [['group', 3],
                                                             ['group', 3],
                                                             ['group', 3],
                                                             ['group', 3]],
                                                 # which scenarios the column
                                                 # belong to
                                                 'scenarios': [[3],
                                                               [3],
                                                               [3],
                                                               [3]]
                                                 }
                               }

    config['aurin_preprocessing'] = {'decimal_places': 2}

    with open('config_web.ini', 'w') as configfile:
        config.write(configfile)


if __name__ == "__main__":
    main()
