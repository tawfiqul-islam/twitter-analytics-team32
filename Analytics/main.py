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

	couch_ip = config['Analytics']['couch_database']
	couch_db_train_data = config['Analytics']['train_data']
	classifier_file_name = config['Analytics']['classifier']
	tweet_is_read = config['Analytics']['obj_is_read']
	tweet_features = config['Analytics']['obj_features']
	tweet_label = config['Analytics']['obj_label']
	read = "rb"

	# connect to database
	couch = couchdb.Server(couch_ip)

	if couch_db_train_data not in couch:
		db = couch.create(couch_db_train_data)
	else:
		db = couch[couch_db_train_data]

	# load model
	file = open(classifier_file_name, read)
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
			if not tweet[tweet_is_read]:
				temp_doc_ids.append(doc_id)
				# tweet_id.append(tweet['t_id'])
				train_features.append(tweet[tweet_features])
				re_read = False

		# if the data is not all predicted, it will predict and update back
		if not re_read:
			train_features = preprocess.format_couchdata(train_features)
			result = lr.predict(train_features)

			for i in range(len(temp_doc_ids)):
				tweet = db.get(temp_doc_ids[i])
				tweet[tweet_label] = result[i]
				tweet[tweet_is_read] = True
				db[temp_doc_ids[i]] = tweet
			re_read = True




if __name__ == '__main__':
	main(sys.argv)