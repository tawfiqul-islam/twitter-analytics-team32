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


#Find user's past tweets based on ID and store in given database
def add_tweets(userID, userdb, db, args):
    status_list = api.user_timeline(userID)
    for status in status_list:
        tweet = status._json
        try:
            if tweet['text']:
                if not tweet['retweeted'] and 'RT @' not in tweet['text']:
                    if not tweet['geo'] and not tweet['coordinates'] and not tweet['place']:
                        #this means the tweet found has no location, so assume same as previous
                        tweet['geo'] = userdb[userID]['geo']
                        tweet['coordinates'] = userdb[userID]['coordinates']
                        tweet['place'] = userdb[userID]['place']
                    db.save(tweet)
                    if args.delete:
                        #delete unless keep argument used
                        userdb.delete(userID)
        except Exception as e:
            print(e)
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

    if args.new:
        for tweet in db:
            try:
                user = {}
                user['_id'] = db[tweet]['user']['id_str']
                user['geo'] = db[tweet]['geo']
                user['coordinates'] = db[tweet]['coordinates']
                user['place'] = db[tweet]['place']
                userdb.save(user)
            except Exception as e:
                print(e)
                pass

    for user in userdb:
        add_tweets(user,userdb,db,args)
