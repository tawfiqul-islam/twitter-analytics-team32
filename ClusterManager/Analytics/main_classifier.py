
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
from sklearn.neural_network import MLPClassifier
from data_obj import TweetData
import configparser


def main(argv):
	config = configparser.ConfigParser()
	config.read(argv[1])

	COUCH_IP = config['Analytics']['couch_database']
	VM1_IP = config['VMTag']['VM1']
	VM2_IP = config['VMTag']['VM2']
	VM3_IP = config['VMTag']['VM3']
	VM4_IP = config['VMTag']['VM4']
	DB_1 = config['VMTag']['VM1_DB']
	DB_2 = config['VMTag']['VM2_DB']
	DB_3 = config['VMTag']['VM3_DB']
	DB_4 = config['VMTag']['VM4_DB']
	COUCH_DB_TRAIN_DATA = config['Analytics']['train_data']
	COUCH_DB_ROW_DATA = config['Analytics']['row_data']
	TWEET_TEXT = config['Analytics']['obj_text']
	TWEET_LABEL = config['Analytics']['obj_label']
	TFID_FILE = config['Analytics']['tfid_con_vec']
	COUNTER_FILE = config['Analytics']['con_vec']
	TFID_CLASSIFIER_FILE = config['Analytics']['classifier_tfid']
	COUNTER_CLASSIFIER_FILE = config['Analytics']['classifier']
	COUNTER_CLASSIFIER_FILE_MNB = config['Analytics']['classifier_mnb']
	COUNTER_CLASSIFIER_FILE_NEURAL = config['Analytics']['classifier_neural']
	WRITE = 'wb'
	WORD_LEVEL = 'word'


	# connect to database
	couch = couchdb.Server(COUCH_IP)



	# db = couch[COUCH_DB_TRAIN_DATA]
	db = couch['test']

	doc_ids = []
	train_features = []
	train_label = []
	for id in db:
	    doc_ids.append(id)
	    
	for doc_id in doc_ids:
		tweet = db[doc_id]
		if TWEET_LABEL in tweet and TWEET_TEXT in tweet:
			train_features.append(tweet[TWEET_TEXT])
			train_label.append(tweet[TWEET_LABEL])

	# get best 5000 vocabulary
	# chi2 can be changed to f_classif
	vectorizer = TfidfVectorizer(sublinear_tf = True, max_df = 0.5)
	X_train_features = vectorizer.fit_transform(train_features)
	ch2 = SelectKBest(chi2, k = 6000)
	X_train_features = ch2.fit_transform(X_train_features, train_label)
	voc = np.asarray(vectorizer.get_feature_names())[ch2.get_support()]

	# save the model and use the same best 6000 vocabularies
	vectorizer = TfidfVectorizer(sublinear_tf = True, max_df = 0.5, vocabulary = voc)
	X_train_features_tfid = vectorizer.fit_transform(train_features)
	pickle.dump(vectorizer.vocabulary_,open(TFID_FILE, WRITE))
	vectorizer = CountVectorizer(analyzer = WORD_LEVEL, vocabulary = voc)
	X_train_features = vectorizer.fit_transform(train_features)
	pickle.dump(vectorizer.vocabulary_,open(COUNTER_FILE, WRITE))

	X_train_features = X_train_features.toarray()
	X_train_features_tfid = X_train_features_tfid.toarray()


	# save memory
	train_features = []
	train_label = []
	'''
		for counter vec classifier
	'''
	# hold-out logistic regression
	X_train, X_test, y_train, y_test = train_test_split(
		X_train_features, train_label, test_size=0.2, random_state=42)

	# logistic regression for cross validation
	lr = LogisticRegression()

	lr.fit(X_train, y_train)
	print("logistic regression hold out: ")
	result = lr.score(X_test, y_test)


	# save model
	with open(COUNTER_CLASSIFIER_FILE, WRITE) as file:
		pickle.dump(lr, file)
	file.close()

	mnb = MultinomialNB()
	scores = cross_val_score(mnb, X_train, y_train, cv = 10)
	score =0.0
	for item in scores:
		score += item
	print('multinomial naive bayes cross validation: ')
	print(score/10)
	mnb.fit(X_train, y_train)
	result = mnb.score(X_test, y_test)
	print('multinomial naive bayes hold-out: ')
	print(result)

	# save model
	with open(COUNTER_CLASSIFIER_FILE_MNB, WRITE) as file:
		pickle.dump(mnb, file)
	file.close()

	neural = MLPClassifier(activation='tanh', alpha=1e-05,
	 	hidden_layer_sizes=(3,3), random_state=1, shuffle=True, solver='sgd', 
	 	verbose=True)
	neural.fit(X_train, y_train)
	result = neural.score(X_test, y_test)
	print('neural network hold-out: ')
	print(result)

	# save model
	with open(COUNTER_CLASSIFIER_FILE_NEURAL, WRITE) as file:
		pickle.dump(neural, file)
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
	with open(TFID_CLASSIFIER_FILE, WRITE) as file:
		pickle.dump(lr, file)
	file.close()


if __name__ == '__main__':
	main(sys.argv)