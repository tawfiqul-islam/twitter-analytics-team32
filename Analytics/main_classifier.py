
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
from couchdb.mapping import Document, TextField, IntegerField, DateTimeField

from sklearn import svm
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB

class TrainData(Document):
	t_id = IntegerField()
	text = TextField()
	label = IntegerField()
	features = TextField()
	geo_code = TextField()

def main(argv):
	# connect to database
	couch = couchdb.Server('http://localhost:5984/')
	if 'train_data' not in couch:
		db = couch.create('train_data')
	else:
		db = couch['train_data']

	doc_ids = []
	train_features = []
	train_label = []
	for id in db:
	    doc_ids.append(id)
	    
	for doc_id in doc_ids:
		tweet = db[doc_id]
		train_features.append(tweet['features'])
		train_label.append(tweet['label'])

	train_features = preprocess.format_couchdata(train_features)



	#hold-out multinomial Naive Bayes
	X_train, X_test, y_train, y_test = train_test_split(
		train_features, train_label, test_size=0.2, random_state=42)

	# logistic regression for cross validation
	lr = LogisticRegression()

	lr.fit(X_train, y_train)
	result = lr.predict(X_test)

	with open('lr_nectar.pkl', 'wb') as file:
    	pickle.dump(lr, file)
	






if __name__ == '__main__':
	main(sys.argv)