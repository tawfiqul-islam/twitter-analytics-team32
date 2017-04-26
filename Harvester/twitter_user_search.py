# To run this code, first edit config_gen.py with your configuration, then:
#
# python[3] config_gen.py
# python[3] twitter_stream.py
# 
# This will start streaming tweets within your specified bounding box
# that will be kept in the couchDB database of your choice.

import tweepy
from tweepy import OAuthHandler
import time
import configparser
import string
import json
import couchdb


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')

    auth = OAuthHandler(config['Harvest']['ConsumerKey'], config['Harvest']['ConsumerSecret'])
    auth.set_access_token(config['Harvest']['AccessToken'], config['Harvest']['AccesTokenSecret'])
    api = tweepy.API(auth)
    couch = couchdb.Server( config['Harvest']['DatabaseIP'])

    