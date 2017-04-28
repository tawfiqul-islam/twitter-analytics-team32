#https://twitter.com/search?q=nba%20mvp&src=typd


import sys
import jsonpickle
import os
import tweepy
import json
import time
import configparser
import couchdb
from backports import configparser



def	twitterSearch(accessToken, accessTokenSecret, searchQuery, db):

	maxTweets = 50000000 
	tweetsPerQry = 100 

	auth = tweepy.AppAuthHandler(accessToken, accessTokenSecret)

	api = tweepy.API(auth, wait_on_rate_limit=True,
	                   wait_on_rate_limit_notify=True)
	maxTweets = 50000000 # Some arbitrary large number
	tweetsPerQry = 100  # this is the max the API permits
	fName = 'tweets.txt' # We'll store the tweets in a text file.


	# If results from a specific ID onwards are reqd, set since_id to that ID.
	# else default to no lower limit, go as far back as API allows
	sinceId = None

	# If results only below a specific ID are, set max_id to that ID.
	# else default to no upper limit, start from the most recent tweet matching the search query.
	max_id = -1

	tweetCount = 0
	duplicatetweet=0;
	print("Downloading max {0} tweets".format(maxTweets))
	while tweetCount < maxTweets:
		try:
			if(max_id <= 0):
				if (not sinceId):
					new_tweets = api.search(q=searchQuery, count=tweetsPerQry, languages=["en"])
				else:
					new_tweets = api.search(q=searchQuery, count=tweetsPerQry, since_id=sinceId, languages=["en"])
			else:
				if (not sinceId):
					new_tweets = api.search(q=searchQuery, count=tweetsPerQry, max_id=str(max_id - 1), languages=["en"])
				else:
					new_tweets = api.search(q=searchQuery, count=tweetsPerQry, max_id=str(max_id - 1), since_id=sinceId, languages=["en"])
			if not new_tweets:
				print("No more tweets found")
				break
			for tweet in new_tweets:
				jsontweet = jsonpickle.encode(tweet._json, unpicklable=False)
				#print(jsontweet[int(id_str)])
				tweet = json.loads(jsontweet)
				#print [jsonstr['id_str']]
				id = tweet['id_str']
				tweet['_id'] = tweet['id_str']
				tweet['havrversterType'] = 'KeyWordSearch2'
				db.save(tweet)
				print id
			tweetCount += len(new_tweets)
			print("Downloaded {0} tweets".format(tweetCount))
			max_id = new_tweets[-1].id
		except Exception as e:
			pass
			duplicatetweet = duplicatetweet+ 1
	print ("Downloaded {0} tweets Duplicate Tweets {1} ".format(tweetCount, duplicatetweet))


if __name__ == '__main__':

	config = configparser.ConfigParser()

	 # Read the Config File
	config.read('config.ini')
	accessToken = config['HarvestConfig']['ConsumerKey']
	accessTokenSecret = config['HarvestConfig']['ConsumerSecret']
	searchQuery =  config['HarvestConfig']['SearchQuery']

	print (accessToken)
	print(accessTokenSecret)
	print(searchQuery)
	



	databaseIP = config['HarvestConfig']['DatabaseIP']
	databaseName = config['HarvestConfig']['DatabaseName']

	couch = couchdb.Server(databaseIP)

	if  databaseName not in couch:
	    db = couch.create(databaseName)
	else:
	    db = couch[databaseName]
	twitterSearch(accessToken, accessTokenSecret, searchQuery, db )