
import couchdb

import create_sentiment
import preprocess
import load_dict
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.feature_selection import chi2, SelectKBest
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
from data_obj import TweetData
import configparser


def main(argv):
	config = configparser.ConfigParser()
	config.read(argv[1])

	couch_ip = config['Analytics']['couch_database']
	couch_db_train_data = config['Analytics']['train_data']
	couch_db_row_data = config['Analytics']['row_data']
	tweet_text = config['Analytics']['obj_text']
	tweet_label = config['Analytics']['obj_label']
	tfid_file = config['Analytics']['tfid_con_vec']
	counter_file = config['Analytics']['con_vec']
	tfid_classifier_file = config['Analytics']['classifier_tfid']
	counter_classifier_file = config['Analytics']['classifier']
	write = 'wb'


	# connect to database
	couch = couchdb.Server(couch_ip)


	if couch_db_train_data not in couch:
		db = couch.create(couch_db_train_data)
	else:
		db = couch[couch_db_train_data]

	doc_ids = []
	train_features = []
	train_label = []
	for id in db:
	    doc_ids.append(id)
	    
	for doc_id in doc_ids:
		tweet = db[doc_id]
		train_features.append(tweet[tweet_text])
		train_label.append(tweet[tweet_label])

	# get best 5000 vocabulary from 7000
	vectorizer = TfidfVectorizer(sublinear_tf = True, max_df = 0.5, max_features = 700)
	X_train_features = vectorizer.fit_transform(train_features)
	ch2 = SelectKBest(chi2, k = 500)
	X_train_features = ch2.fit_transform(X_train_features, train_label)
	voc = np.asarray(vectorizer.get_feature_names())[ch2.get_support()]

	# save the model
	vectorizer = TfidfVectorizer(sublinear_tf = True, max_df = 0.5, vocabulary = voc)
	X_train_features_tfid = vectorizer.fit_transform(train_features)
	pickle.dump(vectorizer.vocabulary_,open(tfid_file, write))
	vectorizer = CountVectorizer(analyzer = "word", vocabulary = voc)
	X_train_features = vectorizer.fit_transform(train_features)
	pickle.dump(vectorizer.vocabulary_,open(counter_file, write))

	X_train_features = X_train_features.toarray()
	X_train_features_tfid = X_train_features_tfid.toarray()


	'''
		for counter vec classifier
	'''
	# hold-out logistic regression
	X_train, X_test, y_train, y_test = train_test_split(
		X_train_features, train_label, test_size=0.2, random_state=42)

	# logistic regression for cross validation
	lr = LogisticRegression()

	lr.fit(X_train, y_train)
	result = lr.predict(X_test)

	# save model
	with open(counter_classifier_file, write) as file:
		pickle.dump(lr, file)
	file.close()


	'''
		for tfid counter vec classifier
	'''
    # hold-out logistic regression
	X_train, X_test, y_train, y_test = train_test_split(
		X_train_features_tfid, train_label, test_size=0.2, random_state=42)

	# logistic regression for cross validation
	lr = LogisticRegression()

	lr.fit(X_train, y_train)
	result = lr.predict(X_test)

	# save model
	with open(tfid_classifier_file, write) as file:
		pickle.dump(lr, file)
	file.close()


if __name__ == '__main__':
	main(sys.argv)