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
        if (doc.lga_code == 0) {
            // skip these
            return
        }
        var v;
        if (doc.doc_type == 'lga_geojson_feature') {
            // only want LGA name
            v = {'lga_name': doc.columns.properties.lga_name};
        } else {
            // use all
            v = doc.columns;
        }
        emit([doc.lga_code, doc.doc_type], v);
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
                         'view_aurin_all': {'docid': '_design/aurin_all',
                                            'view_name': 'collation-view',
                                            'map_func': VIEW_AURIN_ALL_MAP}}

    config['geojson_file'] = {'lga': DATA_PATH + 'vic-lga.json',
                              'doc_type': 'lga_geojson_feature'}

    config['aurin_json_files'] = {'internet_access': DATA_PATH + 'LGA11_Internet_Access_at_Home.json',
                                  'sitting_hours': DATA_PATH + 'LGA_Sedentary_behaviour__sitting_hours_per_day_.json',
                                  'soft_drink': DATA_PATH + 'LGA_Daily_soft_drink_consumption.json',
                                  'health_risk': DATA_PATH + 'LGA11_Health_Risk_Factors_-_Modelled_Estimate.json'}

    config['aurin_columns'] = {'internet_access': {'columns': [['internet_tt_3_percent_6_11_6_11', 'Internet Access', 'Percentage of Private Dwellings with Internet Connections']],
                                                   'actions': [['group', 3]]},
                               'sitting_hours': {'columns': [['significance', 'Sitting Behaviour', "Proportion of People Who Sit for 7 Hours or More per Day Relative to Victoria's Average"]],
                                                 'actions': [['relabel', {'better': 'low',
                                                                          'none': 'medium',
                                                                          'worse': 'high'}]]},
                               'soft_drink': {'columns': [['significance', 'Soft Drink Consumption', "Soft Drink Consumption Relative to Victoria's Average"]],
                                              'actions': [['relabel', {'caution': 'low',
                                                                       'better': 'low',
                                                                       'none': 'medium',
                                                                       'worse': 'high'}]]},
                               'health_risk': {'columns': [['smokers_me_2_rate_3_11_7_13', 'Smokers', 'Percentage of Current smokers (modelled estimate)'],
                                                           ['obese_p_me_2_rate_3_11_7_13', 'Obesity', 'Percentage of Obese Persons (modelled estimate)'],
                                                           ['alcohol_cons_2_rate_3_11_7_13', 'Alcohol Consumption', 'Percentage of High Risk Alcohol Consumption (modelled estimate)']],
                                               'actions': [['group', 3], ['group', 3], ['group', 3]]}}

    config['aurin_preprocessing'] = {'decimal_places': 2}

    with open('config_web.ini', 'w') as configfile:
        config.write(configfile)


if __name__ == "__main__":
    main()
