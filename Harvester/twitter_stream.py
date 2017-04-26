# To run this code, first edit config_gen.py with your configuration, then:
#
# python[3] config_gen.py
# python[3] twitter_stream.py
# 
# This will start streaming tweets within your specified bounding box
# that will be kept in the couchDB database of your choice.

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
    config.read('config.ini')

    auth = OAuthHandler(config['Harvest']['ConsumerKey'], config['Harvest']['ConsumerSecret'])
    auth.set_access_token(config['Harvest']['AccessToken'], config['Harvest']['AccesTokenSecret'])
    api = tweepy.API(auth)
    couch = couchdb.Server( config['Harvest']['DatabaseIP'])

    if config['Harvest']['DatabaseName'] not in couch:
        db = couch.create(config['Harvest']['DatabaseName'])
    else:
        db = couch[config['Harvest']['DatabaseName']]
        
    twitter_stream = Stream(auth, MyListener(db))

    boundingbox = config['Stream']['Location']
    boundingbox = boundingbox.split(',')
    loc1 = float(boundingbox[0])
    loc2 = float(boundingbox[1])
    loc3 = float(boundingbox[2])
    loc4 = float(boundingbox[3])
    twitter_stream.filter(languages=["en"], locations=[loc1,loc2,loc3,loc4])
