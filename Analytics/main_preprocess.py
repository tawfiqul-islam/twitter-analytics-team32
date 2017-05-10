import couchdb

import create_sentiment
import preprocess
from load_dict import load_stopwords, load_emoji, load_minging_dict, load_afinn
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

def numbers_to_strings(argument):
    switcher = {
        0: "zero",
        1: "one",
        2: "two",
    }
    return switcher.get(argument, "nothing")

def get_my_path():
    try:
        filename = __file__ # where we were when the module was loaded
    except NameError: # fallback
        filename = inspect.getsourcefile(get_my_path)
    return os.path.realpath(filename)

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
	MAP_FUNC = config['Analytics']['map_func_preprocess']
	VIEW_VIC = config['Analytics']['view_preprocess_vicstream']
	GET_COORDINATES = config['Analytics']['get_coordinates']
	RETRIEVED_FIELD = config['Analytics']['retrieved_field_vicstream']
	HOST_DIR = config['Analytics']['host_dir']
	HOST_FILE = config['Analytics']['host_file']
	COUCH_DB_TEMP_ = config['Analytics']['temp_']
	HAS_PROCESSED = config['Analytics']['obj_has_processed']
	COUCH_DB_TARGET = config['Analytics']['target_data']
	NLTK_STOPWORDS = 'stopwords'
	NLTK_ENGLISH = 'english'
	VIEW = 'view'
	MAP = 'map'
	READ = "r"
	HTTP = 'http://'
	PORT = ':5984/'
	ip_list = []
	rank = 0
	length = 0
	total_vm = 0
	cur_row = 0
	count = 0
	my_ip = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
	

	#check rank of the machine
	cm_path = get_my_path()
	sp_path = functools.reduce(lambda x, f: f(x), [os.path.dirname]*2, cm_path)
	constants_path = os.path.join(sp_path, HOST_DIR, HOST_FILE)
	with open(constants_path, READ) as hostfile:
		for line in hostfile:
			if my_ip == line.rstrip():
				
				rank = count
			count+=1
			total_vm += 1
			if count % 2 == 0:
				line = HTTP + line.rstrip() + PORT
				ip_list.append(line)
	print(ip_list)
	total_vm /= 2
	total_vm = int(total_vm)
	rank = int(rank/2)
	hostfile.close()
	# connect to database
	couch = couchdb.Server(COUCH_IP)

	print("total is " + str(total_vm) + " vm")
	print("my rank  is " + str(rank))

	# # store the data of training set to another database
	# if COUCH_DB_TRAIN_DATA not in couch:
	# 	db_train = couch.create(COUCH_DB_TRAIN_DATA)
	# else:
	# 	db_train = couch[COUCH_DB_TRAIN_DATA]

	if rank == 0:
		db_list = {}
		couch_list = []
		# get the database
		db = couch[COUCH_DB_ROW_DATA]

		for i in range(total_vm):
			if i != 0:
				should_continue = True
				if should_continue:
					try:
						couch = couchdb.Server(ip_list[i])
						print(ip_list[i])
						couch_list.append(couch)
						db_list[COUCH_DB_TEMP_+str(i)] = couch[COUCH_DB_TEMP_+str(i)]
						should_continue = False
					except:
						pass

	else:
		should_continue = True
		db_name = COUCH_DB_TEMP_ + str(rank)
		couch_local = couchdb.Server(ip_list[rank])

		print(db_name)
		if db_name not in couch_local:
			try:
				db_temp = couch.create(db_name)
			except:
				pass
		else:
			while should_continue:
				try:
					db_temp = couch_local[db_name]
					db_target = couch[COUCH_DB_TARGET]
					should_continue = False
				except:
					pass

	# load dictionary
	afinn_dict = load_afinn(DICT_DIR, AFINN_FILE)
	emojis = load_emoji(DICT_DIR, EMOJI_FILE)
	pos_set, neg_set = load_minging_dict(DICT_DIR, MING_POS_FILE, 
													MING_NEG_FILE)
	WORDS = Counter(spell_checker.words(os.path.join(DICT_DIR, WORDS_FILE)))
	count_all = Counter()

	lga = LGA()

	punctuation = list(string.punctuation)
	stop = load_stopwords


	limit_chunk = 1000
	cur = 0

	while True:
		if rank == 0:
			for _id in db:
				tweet = db.get(_id)
				if HAS_PROCESSED not in tweet:
					# tweet[HAS_PROCESSED] = True
					db[_id] = tweet
					tweet.pop('_rev', None)
					for database in db_list:
						print(db_list)
						send_to = (cur % 3) + 1
						print(send_to)
						if database.endswith(str(send_to)):
							try:
								db_list[database].save(tweet)
							except couchdb.http.ResourceConflict:
								pass

		else:
			for _id in db_temp:
				tweet = db_temp[_id]
				gen_set.gen_set(pos_set, 
			                neg_set,
			                afinn_dict,
			                emojis,
			                WORDS,
			                tweet,
			                db_temp,
			                db_target,
			                config,
			                couch,
			                count_all,
			                punctuation,
			                stop,
			                couchdb,
			                lga)





#




if __name__ == '__main__':
	main(sys.argv)







