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
	COUCH_DB_ROW_DATA = config['Analytics']['row_data']
	AFINN_FILE = config['Analytics']['afinn_dict']
	EMOJI_FILE = config['Analytics']['emojis_dict']
	MING_POS_FILE = config['Analytics']['mining_dict_pos']
	MING_NEG_FILE = config['Analytics']['mining_dict_neg']
	DICT_DIR = './Dict'
	WORDS_FILE = config['Analytics']['words_dict']

	# connect to database
	couch = couchdb.Server(COUCH_IP)

	if COUCH_DB_ROW_DATA not in couch:
		db = couch.create(COUCH_DB_ROW_DATA)
	else:
		db = couch[COUCH_DB_ROW_DATA]

	# store the data of training set to another database
	if COUCH_DB_TRAIN_DATA not in couch:
		db_train = couch.create(COUCH_DB_TRAIN_DATA)
	else:
		db_train = couch[COUCH_DB_TRAIN_DATA]

	# load dictionary
	afinn_dict = load_dict.load_afinn(DICT_DIR, AFINN_FILE)
	emojis = load_dict.load_emoji(DICT_DIR, EMOJI_FILE)
	pos_set, neg_set = load_dict.load_minging_dict(DICT_DIR, MING_POS_FILE, 
													MING_NEG_FILE)
	WORDS = Counter(spell_checker.words(os.path.join(DICT_DIR, WORDS_FILE)))
	
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







