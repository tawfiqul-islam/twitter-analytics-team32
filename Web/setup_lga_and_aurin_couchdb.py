from aurin_data import upload_all_aurin_data
from lga import upload_lga_geojson

if __name__ == '__main__':
    upload_all_aurin_data()

    upload_lga_geojson()
