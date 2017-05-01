# To run this code, first edit config_gen.py with your configuration, then:
#
# python[3] config_gen.py
# python[3] twitter_stream.py [options]
#
# --user keeps twitter userIDs in dbname+user. HARDCODED: take note of naming convention!
# --location similarly keeps location twitter IDs. AGAIN, hardcoded beware
# 
# This will start streaming tweets within your specified bounding box
# that will be kept in the couchDB database of your choice.

import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import configparser
import string
import json
import couchdb
import argparse


class MyListener(StreamListener):
    #Custom StreamListener for streaming data
    def __init__(self,db,args):
        self.db = db
        self.args = args

    #When receiving a tweet
    def on_data(self, data):
        try:
            tweet = json.loads(data)
            #Ensure a tweet we are interested in then store in relevant DBs
            if tweet['text']:
                #only store non retweets
                if not tweet['retweeted'] and 'RT @' not in tweet['text']:
                    tweet['_id'] = tweet['id_str']
                    self.db.save(tweet)

                #when keeping user data, store their ID and tweet location
                if args.user and tweet['user']['id_str']:
                    #ensure id_str is available
                    user = {}
                    user['_id'] = tweet['user']['id_str']
                    user['geo'] = tweet['geo']
                    user['coordinates'] = tweet['coordinates']
                    user['place'] = tweet['place']
                    userdb.save(user)

                #when storing location data, store twitter locationID
                if self.args.location and tweet['place']:
                    if tweet['place']['id']:
                        #only add if location ID exists
                        location = {}
                        location['_id'] = tweet['place']['id']
                        locationdb.save(location)

            return True
        except couchdb.http.ResourceConflict as e:
            #Collisions are expected, move on
            pass
        return True

    def on_error(self, status):
        print(status)
        return True

if __name__ == '__main__':
    #Read arguments and parse
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', 
        help='keep track of any twitter user ids and store in <dbname>user, note convention!!', 
        action='store_true')
    parser.add_argument('-l', '--location',
        help='keep track of twitter location ids and store in <dbname>location, note convention!!',
        action='store_true')
    args = parser.parse_args()

    #Set up configuration
    config = configparser.ConfigParser()
    config.read('config.ini')

    auth = OAuthHandler(config['Harvest']['ConsumerKey'], config['Harvest']['ConsumerSecret'])
    auth.set_access_token(config['Harvest']['AccessToken'], config['Harvest']['AccesTokenSecret'])
    api = tweepy.API(auth)
    couch = couchdb.Server( config['Harvest']['DatabaseIP'])
    databasename = config['Stream']['DatabaseName']
    userdatabase = databasename + 'user'
    locationdatabase = databasename + 'location'

    #Open up our couchdb database
    if databasename not in couch:
        db = couch.create(databasename)
    else:
        db = couch[databasename]

    twitter_stream = Stream(auth, MyListener(db=db,args=args))

    #user option enabled
    if args.user:
        if userdatabase not in couch:
            userdb = couch.create(userdatabase)
        else:
            userdb = couch[userdatabase]
        twitter_stream.userdb = userdb

    #location option enabled
    if args.location:
        if locationdatabase not in couch:
            locationdb = couch.create(locationdatabase)
        else:
            locationdb = couch[locationdatabase]
        twitter_stream.locationdb = locationdb

    #This is the bounding box within which we want tweets
    boundingbox = config['Stream']['Location']
    boundingbox = boundingbox.split(',')
    loc1 = float(boundingbox[0])
    loc2 = float(boundingbox[1])
    loc3 = float(boundingbox[2])
    loc4 = float(boundingbox[3])

    #Set up the stream
    twitter_stream.filter(locations=[loc1,loc2,loc3,loc4])
