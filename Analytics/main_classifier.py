
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
from data_obj import TrainData
import configparser


def main(argv):
	config = configparser.ConfigParser()
	config.read(argv[1])
	# connect to database
	couch = couchdb.Server(config['Analytics']['couch_database'])

	if config['Analytics']['train_data'] not in couch:
		db_train = couch.create(config['Analytics']['train_data'])
	else:
		db_train = couch[config['Analytics']['train_data']]

	doc_ids = []
	train_features = []
	train_label = []
	for id in db:
	    doc_ids.append(id)
	    
	for doc_id in doc_ids:
		tweet = db[doc_id]
		train_features.append(tweet[config['Analytics']['obj_features']])
		train_label.append(tweet[config['Analytics']['obj_lebel']])

	train_features = preprocess.format_couchdata(train_features)



	# hold-out logistic regression
	X_train, X_test, y_train, y_test = train_test_split(
		train_features, train_label, test_size=0.2, random_state=42)

	# logistic regression for cross validation
	lr = LogisticRegression()

	lr.fit(X_train, y_train)
	result = lr.predict(X_test)

	# save model
	with open(config['Analytics']['classifier'], 'wb') as file:
    	pickle.dump(lr, file)


if __name__ == '__main__':
	main(sys.argv)