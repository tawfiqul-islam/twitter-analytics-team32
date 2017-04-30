import configparser

config = configparser.ConfigParser()
config['Harvest'] = { 'ConsumerKey' : 'b4bivK0epgUoLUEWIisHyWmZL',
                      'ConsumerSecret' : 'ESyt92sAE9hetlIPXCfkQPAK0409pdUE5D0LDptASwdXnVBfNm',
                      'AccessToken' : '856294076353728512-tkg8rtWtybk82dS56MWXFrFtBI7sH7p',
                      'AccesTokenSecret' : 'j6fh0LfFSJWKEfIh5bWTik6yyCYR5vf9cV3rBMt1aCCmY',
                      'DatabaseIP' : 'http://115.146.92.171:5984/'}

#Note the order of the coords, bounding box from bottom left then top right
#Longtitude then latitude pairs, comma seperated
config['Stream'] = { 'Location' : '140.888036,-39.05559,150.525361,-34.196400',
                     'DatabaseName' : 'victoriastream'}

#The name of the database upon which to crawl and search for more tweets
#By convention, suggested format is dbcrawl = dbstore+user
#Convention is NECESSARY if intended use in conjunction with whole package
config['UserSearch'] = { 'DatabaseCrawl' : 'victoriastreamuser',
                         'DatabaseStore' : 'victoriastream',
                         'MaxTweets' : 50000}

#The name of the database upon which to crawl and search for more tweets
#By convention, suggested format is dbcrawl = dbstore+location
#Convention is NECESSARY if intended use in conjunction with whole package
config['LocationSearch'] = { 'DatabaseCrawl' : 'victoriastreamlocation',
                             'DatabaseStore' : 'victoriastream',
                             'MaxTweets' : 50000}

with open('config.ini', 'w') as configfile:
    config.write(configfile)