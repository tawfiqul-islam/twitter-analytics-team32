import couchdb
from mpi4py import MPI
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
from check_ip import check_which_db



def main(argv):
	comm = MPI.COMM_WORLD
	rank = comm.Get_rank()
	size = comm.Get_size()

	# declare config parser
	config = configparser.ConfigParser()
	config.read(argv[1])

	# get value from config parser
	COUCH_IP = config['Analytics']['couch_database']
	COUCH_IP_TARGET = config['Analytics']['couch_database_target']
	COUCH_DB_TRAIN_DATA = config['Analytics']['train_data']
	COUCH_DB_ROW_DATA = config['Analytics']['row_data']
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

	# get machine ip
	my_ip = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
	
	db_row = check_which_db(ip1, ip2, ip3, ip4, db1, db2, db3, db4, my_ip)

	# get target db
	couch_target = couchdb.Server(COUCH_IP_TARGET)
	db_target = couch_target[COUCH_DB_TARGET_DATA]
	couch = couchdb.Server(COUCH_IP)
	couch_target = couchdb.Server(COUCH_IP_TARGET)



	# load dictionary
	food_dict = load_food_dict(DICT_DIR, FOOD_FILE)
	negation_list = load_negation_list()
	afinn_dict = load_afinn(DICT_DIR, AFINN_FILE)
	emojis = load_emoji(DICT_DIR, EMOJI_FILE)
	pos_set, neg_set = load_minging_dict(DICT_DIR, MING_POS_FILE, 
													MING_NEG_FILE)
	count_all = Counter()
	WORDS = Counter(spell_checker.words(os.path.join(DICT_DIR, WORDS_FILE)))

	lga = LGA()

	punctuation = list(string.punctuation)
	stop = load_stopwords()

	print('finish reading')
	count = 0

	for _id in db_row:
		tweet = db_row.get(_id)
		gen_set.gen_negation_train_set(pos_set, 
                    neg_set,
                    afinn_dict,
                    emojis,
                    WORDS,
                    recvtweet,
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
                    food_dict)


if __name__ == '__main__':
	main(sys.argv)
