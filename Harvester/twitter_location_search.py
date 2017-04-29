# To run this code, first edit config_gen.py with your configuration, then:
#
# python[3] config_gen.py
# python[3] twitter_location_search.py [options]
#
# Crawls given twitter locationID db to store in other given db.
#
# If intended use is in conjunction with user searcher, -u option will keep
# any twitter user IDs this comes across in a database named dbname + user
# NOTE NAMING CONVENTION. This is hard coded. If you wish to use all packages in
# conjunction, be careful!
# 
# Optionally, with the -n option this program will instead scrape and find location
# IDs in existing tweet db before performing a similar task of finding past tweets
#
# Enable -d to remove searched for locationIDs to remove re-searching in the future

import tweepy
from tweepy import OAuthHandler
import configparser
import string
import json
import couchdb
import argparse


class LocationCrawler():
    def __init__(self,locationdb,db,args,maxtweets=None,userdb=None,locationID=None):
        if userdb:
            self.userdb = userdb
        if locationID:
            self.locationID = locationID
        if maxtweets:
            self.maxtweets = maxtweets

        self.maxID = -1

        self.locationdb = locationdb
        self.db = db
        self.args = args

    #Crawl existing db and make a list of its locations
    def add_locations(self):
        for tweetID in self.db:
                    tweet = self.db[tweetID]
                    if not tweet['place']:
                        #need a place
                        continue
                    if not tweet['place']['id']:
                        #if no place ID, tweet not useful
                        continue
                    try:
                        location = {}
                        location['_id'] = tweet['place']['id']
                        self.locationdb.save(location)
                    except couchdb.http.ResourceConflict as e:
                        #Collisions are expected, move on
                        pass

    #Find user's past tweets based on ID and store in given database
    def add_tweets(self):
        doc = self.locationdb[locationID]
        query = 'place:'+locationID

        if self.maxID > 0:
            try:
                status_list = (api.search(q=query,count=100))['statuses']
            except tweepy.error.TweepError as e:
                #bad location, remove from db
                self.locationdb.delete(doc)
                return
        else:
            try:
                status_list = (api.search(q=query,count=100,max_id=self.maxID))['statuses']
            except tweepy.error.TweepError as e:
                #bad location, remove from db
                self.locationdb.delete(doc)
                return

        if self.args.delete:
            #if delete option is activated remove IDs from locationdb 
            #possibly to avoid re-searching in future
            self.locationdb.delete(doc)

        for tweet in status_list:
            try:
                #first check if tweet is relevant aka has text and is not a retweet
                if tweet['text']:
                    if not tweet['retweeted'] and 'RT @' not in tweet['text']:
                        if not tweet['geo'] and not tweet['coordinates'] and not tweet['place']:
                            #this means the tweet found has no location, not useful to us so skip
                            #note that this is possible as a user's profile location can lead
                            #to a successful search
                            continue

                        else:
                            #relevant tweet
                            tweet['_id'] = tweet['id_str']
                            self.maxID = tweet['id'] - 1
                            self.db.save(tweet)

                            if self.args.user and tweet['user']['id_str']:
                                #ensure id_str is available
                                user = {}
                                user['_id'] = tweet['user']['id_str']
                                user['geo'] = tweet['geo']
                                user['coordinates'] = tweet['coordinates']
                                user['place'] = tweet['place']
                                self.userdb.save(user)
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
        help='use to mean existing DB needs to be scraped for twitter placeIDs, then exit', 
        action='store_true')
    parser.add_argument('-d', '--delete', 
        help='if enabled, the locations from locationdb will be deleted after tweet searching', 
        action='store_true')
    parser.add_argument('-u', '--user', 
        help='''if enabled, store userIDs this comes across, implying an intended use
        in conjunction with the accompanying user searcher. IMPORTANT: take note of 
        naming convention of <dbname>user and <dbname>location''', 
        action='store_true')
    args = parser.parse_args()

    #Set up configuration
    config = configparser.ConfigParser()
    config.read('config.ini')

    auth = OAuthHandler(config['Harvest']['ConsumerKey'], config['Harvest']['ConsumerSecret'])
    auth.set_access_token(config['Harvest']['AccessToken'], config['Harvest']['AccesTokenSecret'])
    api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
    couch = couchdb.Server( config['Harvest']['DatabaseIP'])
    databasename = config['LocationSearch']['DatabaseStore']
    userdatabase = databasename + 'user'
    locationdatabase = config['LocationSearch']['DatabaseCrawl']

    maxtweets = int(config['LocationSearch']['MaxTweets'])

    #Open up db
    if databasename not in couch:
        print("Exiting. Check if databasename exists")
        raise SystemExit
    else:
        db = couch[databasename]

    if locationdatabase not in couch:
        locationdb = couch.create(locationdatabase)
    else:
        locationdb = couch[locationdatabase]

    userdb = None
    if args.user:
        if userdatabase not in couch:
            userdb = couch.create(userdatabase)
        else:
            userdb = couch[userdatabase]

    crawler = LocationCrawler(locationdb,db,args)

    #if option enabled, make a twitter placeid db first
    if args.new:
        crawler.add_locations()
        print('Done scraping, run without -n option now to find more tweets!')
        raise SystemExit

    for locationID in locationdb:
        crawler = LocationCrawler(locationdb,db,args,maxtweets,userdb,locationID)
        crawler.add_tweets()