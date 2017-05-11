
HOW TO RUN

make sure flask and shapely are installed.
If not, do a pip install
pip install flask
pip install shapely


Setup configuration file

python config_web.py <couchdb-ip> <couchdb port>

for example: python config_web.py http://115.146.92.169 5986


Upload GeoJSON and Aurin data into database
python setup_lga_and_aurin_couchdb.py


Run web server
sudo python app.py
