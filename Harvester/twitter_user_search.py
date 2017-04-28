# To run this code, first edit config_gen.py with your configuration, then:
#
# python[3] config_gen.py
# python[3] twitter_user_search.py
#
# Given a database name (say, x) this will assume an existing database of just userIDs
# at "x + user" exists which this will search for past tweets and save back into x
#
# Furthermore, if the new tweet obtained from searching user past history has no
# location information, the existing information is used instead and past tweets
# are assumed to be from the same location.
# 
# Optionally, with the -n option this program will instead crawl and find users
# before performing a similar task of finding past tweets
#
# ALso, by default any users that are searched for will not be deleted from the
# user database. However, to minimise re-searching users already done, the 
# -d option will instead DELETE userIDs in the database.

import tweepy
from tweepy import OAuthHandler
import configparser
import string
import json
import couchdb
import argparse

#Crawl existing db and make a list of its users
def add_users(db):
    for tweetID in db:
                tweet = db[tweetID]
                try:
                    user = {}
                    user['_id'] = tweet['user']['id_str']
                    user['geo'] = tweet['geo']
                    user['coordinates'] = tweet['coordinates']
                    user['place'] = tweet['place']
                    userdb.save(user)
                except Exception as e:
                    print(e)
                    pass

#Find user's past tweets based on ID and store in given database
def add_tweets(userID, userdb, db, args):
    status_list = api.user_timeline(userID)
    doc = userdb[userID]
    for status in status_list:
        tweet = status._json
        try:
            if tweet['text']:
                if not tweet['retweeted'] and 'RT @' not in tweet['text']:
                    if not tweet['geo'] and not tweet['coordinates'] and not tweet['place']:
                        #this means the tweet found has no location, so assume same as previous
                        tweet['geo'] = doc['geo']
                        tweet['coordinates'] = doc['coordinates']
                        tweet['place'] = doc['place']
                    tweet['_id'] = tweet['id_str']
                    db.save(tweet)
                    if args.delete:
                        #if delete option is activated remove IDs from userdb 
                        #possibly to avoid re-searching in future
                        userdb.delete(doc)
        except couchdb.http.ResourceConflict as e:
            #Collisions are expected, move on
            pass
        except couchdb.http.ResourceNotFound as e:
            #Deletes may need time to catch up
            pass


if __name__ == '__main__':
    #Read arguments and parse
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--new', 
        help='use to mean existing DB needs to be scraped for users', 
        action='store_true')
    parser.add_argument('-d', '--delete', 
        help='if enabled, the user from userdb will be deleted after tweet searching', 
        action='store_true')
    args = parser.parse_args()

    #Set up configuration
    config = configparser.ConfigParser()
    config.read('config.ini')

    auth = OAuthHandler(config['Harvest']['ConsumerKey'], config['Harvest']['ConsumerSecret'])
    auth.set_access_token(config['Harvest']['AccessToken'], config['Harvest']['AccesTokenSecret'])
    api = tweepy.API(auth)
    couch = couchdb.Server( config['Harvest']['DatabaseIP'])
    databasename = config['UserSearch']['DatabaseCrawl']
    userdatabase = databasename + 'user'

    #Open up db
    if databasename not in couch:
        print("Exiting. Check if databasename exists")
        raise SystemExit
    else:
        db = couch[databasename]

    if userdatabase not in couch:
        userdb = couch.create(userdatabase)
    else:
        userdb = couch[userdatabase]

    #if option enabled, make a userid db first
    if args.new:
        add_users(db)

    for userID in userdb:
        add_tweets(userID,userdb,db,args)
