import sys
import configparser


DATA_PATH = './static/resources/data/'


def main():
    if (len(sys.argv) != 2):
        print("Please provide couchdb's ip address without port number")
        sys.exit(1)

    ip_address = sys.argv[1]

    config = configparser.ConfigParser()

    config['couchdb'] = {'port': '5984',
                         'ip_address': ip_address,
                         'db_name_aurin': 'aurin',
                         'key': 'lga_code'}

    config['geojson_file'] = {'lga': DATA_PATH + 'vic-lga.json'}

    config['aurin_json_files'] = {'internet_access': DATA_PATH + 'LGA11_Internet_Access_at_Home.json',
                                  'sitting_hours': DATA_PATH + 'LGA_Sedentary_behaviour__sitting_hours_per_day_.json',
                                  'soft_drink': DATA_PATH + 'LGA_Daily_soft_drink_consumption.json',
                                  'health_risk': DATA_PATH + 'LGA11_Health_Risk_Factors_-_Modelled_Estimate.json'}

    with open('config_web.ini', 'w') as configfile:
        config.write(configfile)


if __name__ == "__main__":
    main()
