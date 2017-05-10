import sys
import json
import re
import string
import codecs
import os

def load_afinn(dict_dir, file_name):
    scores = {} # initialize an empty dictionary
    with open(os.path.join(dict_dir, file_name)) as afinnfile:
        for line in afinnfile:
            term, score  = line.split("\t")  
            scores[term] = int(score)
    afinnfile.close()

    return scores 


##########
### sentiment word list from Minqing Hu and Bing Liu
##########
def load_minging_dict(dict_dir, file_name_pos, file_name_neg):
    
    neg_1 = []
    pos_1 = []
    #negative-words.txt
    with codecs.open(os.path.join(dict_dir, file_name_neg), encoding='utf-8', errors='ignore') as new:
    # with open('negative-words.txt', 'r') as new:
        for line in new:
            li=line.strip()
            if not li.startswith(";"):
                neg_1.append(li)
    new.close()
    #positive-words
    with open(os.path.join(dict_dir, file_name_pos)) as new:
        for line in new:
            li=line.strip()
            if not li.startswith(";"):
                pos_1.append(li)
    new.close()

    neg_1_set = set(neg_1)
    pos_1_set = set(pos_1)
    return pos_1_set, neg_1_set


def load_emoji(dict_dir, file_name):
    count = True
    emojis = {}
    with open(os.path.join(dict_dir, file_name)) as file:
        for line in file:
            if count:
                emoji, _, _, _, _, _, _, _, score = line.rstrip().split('\t')
                emojis[emoji] = float(score)
                count = False
            else:
                count=True
                continue
    file.close()
    return emojis

def load_stopwords():
    stops = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 
    'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 
    'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 
    'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 
    'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 
    'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 
    'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 
    'for', 'with', 'about', 'between', 'into', 'through', 'during', 'before', 'after', 
    'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 
    'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 
    'why', 'how', 'all', 'any', 'both', 'each', 'so', 'than']

    return stops

def load_negation_list():
    negation_list = ['not', 'never', 'no', 'n\'t', 'nope', 'non', 'nor', 'while', 'but', 'however', 'wherea']
    return negation_list

def load_food_dict(dict_dir, file_name):
    food_dict = []
    with open(os.path.join(dict_dir, file_name)) as file:
        for line in file:
            line = line.rstrip()
            line = line.lower()
            food_dict.append(line)
    return food_dict
    


