import couchdb

import create_sentiment
import preprocess
import load_dict
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
import operator
from nltk.corpus import stopwords
import nltk
import json
import string
import os
import sys
import gen_set
import csv
import numpy as np
import spell_checker
import datetime
import pickle
from couchdb.mapping import Document, TextField, IntegerField, DateTimeField, BooleanField
from data_obj import TweetData
import configparser

def main(argv):

	config = configparser.ConfigParser()
	config.read(argv[1])

	COUCH_IP = config['Analytics']['couch_database']
	COUCH_DB_TRAIN_DATA = config['Analytics']['train_data']
	CLASSIFIER_FILE_NAME = config['Analytics']['classifier']
	TWEET_IS_READ = config['Analytics']['obj_is_read']
	TWEET_FEATURES = config['Analytics']['obj_features']
	TWEET_LABEL = config['Analytics']['obj_label']
	READ = "rb"

	# connect to database
	couch = couchdb.Server(COUCH_IP)

	if COUCH_DB_TRAIN_DATA not in couch:
		db = couch.create(COUCH_DB_TRAIN_DATA)
	else:
		db = couch[COUCH_DB_TRAIN_DATA]

	# load model
	file = open(CLASSIFIER_FILE_NAME, READ)
	lr = pickle.load(file)

	re_read = True

	# continuously read from database
	while True:
		doc_ids = []
		train_features = []
		tweet_id = []
		temp_doc_ids = []

		for t_id in db:
			doc_ids.append(t_id)

		for doc_id in doc_ids:
			tweet = db[doc_id]
			if not tweet[TWEET_IS_READ]:
				temp_doc_ids.append(doc_id)
				# tweet_id.append(tweet['t_id'])
				train_features.append(tweet[TWEET_FEATURES])
				re_read = False

		# if the data is not all predicted, it will predict and update back
		if not re_read:
			train_features = preprocess.format_couchdata(train_features)
			result = lr.predict(train_features)

			for i in range(len(temp_doc_ids)):
				tweet = db.get(temp_doc_ids[i])
				tweet[TWEET_LABEL] = result[i]
				tweet[TWEET_IS_READ] = True
				db[temp_doc_ids[i]] = tweet
			re_read = True




if __name__ == '__main__':
	main(sys.argv)