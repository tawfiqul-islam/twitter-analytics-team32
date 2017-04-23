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
from data_obj import TrainData
import configparser



def main(argv):
	config = configparser.ConfigParser()
	config.read(argv[1])
	# connect to database
	couch = couchdb.Server(config['Analytics']['couch_database'])
	if config['Analytics']['row_data'] not in couch:
		db = couch.create(config['Analytics']['row_data'])
	else:
		db = couch[config['Analytics']['row_data']]

	# load dictionary
	afinn_dict = load_dict.load_afinn(config['Analytics']['afinn_dict'])
	emojis = load_dict.load_emoji(config['Analytics']['emojis_dict'])
	pos_set, neg_set = load_dict.load_minging_dict(config['Analytics']['mining_dict_pos'], 
														config['Analytics']['mining_dict_neg'])
	WORDS = Counter(spell_checker.words(os.path.join('./Dict', config['Analytics']['words_new.txt'])))
	

	# get all documents' id
	doc_ids = []
	for id in db:
		doc_ids.append(id)

	# generate text and label training set
	total_tweets, labels, ids, geo_codes = gen_set.gen_set(pos_set, 
					                                    neg_set,
					                                    afinn_dict,
					                                    emojis,
					                                    db,
					                                    doc_ids)

	# vectorise the features of training set
	vectorizer = CountVectorizer(analyzer = "word",   
	                             tokenizer = None,    
	                             preprocessor = None, 
	                             stop_words = None,   
	                             max_features = 5000)

	train_data_features = vectorizer.fit_transform(total_tweets)

	# save the model
	pickle.dump(vectorizer.vocabulary_,open(config['Analytics']['con_vec'],"wb"))
	train_data_features = train_data_features.toarray().tolist()


	# store the data of training set to another database
	if config['Analytics']['train_data'] not in couch:
		db_train = couch.create(config['Analytics']['train_data'])
	else:
		db_train = couch[config['Analytics']['train_data']]

	for i in range(len(labels)):
	    train_data = TrainData(t_id = ids[i],
						    	text = total_tweets[i], 
						    	label=labels[i], 
						    	features=train_data_features[i],
						    	geo_code = geo_codes[i],
						    	is_read = False)
	    train_data.store(db_train)



if __name__ == '__main__':
	main(sys.argv)







