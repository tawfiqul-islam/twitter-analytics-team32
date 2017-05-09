#Driver program for harvester

import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import argparse
import configparser
import json
import couchdb
import twitter_stream
import twitter_user_search
import twitter_location_search
from  twitter_stream import MyListener
from twitter_user_search import UserCrawler
from twitter_location_search import LocationCrawler
import socket
import time

#from stream
if __name__ == '__main__':
    #args
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', 
        action='store_true')
    parser.add_argument('-l', '--location',
        action='store_true')
    parser.add_argument('-d', '--delete',
        action='store_true')
    args = parser.parse_args()

    #Set up configuration
    config = configparser.ConfigParser()
    config.read('../config.ini')

    auth = OAuthHandler(config['Harvest']['ConsumerKey'], config['Harvest']['ConsumerSecret'])
    auth.set_access_token(config['Harvest']['AccessToken'], config['Harvest']['AccesTokenSecret'])
    databasename = config['Stream']['DatabaseName']
    userdatabase = databasename + 'user'
    locationdatabase = databasename + 'location'

    #find rank based on IP
    my_ip = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
    for vmnum in config['VMTag']:
        ipaddr = str(config['VMTag'][vmnum])
        if my_ip == ipaddr:
            my_rank = vmnum

    #open up dbs
    dbs = []
    for i in range(1,len(config['VMTag'])+1):
        vm = 'vm' + str(i)
        #note the port and ip format is assumed
        couch = couchdb.Server('http://' + config['VMTag'][vm] + ':5986/')
        tempname = databasename + str(i)
        if tempname not in couch:
            tempdb = couch.create(tempname)
        else:
            tempdb = couch[tempname]
        dbs.append(tempdb)

    if userdatabase not in couch:
        userdb = couch.create(userdatabase)
    else:
        userdb = couch[userdatabase]

    if locationdatabase not in couch:
        locationdb = couch.create(locationdatabase)
    else:
        locationdb = couch[locationdatabase]


    if my_rank == 'vm2':
        #STREAMER
        while(True):
            try:
                twitter_stream = Stream(auth, MyListener(dbs=dbs,args=args,userdb=userdb,locationdb=locationdb))
                api = tweepy.API(auth)
                twitter_stream.api = api

                #This is the bounding box within which we want tweets
                boundingbox = config['Stream']['Location']
                boundingbox = boundingbox.split(',')
                loc1 = float(boundingbox[0])
                loc2 = float(boundingbox[1])
                loc3 = float(boundingbox[2])
                loc4 = float(boundingbox[3])
                #Set up the stream
                twitter_stream.filter(locations=[loc1,loc2,loc3,loc4])
            except:
                time.sleep(15)
                pass

    elif my_rank == 'vm3':
        #LOCATION SEARCHER
        api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
        twitter_location_search.api = api
        while True:
            couch = couchdb.Server( config['Harvest']['DatabaseIP'])
            locationdb = couch[locationdatabase]
            maxtweets = int(config['LocationSearch']['MaxTweets'])

            for locationID in locationdb:
                crawler = LocationCrawler(locationdb,dbs,args,maxtweets,userdb,locationID)
                crawler.add_tweets()
            time.sleep(1800)

    elif my_rank == 'vm4':
        #USER SEARCHER
        api = tweepy.API(auth)
        twitter_user_search.api = api

        while True:
            couch = couchdb.Server( config['Harvest']['DatabaseIP'])
            userdb = couch[userdatabase]
            maxtweets = int(config['UserSearch']['MaxTweets'])

            for userID in userdb:
                crawler = UserCrawler(userdb,dbs,args,maxtweets,locationdb,userID)
                crawler.add_tweets()
            time.sleep(1800)