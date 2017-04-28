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
	couch_db_row_data = config['Analytics']['row_data']
	afinn_file = config['Analytics']['afinn_dict']
	emoji_file = config['Analytics']['emojis_dict']
	ming_pos_file = config['Analytics']['mining_dict_pos']
	ming_neg_file = config['Analytics']['mining_dict_neg']
	dict_dir = './Dict'
	words_file = config['Analytics']['words_dict']

	# connect to database
	couch = couchdb.Server(couch_ip)

	if couch_db_row_data not in couch:
		db = couch.create(couch_db_row_data)
	else:
		db = couch[couch_db_row_data]

	# store the data of training set to another database
	if couch_db_train_data not in couch:
		db_train = couch.create(couch_db_train_data)
	else:
		db_train = couch[couch_db_train_data]

	# load dictionary
	afinn_dict = load_dict.load_afinn(afinn_file)
	emojis = load_dict.load_emoji(emoji_file)
	pos_set, neg_set = load_dict.load_minging_dict(ming_pos_file, 
													ming_neg_file)
	WORDS = Counter(spell_checker.words(os.path.join(dict_dir, words_file)))
	
	while True:
		# get all documents' id
		doc_ids = []
		for _id in db:
			doc_ids.append(_id)

		# generate text and label training set
		gen_set.gen_set(pos_set, 
		                neg_set,
		                afinn_dict,
		                emojis,
		                WORDS,
		                db,
		                doc_ids,
		                db_train,
		                config,
		                couch)










if __name__ == '__main__':
	main(sys.argv)







