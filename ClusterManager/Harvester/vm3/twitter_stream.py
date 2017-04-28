# To run this code, first edit config.py with your configuration, then:
#
# mkdir data
# python twitter_stream_download.py -q apple -d data
# 
# It will produce the list of tweets for the query "apple" 
# in the file data/stream_apple.json

import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import time
import configparser
import string
import json
import couchdb


class MyListener(StreamListener):
    """Custom StreamListener for streaming data."""
    def on_data(self, data):
        try:
            tweet = json.loads(data)

            if 'text' in tweet:
                if not tweet['retweeted'] and 'RT @' not in tweet:
                    tweet['_id'] = tweet['id_str']
                    tweet['harvesterType'] = 'BoundingBoxStream'
                    db.save(tweet)
            return True
        except Exception as e:
            print(e)
            pass
        return True

    def on_error(self, status):
        print(status)
        return True

if __name__ == '__main__':
    config = configparser.ConfigParser()

    # Read the Config File

    config.read('config.ini')
    consumerKey = config['HarvestConfig']['ConsumerKey']
    consumerSecret = config['HarvestConfig']['ConsumerSecret']
    accessToken = config['HarvestConfig']['AccessToken']
    accessTokenSecret = config['HarvestConfig']['AccesTokenSecret']
    auth = OAuthHandler( consumerKey, consumerSecret)
    auth.set_access_token( accessToken, accessTokenSecret )

    api = tweepy.API(auth)
    databaseIP = config['HarvestConfig']['DatabaseIP']
    databaseName = config['HarvestConfig']['DatabaseName']
    couch = couchdb.Server(databaseIP)
    if  databaseName not in couch:
    	db = couch.create(databaseName)
    else:
    	db = couch[databaseName]
    twitter_stream = Stream(auth, MyListener(db))

    boundingbox = config['HarvestConfig']['Location']
    boundingbox = boundingbox.split(',')
    loc1 = float(boundingbox[0])
    loc2 = float(boundingbox[1])
    loc3 = float(boundingbox[2])
    loc4 = float(boundingbox[3])

    twitter_stream.filter(languages=["en"], locations=[loc1,loc2,loc3,loc4])
