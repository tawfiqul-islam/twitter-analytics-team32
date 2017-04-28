import configparser

config = configparser.ConfigParser()
config['Harvest'] = { 'ConsumerKey' : 'eWUVGAAVPs0PH12jl8ZNm3V5A',
                      'ConsumerSecret' : 'VFkfKZkqOTw7DMVAiBZrjKrY4ccDbpwdC3z28bq0F3bFtG4efh',
                      'AccessToken' : '92007701-fPTuS79V3mi9aBqSpYiHwhPnk6Fp6QzhJ6kGkeDS8',
                      'AccesTokenSecret' : '3a4BDmMz2IFylrQITZRzN3RNCDBK6lvwN89UZ0zGx3EBi',
                      'DatabaseIP' : 'http://127.0.0.1:5984/',
                      'DatabaseName' : 'victoriastream'}

#Note the order of the coords, bounding box from bottom left then top right
#Longtitude then latitude pairs, comma seperated
config['Stream'] = { 'Location' : '140.888036,-39.05559,150.525361,-34.196400'}

#The name of the database upon which to crawl and search for more tweets
config['UserSearch'] = { 'DatabaseCrawl' : 'victoriastream'}

with open('config.ini', 'w') as configfile:
    config.write(configfile)