import sys
import json
import re
import string
import codecs
import os

def load_afinn():
    scores = {} # initialize an empty dictionary
    with open(os.path.join('./Dict', "AFINN-111.txt")) as afinnfile:
        for line in afinnfile:
            term, score  = line.split("\t")  
            scores[term] = int(score)
    afinnfile.close()

    return scores 


##########
### sentiment word list from Minqing Hu and Bing Liu
##########
def load_minging_dict():
    
    neg_1 = []
    pos_1 = []
    #negative-words.txt
    with codecs.open(os.path.join('./Dict', "negative-words.txt"), encoding='utf-8', errors='ignore') as new:
    # with open('negative-words.txt', 'r') as new:
        for line in new:
            li=line.strip()
            if not li.startswith(";"):
                neg_1.append(li)
    new.close()
    #positive-words
    with open(os.path.join('./Dict', "positive-words.txt")) as new:
        for line in new:
            li=line.strip()
            if not li.startswith(";"):
                pos_1.append(li)
    new.close()

    neg_1_set = set(neg_1)
    pos_1_set = set(pos_1)
    return pos_1_set, neg_1_set




def load_emoti():
    positive_emoticon = [ ':)', ':D', ':)', 
                        ':p', ':P', ':d', ':-)' , 
                        ':-D', ': D', ': P', '; D', 
                        '; p', '; d', '; P', ': p', 
                        ';/', ';)', ';D', ';d', '; )', 
                        ';p', ';P', '; (', '= P', ';-)', 
                        '= d', ':  D', '= p', ': )', '=)', 
                        '=P', '=d', ':d' , '=p', ': ]', ';  p',
                        ';  d','=D', ';  )',  ': OD','= )',  ':   p', 
                        ':   P', ';]']
    negative_emoticon = [':/', ':(', ':-(', '://', ':-\\', ': (', 
                        '=/', '; \\', ';/' , '=/', '; /', '= (', '=(', 
                        ': \\', ';(', '=\\', ';----- (',':\\', ':-\\', ': O/']
    neutral_emoticon = ['; o', ': Ooo', '; O', ': o',  ';o', ': d', 
                        ': Od', '= O', '= o', ':o', ';O', '; Op', '=o', 
                        ': Ooooooo', '; Od', '; OP', ': OP', ';  O', ': Oop', 
                        ': Oooo', ': Oo', ': oo', ': --- O',';-- D', ':  o', 
                        ': od', ': ooooooo']
    return positive_emoticon, negative_emoticon, neutral_emoticon

def load_emoji():
    count = True
    emojis = {}
    with open(os.path.join('./Dict', "emojis.txt")) as file:
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


