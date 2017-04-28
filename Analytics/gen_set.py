
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
import csv
import numpy as np
import spell_checker
from data_obj import TweetData


def gen_set(pos_1_set, 
    neg_1_set,
    afinn_dict,
    emojis,
    WORDS,
    db,
    doc_ids,
    db_train,
    config,
    couch):

    #########
    ### create the bag of words
    #########

    count_all = Counter()
    nltk.download('stopwords')

    punctuation = list(string.punctuation)
    stop = stopwords.words('english')
    

    # count # of pos neg neutral word determined by 4 dataset
    count_positive = 0
    count_negative = 0
    ids = []
    total_tweet = []
    polarity_tweet = []
    geo_codes = []
    cur_senti = 5


    for doc_id in doc_ids:
        tweet = db[doc_id]
        if not tweet[config['Analytics']['obj_has_processed']]:
            filter_words = preprocess.process_tokens(tweet[config['Analytics']['obj_text']], stop, punctuation, emojis, WORDS)
            no_spell = preprocess.process_tokens_no_spell(tweet[config['Analytics']['obj_text']], stop, punctuation, emojis)

            if len(filter_words) > 1:
                #calculate_emoti_senti(tweet, pos_emoticon, neg_emoticon, pos, neg):
                count_positive, count_negative = create_sentiment.calculate_emoti_senti(filter_words,
                                                                                        count_positive,
                                                                                        count_negative)

                count_positive, count_negative = create_sentiment.calculate_emoji_senti(filter_words,
                                                                                       emojis,
                                                                                       count_positive,
                                                                                       count_negative)
                # use AFINN-111 sentiment word to label the tweet
                count_positive, count_negative = create_sentiment.calculate_afinn_senti(filter_words,
                                                                                      afinn_dict,
                                                                                      count_positive,
                                                                                      count_negative)


                # use Minqing Hu and Bing Liu sentiment word to label the tweet
                count_positive, count_negative = create_sentiment.calculate_minqing_senti(filter_words,
                                                                                        pos_1_set,
                                                                                        neg_1_set,
                                                                                        count_positive,
                                                                                        count_negative)




                temp_text = create_data(filter_words)
                geo_info = gen_geo_info(tweet)

                cur_senti = create_sentiment.total_sentiment(count_positive, count_negative)
                if cur_senti != 5:
                    target_tweet = TweetData(
                            _id = tweet['id_str'],
                            original_text = tweet['text'],
                            text = temp_text,
                            no_spell_text = no_spell,
                            label = cur_senti,
                            tfid_features = "",
                            features = "",
                            geo_code = geo_info,
                            is_read = False)
                    try:
                        target_tweet.store(db_train)
                    except couchdb.http.ResourceConflict:
                        pass



                    tweet[config['Analytics']['obj_has_processed']] = True
                    db[doc_id] = tweet




                count_positive = 0
                count_negative = 0


def gen_train(train_data, train_label, number):
    new_trainX = []
    new_trainY = []
    rest_X = []
    rest_Y = []
    count_pos = 0
    count_neg = 0
    count_neu = 0
    for i in range(len(train_label)):
        if train_label[i] == 1 and count_pos <= number:
            new_trainX.append(train_data[i])
            new_trainY.append(train_label[i])
            count_pos += 1
        elif train_label[i] == -1 and count_neg <= number:
            new_trainX.append(train_data[i])
            new_trainY.append(train_label[i])
            count_neg += 1
        elif train_label[i] == 0 and count_neu <= number:
            new_trainX.append(train_data[i])
            new_trainY.append(train_label[i])
            count_neu += 1
        else:
            rest_X.append(train_data[i])
            rest_Y.append(train_label[i])
    return new_trainX, new_trainY, rest_X, rest_Y

def gen_geo_info(tweet):
    if tweet['place'] and not tweet['coordinates']:
        geo_info = tweet['place']
    elif tweet['coordinates'] and not tweet['place']:
        if 'coordinates' in  tweet['coordinates']:
            print(tweet['coordinates'])
            geo_info = tweet['coordinates']['coordinates']
    elif not tweet['place'] and not tweet['coordinates']:
        geo_info = None
    else:
        geo_info = tweet['place']

    return geo_info

def create_data(tweet):
    each_tweet = ' '.join(tweet)
    return each_tweet