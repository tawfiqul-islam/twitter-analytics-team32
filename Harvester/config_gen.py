import configparser

config = configparser.ConfigParser()
config['Harvest'] = { 'ConsumerKey' : 'b4bivK0epgUoLUEWIisHyWmZL',
                      'ConsumerSecret' : 'ESyt92sAE9hetlIPXCfkQPAK0409pdUE5D0LDptASwdXnVBfNm',
                      'AccessToken' : '856294076353728512-tkg8rtWtybk82dS56MWXFrFtBI7sH7p',
                      'AccesTokenSecret' : '    j6fh0LfFSJWKEfIh5bWTik6yyCYR5vf9cV3rBMt1aCCmY',
                      'DatabaseIP' : 'http://127.0.0.1:5984/',
                      'DatabaseName' : 'victoriastream'}

#Note the order of the coords, bounding box from bottom left then top right
#Longtitude then latitude pairs, comma seperated
config['Stream'] = { 'Location' : '140.888036,-39.05559,150.525361,-34.196400'}

#The name of the database upon which to crawl and search for more tweets
config['UserSearch'] = { 'DatabaseCrawl' : 'victoriastream'}

with open('config.ini', 'w') as configfile:
    config.write(configfile)