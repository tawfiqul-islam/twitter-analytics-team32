
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


# def gen_set(pos_1_set, 
#     neg_1_set,
#     afinn_dict,
#     emojis,
#     WORDS,
#     tweet,
#     db,
#     db_target,
#     config,
#     couch,
#     count_all,
#     punctuation,
#     stop,
#     couchdb,
#     lga):


#     TWEET_HAS_PROCESSED = config['Analytics']['obj_has_processed']
#     TWEET_TEXT = config['Analytics']['obj_text']
#     ID_STR = 'id_str'
#     NONE = ""
#     COORDINATES = 'coordinates'
#     BOUNDING_BOX = 'bounding_box'
#     PLACE = 'place'
#     JSON = 'json'
#     SPACE = "\n\n\n\n\n"


#     # count # of pos neg neutral word determined by 4 dataset
#     count_positive = 0
#     count_negative = 0
#     ids = []
#     total_tweet = []
#     polarity_tweet = []
#     geo_codes = []
#     cur_senti = 5
#     count = 0
#     lga_dict = {}



#     if TWEET_TEXT in tweet:
#         if tweet[ID_STR] not in db_target:
#         # tweet = json[JSON]
#         # if not tweet[TWEET_HAS_PROCESSED]:
#             filter_words = preprocess.process_tokens(tweet[TWEET_TEXT], stop, punctuation, emojis, WORDS)
#             no_spell = preprocess.process_tokens_no_spell(tweet[TWEET_TEXT], stop, punctuation, emojis)

#             if len(filter_words) > 1:
#                 #calculate_emoti_senti(tweet, pos_emoticon, neg_emoticon, pos, neg):
#                 count_positive, count_negative = create_sentiment.calculate_emoti_senti(filter_words,
#                                                                                         count_positive,
#                                                                                         count_negative)

#                 count_positive, count_negative = create_sentiment.calculate_emoji_senti(filter_words,
#                                                                                        emojis,
#                                                                                        count_positive,
#                                                                                        count_negative)
#                 # use AFINN-111 sentiment word to label the tweet
#                 count_positive, count_negative = create_sentiment.calculate_afinn_senti(filter_words,
#                                                                                       afinn_dict,
#                                                                                       count_positive,
#                                                                                       count_negative)


#                 # use Minqing Hu and Bing Liu sentiment word to label the tweet
#                 count_positive, count_negative = create_sentiment.calculate_minqing_senti(filter_words,
#                                                                                         pos_1_set,
#                                                                                         neg_1_set,
#                                                                                         count_positive,
#                                                                                         count_negative)




#                 temp_text = create_data(filter_words)
#                 geo_info = gen_geo_info(tweet, COORDINATES, PLACE)
#                 coor, lga_code = gen_coordinates_lga(geo_info, BOUNDING_BOX, COORDINATES, lga)
                
#                 lga_dict[lga_code] = lga_code
#                 cur_senti = create_sentiment.total_sentiment(count_positive, count_negative)
#                 if cur_senti != 5:
#                     target_tweet = TweetData(
#                             _id = tweet[ID_STR],
#                             original_text = tweet[TWEET_TEXT],
#                             text = temp_text,
#                             no_spell_text = no_spell,
#                             label = cur_senti,
#                             tfid_features = NONE,
#                             features = NONE,
#                             geo_code = geo_info,
#                             is_read = False,
#                             coordinates = coor,
#                             lga_code = lga_code)
#                     print(target_tweet)
#                     # try:
#                     try:
#                         target_tweet.store(db_target)
#                         db.delete(tweet)
#  #                       ori_tweet = db.get(tweet[ID_STR])
#  #                       ori_tweet[TWEET_HAS_PROCESSED] = True
#  #                       db[tweet[ID_STR]] = ori_tweet

#                     except couchdb.http.ResourceConflict:
#                         pass







#             count_positive = 0
#             count_negative = 0
#     elif JSON in tweet:
#         if tweet[JSON][ID_STR] not in db_target:
#             tweet = tweet[JSON]
#             filter_words = preprocess.process_tokens(tweet[TWEET_TEXT], stop, punctuation, emojis, WORDS)
#             no_spell = preprocess.process_tokens_no_spell(tweet[TWEET_TEXT], stop, punctuation, emojis)

#             if len(filter_words) > 1:
#                 #calculate_emoti_senti(tweet, pos_emoticon, neg_emoticon, pos, neg):
#                 count_positive, count_negative = create_sentiment.calculate_emoti_senti(filter_words,
#                                                                                         count_positive,
#                                                                                         count_negative)

#                 count_positive, count_negative = create_sentiment.calculate_emoji_senti(filter_words,
#                                                                                        emojis,
#                                                                                        count_positive,
#                                                                                        count_negative)
#                 # use AFINN-111 sentiment word to label the tweet
#                 count_positive, count_negative = create_sentiment.calculate_afinn_senti(filter_words,
#                                                                                       afinn_dict,
#                                                                                       count_positive,
#                                                                                       count_negative)


#                 # use Minqing Hu and Bing Liu sentiment word to label the tweet
#                 count_positive, count_negative = create_sentiment.calculate_minqing_senti(filter_words,
#                                                                                         pos_1_set,
#                                                                                         neg_1_set,
#                                                                                         count_positive,
#                                                                                         count_negative)




#                 temp_text = create_data(filter_words)
#                 geo_info = gen_geo_info(tweet, COORDINATES, PLACE)
#                 coor, lga_code = gen_coordinates_lga(geo_info, BOUNDING_BOX, COORDINATES, lga)
#                 cur_senti = create_sentiment.total_sentiment(count_positive, count_negative)
#                 if cur_senti != 5:
#                     target_tweet = TweetData(
#                             _id = tweet[ID_STR],
#                             original_text = tweet[TWEET_TEXT],
#                             text = temp_text,
#                             no_spell_text = no_spell,
#                             label = cur_senti,
#                             tfid_features = NONE,
#                             features = NONE,
#                             geo_code = geo_info,
#                             is_read = False,
#                             coordinates = coor,
#                             lga_code = lga_code)
#                     try:
#                         target_tweet.store(db_target)
#                         # db.delete(tweet)

#                     except couchdb.http.ResourceConflict:
#                         pass








#                 count_positive = 0
#                 count_negative = 0
#     else:

#         print(tweet)
#         print(SPACE)


'''
    This is mainly used after the classifier has been trained and created
    Input are dictioinaries, tweet, lga object, target database classifier model 
            and counter model
    
    check lga code to see if the tweet in victoria

    If the tweet is in English:
        Generate the feature with negation and label it with sentiment and food tag (True, False)
    else:
        Label it with food tag

    Store back part of the processed tweets
'''

def gen_negation_set(
                    emojis,
                    WORDS,
                    tweet,
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
                    lr):


    TWEET_HAS_PROCESSED = config['Analytics']['obj_has_processed']
    TWEET_TEXT = config['Analytics']['obj_text']
    LANG = 'lang'
    ID_STR = 'id_str'
    NONE = ""
    COORDINATES = 'coordinates'
    BOUNDING_BOX = 'bounding_box'
    PLACE = 'place'
    JSON = 'json'
    SPACE = "\n\n\n\n\n"
    SPACE_1 = " "


    # count # of pos neg neutral word determined by 4 dataset
    count_positive = 0
    count_negative = 0
    ids = []
    total_tweet = []
    polarity_tweet = []
    geo_codes = []
    cur_senti = 5
    count = 0
    is_food = False
    lga_dict = {}
    neighbour_words = []
    negation_terms = []
    temp_dict = {}
    temp = []
    text_list = []


    # if TWEET_HAS_PROCESSED not in tweet:
    if True:
        if TWEET_TEXT in tweet:
            if tweet[ID_STR] not in db_target:

                geo_info, is_place, is_coordinates = gen_geo_info(tweet, COORDINATES, PLACE)
                coor, lga_code = gen_coordinates_lga(geo_info, BOUNDING_BOX, COORDINATES, lga, is_place, is_coordinates)
                if lga_code != 0:
                    is_food = gen_target_scenario(food_dict, tweet, TWEET_TEXT)
                    if tweet[LANG] == 'en':

                        filter_words = preprocess.process_tokens(tweet[TWEET_TEXT], stop, punctuation, emojis, WORDS, negation_list)
                        no_spell = preprocess.process_tokens_no_spell(tweet[TWEET_TEXT], stop, punctuation, emojis)
                        no_spell_text = create_data(no_spell)
                        temp_text = create_data(filter_words)

                        if len(filter_words) > 1:

                            for term in negation_list:
                                result = preprocess.find_negation(term, temp_text)
                                if result:
                                    negation_terms.append(term)
                                    for item in result:
                                        neighbour_words.append(item)


                            if neighbour_words:
                                for negation_term in negation_terms:
                                    temp = [negation_term+"_"+word for word in neighbour_words]
                                    for item in temp:
                                        temp_dict[item] = item
                                        temp_text = temp_text + SPACE_1 + item


                            text_list.append(temp_text)
                            text_feature = load_vec.transform(text_list)
                            cur_senti = lr.predict(text_feature.toarray())
                            

                            target_tweet = TweetData(
                                    _id = tweet[ID_STR],
                                    original_text = tweet[TWEET_TEXT],
                                    text = temp_text,
                                    no_spell_text = no_spell_text,
                                    label = cur_senti[0],
                                    tfid_features = NONE,
                                    features = "",
                                    geo_code = geo_info,
                                    is_read = False,
                                    coordinates = coor,
                                    lga_code = lga_code,
                                    tag_food = is_food)
                            # try:
                            try:
                                target_tweet.store(db_target)
                                # print(temp_text)
                                # print(cur_senti[0])
                                # ori_tweet = db.get(tweet[ID_STR])
                                # ori_tweet[TWEET_HAS_PROCESSED] = True
                                # db[tweet[ID_STR]] = ori_tweet


                            except couchdb.http.ResourceConflict:
                                pass
                    else:
                        target_tweet = TweetData(
                                        _id = tweet[ID_STR],
                                        original_text = tweet[TWEET_TEXT],
                                        text = NONE,
                                        no_spell_text = NONE,
                                        label = 5,
                                        tfid_features = NONE,
                                        features = NONE,
                                        geo_code = NONE,
                                        is_read = False,
                                        coordinates = NONE,
                                        lga_code = lga_code,
                                        tag_food = is_food)
                        try:
                            target_tweet.store(db_target)
                            # ori_tweet = db.get(tweet[ID_STR])
                            # ori_tweet[TWEET_HAS_PROCESSED] = True
                            # db[tweet[ID_STR]] = ori_tweet
                        except couchdb.http.ResourceConflict:
                            pass


'''
    This is mainly used to label the training and test data
    Input are dictionaries, tweet, row database, target database, lga object
    It labels the tweet when the sentiment is found by presence of word in the dictionaries
    * Only English tweet are labelled
'''

def gen_negation_train_set(pos_set, 
                    neg_set,
                    afinn_dict,
                    emojis,
                    WORDS,
                    tweet,
                    db,
                    db_target,
                    config,
                    couch,
                    count_all,
                    punctuation,
                    stop,
                    couchdb,
                    lga,
                    negation_list,
                    food_dict):


    TWEET_HAS_PROCESSED = config['Analytics']['obj_has_processed']
    # TWEET_TEXT = config['Analytics']['obj_text']
    LANG = 'lang'
    TWEET_TEXT = 'text'
    ID_STR = 'id_str'
    NONE = ""
    COORDINATES = 'coordinates'
    BOUNDING_BOX = 'bounding_box'
    PLACE = 'place'
    JSON = 'json'
    SPACE_1 = " "
    SPACE = "\n\n\n\n\n"
    NO_LGA_PROCESSED = 'no_lga_processed'


    # count # of pos neg neutral word determined by 4 dataset
    count_positive = 0
    count_negative = 0
    ids = []
    total_tweet = []
    polarity_tweet = []
    geo_codes = []
    cur_senti = 5
    count = 0
    is_food = False
    is_lexical = False
    lga_dict = {}
    neighbour_words = []
    negation_terms = []
    temp_dict = {}



    if TWEET_TEXT in tweet:
        # if tweet[ID_STR] not in db_target:
            if NO_LGA_PROCESSED not in tweet:
                geo_info, is_place, is_coordinates = gen_geo_info(tweet, COORDINATES, PLACE)
                coor, lga_code = gen_coordinates_lga(geo_info, BOUNDING_BOX, COORDINATES, lga, is_place, is_coordinates)
                # if lga_code != 0:
                is_food = gen_target_scenario(food_dict, tweet, TWEET_TEXT)
                if tweet[LANG] == 'en':


                    filter_words = preprocess.process_tokens(tweet[TWEET_TEXT], stop, punctuation, emojis, WORDS, negation_list)
                    no_spell = preprocess.process_tokens_no_spell(tweet[TWEET_TEXT], stop, punctuation, emojis)

                    temp_text = create_data(filter_words)

                    if len(filter_words) > 1:


                        for term in negation_list:
                            result = preprocess.find_negation(term, temp_text)

                            if result:
                                negation_terms.append(term)
                                for item in result:
                                    neighbour_words.append(item)


                        #calculate_emoti_senti(tweet, pos_emoticon, neg_emoticon, pos, neg):
                        count_positive, count_negative = create_sentiment.calculate_emoti_senti(filter_words,
                                                                                                count_positive,
                                                                                                count_negative)

                        count_positive, count_negative = create_sentiment.calculate_emoji_senti(filter_words,
                                                                                               emojis,
                                                                                               count_positive,
                                                                                               count_negative)
                        

                        if count_positive == 0 and count_negative == 0:


                            word_dict, sum_senti = create_sentiment.create_senti_and_word(filter_words, 
                                                                                            neighbour_words, 
                                                                                            afinn_dict, 
                                                                                            pos_set, 
                                                                                            neg_set, 
                                                                                            count_positive, 
                                                                                            count_negative)

                            if word_dict:
                                for negation_term in negation_terms:
                                    temp = [negation_term+"_"+word for word in word_dict]
                                    for item in temp:
                                        temp_dict[item] = item
                                        temp_text = temp_text + SPACE_1 + item


                            if sum_senti > 0:
                                if word_dict:
                                    count_positive = 0
                                    count_negative = 2
                                elif not word_dict:
                                    count_positive = 2
                                    count_negative = 0
                            elif sum_senti < 0:
                                if word_dict:
                                    count_positive = 2
                                    count_negative = 0
                                elif not word_dict:
                                    count_positive = 0
                                    count_negative = 2


            
                        lga_dict[lga_code] = lga_code
                        cur_senti = create_sentiment.total_sentiment(count_positive, count_negative)

                        if cur_senti != 5:
                            target_tweet = TweetData(
                                    _id = tweet[ID_STR],
                                    original_text = tweet[TWEET_TEXT],
                                    text = temp_text,
                                    no_spell_text = no_spell,
                                    label = cur_senti,
                                    tfid_features = NONE,
                                    features = NONE,
                                    geo_code = geo_info,
                                    is_read = False,
                                    coordinates = coor,
                                    lga_code = lga_code,
                                    tag_food = is_food)

                            # try:
                            try:
                                target_tweet.store(db_target)
                                print(temp_text)
                                # db.delete(tweet)
                                # ori_tweet = db.get(tweet[ID_STR])
                                # ori_tweet[NO_LGA_PROCESSED] = True
                                # db[tweet[ID_STR]] = ori_tweet

                            except couchdb.http.ResourceConflict:
                                pass



'''
    Check the kinds of different geo info in the tweet
    As some tweets only contain place with bounding box without coordinates, 
        some only contain coordinates without place and without bounding box
'''
def gen_geo_info(tweet, coordinates, place):
    is_place = False
    is_coordinates = False
    if tweet[place] and not tweet[coordinates]:
        geo_info = tweet[place]
        is_place = True
    elif tweet[coordinates] and not tweet[place]:
        if coordinates in  tweet[coordinates]:
            print(tweet[coordinates])
            geo_info = tweet[coordinates][coordinates]
            is_coordinates=True
    elif not tweet[place] and not tweet[coordinates]:
        geo_info = None
    else:
        geo_info = tweet[place]
        is_place=True

    return geo_info, is_place, is_coordinates


'''

'''

def gen_coordinates_lga(geo_info, bounding_box, coordinates, lga, is_place, is_coordinates):
    coordinates = 'coordinates'
    bounding_box = 'bounding_box'
    geo = None
    lga_code = 0
    if geo_info:
        if is_coordinates:
            geo = geo_info
            lga_code = lga.get_code_from_coordinates(geo_info[0], geo_info[1])
        if is_place:
            if bounding_box in geo_info:
                if geo_info[bounding_box]:
                    if coordinates in geo_info[bounding_box]:
                        if geo_info[bounding_box][coordinates]:
                            temp = geo_info[bounding_box][coordinates][0]
                            geo = []
                            temp_lat = 0.0
                            temp_long = 0.0
                            for i in range(len(temp)):
                                temp_lat += temp[i][0]
                                temp_long += temp[i][1]
                            temp_lat /= 4
                            temp_long /= 4
                            geo.append(temp_lat)
                            geo.append(temp_long)
                            lga_code = lga.get_code_from_coordinates(temp_lat, temp_long)
         


    return geo, lga_code


'''
    Convert the tokens to sentence
'''

def create_data(tweet):
    each_tweet = ' '.join(tweet)
    return each_tweet


'''
    Input are the scenario dictionary, text of tweet
    It checks if the given tweet belongs to that scenario
'''
def gen_target_scenario(dict, tweet, text):
    is_scenario = False
    for item in dict:
        word_list = item.split(' ')
        match_length = 0
        for word in word_list:
            if word in tweet[text]:
                match_length += 1
        if match_length == len(word_list):
            is_scenario = True
    return is_scenario




