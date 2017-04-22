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

class TrainData(Document):
	t_id = IntegerField()
	text = TextField()
	label = IntegerField()
	features = TextField()
	geo_code = TextField()
	is_read = BooleanField()

def main(argv):
	# connect to db
	couch = couchdb.Server('http://localhost:5984/')
	if 'train_data' not in couch:
		db = couch.create('train_data')
	else:
		db = couch['train_data']

	# load model
	file = open('lr_nectar.pkl', 'rb')
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
			if not tweet['is_read']:
				temp_doc_ids.append(doc_id)
				# tweet_id.append(tweet['t_id'])
				train_features.append(tweet['features'])
				re_read = False

		# if the data is not all predicted, it will predict and update back
		if not re_read:
			train_features = preprocess.format_couchdata(train_features)
			result = lr.predict(train_features)

			for i in range(len(temp_doc_ids)):
				tweet = db.get(temp_doc_ids[i])
				tweet['label'] = result[i]
				tweet['is_read'] = True
				db[temp_doc_ids[i]] = tweet
			re_read = True




if __name__ == '__main__':
	main(sys.argv)