import configparser

config = configparser.ConfigParser()
config['Harvest'] = { 'ConsumerKey' : 'eWUVGAAVPs0PH12jl8ZNm3V5A',
                      'ConsumerSecret' : 'VFkfKZkqOTw7DMVAiBZrjKrY4ccDbpwdC3z28bq0F3bFtG4efh',
                      'AccessToken' : '92007701-fPTuS79V3mi9aBqSpYiHwhPnk6Fp6QzhJ6kGkeDS8',
                      'AccesTokenSecret' : '3a4BDmMz2IFylrQITZRzN3RNCDBK6lvwN89UZ0zGx3EBi',
                      'DatabaseIP' : 'http://115.146.92.169:5984/'}

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

#IP to identiy which VM we are, VM1 = db
config['VMTag'] = {'VM1' : '115.146.92.169',
                   'VM2' : '115.146.93.16',
                   'VM3' : '115.146.92.181',
                   'VM4' : '115.146.92.169'}


with open('config.ini', 'w') as configfile:
    config.write(configfile)