import sys
import json
import re
import string
import codecs
import os

def load_afinn(file_name):
    scores = {} # initialize an empty dictionary
    with open(os.path.join('./Dict', file_name)) as afinnfile:
        for line in afinnfile:
            term, score  = line.split("\t")  
            scores[term] = int(score)
    afinnfile.close()

    return scores 


##########
### sentiment word list from Minqing Hu and Bing Liu
##########
def load_minging_dict(file_name_pos, file_name_neg):
    
    neg_1 = []
    pos_1 = []
    #negative-words.txt
    with codecs.open(os.path.join('./Dict', file_name_neg), encoding='utf-8', errors='ignore') as new:
    # with open('negative-words.txt', 'r') as new:
        for line in new:
            li=line.strip()
            if not li.startswith(";"):
                neg_1.append(li)
    new.close()
    #positive-words
    with open(os.path.join('./Dict', file_name_pos)) as new:
        for line in new:
            li=line.strip()
            if not li.startswith(";"):
                pos_1.append(li)
    new.close()

    neg_1_set = set(neg_1)
    pos_1_set = set(pos_1)
    return pos_1_set, neg_1_set


def load_emoji(file_name):
    count = True
    emojis = {}
    with open(os.path.join('./Dict', file_name)) as file:
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


