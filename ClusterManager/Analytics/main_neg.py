import couchdb
import create_sentiment
import preprocess
from load_dict import load_stopwords, load_emoji, load_minging_dict, load_afinn, load_negation_list, load_food_dict
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
from lga import LGA
import socket
import functools
import random
import socket
from check_ip import check_which_db


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
	COUCH_IP_TARGET = config['Analytics']['couch_database_target']
	COUCH_DB_TRAIN_DATA = config['Analytics']['train_data']
	COUCH_DB_ROW_DATA = config['Analytics']['row_data']
	COUCH_DB_TARGET_DATA = config['Analytics']['target_data']
	AFINN_FILE = config['Analytics']['afinn_dict']
	FOOD_FILE = config['Analytics']['food_dict']
	EMOJI_FILE = config['Analytics']['emojis_dict']
	MING_POS_FILE = config['Analytics']['mining_dict_pos']
	MING_NEG_FILE = config['Analytics']['mining_dict_neg']
	DICT_DIR = config['Analytics']['dict_dir']
	WORDS_FILE = config['Analytics']['words_dict']
	MAP_FUNC = config['Analytics']['map_func_preprocess']
	VIEW_VIC = config['Analytics']['view_preprocess_vicstream']
	GET_COORDINATES = config['Analytics']['get_coordinates']
	RETRIEVED_FIELD = config['Analytics']['retrieved_field_vicstream']
	HOST_DIR = config['Analytics']['host_dir']
	HOST_FILE = config['Analytics']['host_file']
	COUCH_DB_TEMP_ = config['Analytics']['temp_']
	HAS_PROCESSED = config['Analytics']['obj_has_processed']
	COUCH_DB_TARGET = config['Analytics']['target_data']
	TWEET_TEXT = config['Analytics']['obj_text']
	LR_FILE = config['Analytics']['classifier']
	COUNTER_FILE = config['Analytics']['con_vec']
	READBYTE = 'rb'
	FINISH_READING = 'Finish all reading and loading\nWe start to process doc from DB'
	DB_INFO = 'Source Database: '
	DB_INFO2 = 'Target Database: '
	IP_INFO = 'IP: '
	# get machine ip
	my_ip = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
	
	couch, db_row = check_which_db(VM1_IP, VM2_IP, VM3_IP, VM4_IP, DB_1, DB_2, DB_3, DB_4, my_ip)

	# get target db
	couch_target = couchdb.Server(COUCH_IP_TARGET)
	db_target = couch_target[COUCH_DB_TARGET_DATA]

	print(IP_INFO + str(my_ip))
	print(DB_INFO + str(db_row))
	print(DB_INFO2 + str(db_target))


	# load dictionaries
	food_dict = load_food_dict(DICT_DIR, FOOD_FILE)
	negation_list = load_negation_list()
	afinn_dict = load_afinn(DICT_DIR, AFINN_FILE)
	emojis = load_emoji(DICT_DIR, EMOJI_FILE)
	pos_set, neg_set = load_minging_dict(DICT_DIR, MING_POS_FILE, 
													MING_NEG_FILE)
	count_all = Counter()
	WORDS = Counter(spell_checker.words(os.path.join(DICT_DIR, WORDS_FILE)))

	# load classifier
	file = open(LR_FILE, READBYTE)
	lr = pickle.load(file)
	file.close()

	# load counter vector
	counter = CountVectorizer()
	load_vec = CountVectorizer(vocabulary = pickle.load(open(COUNTER_FILE, READBYTE)))

	lga = LGA()

	punctuation = list(string.punctuation)
	stop = load_stopwords()

	print(FINISH_READING)
	while true:
	# process each document in the db
		for _id in db_row:
			tweet = db_row.get(_id)

			if HAS_PROCESSED not in tweet:
				gen_set.gen_negation_set(
				   emojis,
				   WORDS,
				   tweet,
				   db_row,
				   db_target,
				   config,
				   couch,
				   count_all,
				   punctuation,
				   stop,
				   couchdb,
				   lga,
				   negation_list,
				   food_dict,
				   load_vec,
				   lr)



if __name__ == '__main__':
	main(sys.argv)
