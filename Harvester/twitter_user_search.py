# To run this code, first edit config_gen.py with your configuration, then:
#
# python[3] config_gen.py
# python[3] twitter_user_search.py [options]
#
# Crawls given userID db to store in other given db.
#
# With the -n option this program will instead crawl and find users
# before performing a similar task of finding past tweets
#
# -l option will keep any twitter location IDs this comes across in a database named 
# dbname + location if intended use is in conjunction with location searcher, 
# NOTE NAMING CONVENTION. This is hard coded. If you wish to use all packages in
# conjunction, be careful!
#
# Furthermore, if the new tweet obtained from searching user past history has no
# location information, the existing information is used instead and past tweets
# are assumed to be from the same location.
#
# Also, by default any users that are searched for will not be deleted from the
# user database. However, to minimise re-searching users already done, the 
# -d option will instead DELETE userIDs in the database.

import tweepy
from tweepy import OAuthHandler
import configparser
import string
import json
import couchdb
import argparse

class UserCrawler():
    def __init__(self, userdb, db, args, maxtweets=None, locationdb=None,userID=None):
        if locationdb:
            self.locationdb = locationdb
        if userID:
            self.userID = userID
        if maxtweets:
            self.maxtweets = maxtweets

        self.userdb = userdb
        self.db = db
        self.args = args

        self.maxID = -1

    #Crawl existing db and make a list of its users
    def add_users(self):
        for tweetID in self.db:
                    tweet = self.db[tweetID]
                    try:
                        user = {}
                        user['_id'] = tweet['user']['id_str']
                        user['geo'] = tweet['geo']
                        user['coordinates'] = tweet['coordinates']
                        user['place'] = tweet['place']
                        self.userdb.save(user)
                    except couchdb.http.ResourceConflict as e:
                        #Collisions are expected, move on
                        pass

    #Find user's past tweets based on ID and store in given database
    def add_tweets(self):
        try:
            doc = self.userdb[userID]
        except couchdb.http.ResourceNotFound as e:
            #some sync issue has occured probably, expected so move on
            return

        if self.maxID < 0:
            #first run through
            try:
                status_list = api.user_timeline(userID,count=100)
            except tweepy.error.TweepError as e:
                #some users will not allow their timelines viewed or have been deleted
                #remove as not useful
                self.userdb.delete(doc)
                return
        else:
            try:
                status_list = api.user_timeline(userID,count=100,max_id=self.maxID)
            except tweepy.error.TweepError as e:
                #some users will not allow their timelines viewed or have been deleted
                #remove as not useful
                self.userdb.delete(doc)
                return


        if self.args.delete:
            #if delete option is activated remove IDs from userdb 
            #possibly to avoid re-searching in future
            self.userdb.delete(doc)


        for status in status_list:
            tweet = status._json
            try:
                if tweet['text']:
                    #check for retweets
                    if not tweet['retweeted'] and 'RT @' not in tweet['text']:
                        if not tweet['geo'] and not tweet['coordinates'] and not tweet['place']:
                            #this means the tweet found has no location, so assume same as previous
                            tweet['geo'] = doc['geo']
                            tweet['coordinates'] = doc['coordinates']
                            tweet['place'] = doc['place']
                        tweet['_id'] = tweet['id_str']
                        self.maxID = tweet['id'] - 1
                        self.db.save(tweet)

                    #when storing location data, store twitter locationID
                    if self.args.location and tweet['place']:
                        if tweet['place']['id']:
                            #only add if location ID exists
                            location = {}
                            location['_id'] = tweet['place']['id']
                            self.locationdb.save(location)

            except couchdb.http.ResourceConflict as e:
                #Collisions are expected, move on
                pass

        #keep going until max tweets reached or no more returned
        if(len(status_list) < 100 or self.maxtweets < 0):
            return
        else:
            self.maxtweets = self.maxtweets - 100
            self.add_tweets()

if __name__ == '__main__':
    #Read arguments and parse
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--new', 
        help='use to mean existing DB needs to be scraped for users, then exit', 
        action='store_true')
    parser.add_argument('-d', '--delete', 
        help='if enabled, the user from userdb will be deleted after tweet searching', 
        action='store_true')
    parser.add_argument('-l', '--location', 
        help='''if enabled, store locationIDs this comes across, implying an intended use
        in conjunction with the accompanying location searcher. IMPORTANT: take note of 
        naming convention of <dbname>user and <dbname>location''', 
        action='store_true')
    args = parser.parse_args()

    #Set up configuration
    config = configparser.ConfigParser()
    config.read('config.ini')

    auth = OAuthHandler(config['Harvest']['ConsumerKey'], config['Harvest']['ConsumerSecret'])
    auth.set_access_token(config['Harvest']['AccessToken'], config['Harvest']['AccesTokenSecret'])
    api = tweepy.API(auth)
    couch = couchdb.Server( config['Harvest']['DatabaseIP'])
    databasename = config['UserSearch']['DatabaseStore']
    userdatabase = config['UserSearch']['DatabaseCrawl']
    locationdatabase = databasename + 'location'

    maxtweets = int(config['UserSearch']['MaxTweets'])

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

    locationdb = None
    if args.location:
        if locationdatabase not in couch:
            locationdb = couch.create(locationdatabase)
        else:
            locationdb = couch[locationdatabase]

    crawler = UserCrawler(userdb,db,args)

    #if option enabled, make a userid db first
    if args.new:
        crawler.add_users
        print('Done scraping, run without -n option now to find more tweets!')
        raise SystemExit

    for userID in userdb:
        crawler = UserCrawler(userdb,db,args,maxtweets,locationdb,userID)
        crawler.add_tweets()

