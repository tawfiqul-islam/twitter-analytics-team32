
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


def gen_set(pos_1_set, 
    neg_1_set,
    afinn_dict,
    emojis,
    db,
    doc_ids):

    #########
    ### create the bag of words
    #########

    count_all = Counter()
    nltk.download('stopwords')

    punctuation = list(string.punctuation)
    stop = stopwords.words('english')
    WORDS = Counter(spell_checker.words(os.path.join('./Dict', "words_new.txt")))

    # count # of pos neg neutral word determined by 4 dataset
    count_positive = 0
    count_negative = 0
    ids = []
    total_tweet = []
    polarity_tweet = []
    geo_codes = []

    count = 0

    for doc_id in doc_ids:
        tweet = db[doc_id]
        terms_all = [term for term in preprocess.preprocess(tweet['text'])]
        filter_words = preprocess.process_tokens(terms_all, stop, punctuation, emojis, WORDS)
        count += 1
        if count % 10 == 0:
            print(count)
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

            if not tweet['coordinates']:
                tweet['coordinates'] = '[0, 0]'

            #create_training_set(tweet, train_data, train_label, pos, neg, total_pos, total_neg, total_neu):
            count_positive, count_negative, total_tweet, polarity_tweet, ids, geo_codes  = create_sentiment.create_training_set(filter_words,                                
                                                                                                                                total_tweet,
                                                                                                                                polarity_tweet,
                                                                                                                                tweet['id'],
                                                                                                                                ids,
                                                                                                                                tweet['coordinates'],
                                                                                                                                geo_codes,
                                                                                                                                count_positive,
                                                                                                                                count_negative)
            count_positive = 0
            count_negative = 0
    return total_tweet, polarity_tweet, ids, geo_codes

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

