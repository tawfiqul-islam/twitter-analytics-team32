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

class TrainData(Document):
	text = TextField()
	label = IntegerField()
	features = TextField()

def main(argv):
	# connect to database
	couch = couchdb.Server('http://localhost:5984/')
	if 'sentiment' not in couch:
		db = couch.create('sentiment')
	else:
		db = couch['sentiment']

	# load dictionary
	afinn_dict = load_dict.load_afinn(argv[1])
	pos_emoti, neg_emoti, neu_emoti = load_dict.load_emoti()
	emojis = load_dict.load_emoji(argv[2])
	pos_1_set, neg_1_set = load_dict.load_minging_dict(argv[3], argv[4])
	

	# get all documents' id
	doc_ids = []
	for id in db:
		doc_ids.append(id)

	# generate text and label training set
	total_tweets, labels = gen_set.gen_set(pos_1_set, 
	                                    neg_1_set,
	                                    afinn_dict,
	                                    emojis,
	                                    pos_emoti,
	                                    neg_emoti,
	                                    db,
	                                    doc_ids)

	# vectorise the features of training set
	vectorizer = CountVectorizer(analyzer = "word",   
	                             tokenizer = None,    
	                             preprocessor = None, 
	                             stop_words = None,   
	                             max_features = 2000)

	train_data_features = vectorizer.fit_transform(total_tweets)

	# save the model
	pickle.dump(vectorizer.vocabulary_,open("counter_model.pkl","wb"))


	# store the data of training set to another database
	if "train_data" not in couch:
		db_train = couch.create('train_data')
	else:
		db_train = couch['train_data']

	for i in range(len(labels)):
	    train_data = TrainData(text = total_tweets[i], label=labels[i], features=train_data_features[i])
	    train_data.store(db_train)



if __name__ == '__main__':
	main(sys.argv)







