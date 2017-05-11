import re
import spell_checker
import numpy

emoticons_str = r"""
    (?:
        [:=;] # Eyes
        [oO\-]? # Nose (optional)
        [D\)\]\(\]/\\OpP] # Mouth
        
    )"""
  
regex_str = [
    emoticons_str,
    r'<[^>]+>', # HTML tags
    r'(?:@[\w_]+)', # @-mentions
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)", # hash-tags
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', # URLs
    r'[\U0001F300-\U0001F64F]',
    r'[\U0001F600-\U0001F64F]',
    r'[\U0001F300-\U0001F5FF]',
    r'[\U0001F680-\U0001F6FF]',
    r'[\U0001F1E0-\U0001F1FF]',
    r'[\U0001F621-\U0001F640]',
    r'(?:(?:\d+,?)+(?:\.?\d+)?)', # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])", # words with - and '
    r'(?:[\w_]+)', # other words
    r'(?:\S)' # anything else
]

tokens_re = re.compile(r'('+'|'.join(regex_str)+')', re.VERBOSE | re.IGNORECASE)
emoticon_re = re.compile(r'^'+emoticons_str+'$', re.VERBOSE | re.IGNORECASE)

def tokenize(s):
    return tokens_re.findall(s)

def preprocess(s, lowercase=True):
    tokens = tokenize(s)
    if lowercase:
        tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
    return tokens

def filter_ad(terms_all, ad_list):
    should_break = False
    for ad in ad_list:
        if ad in terms_all:
            should_break = True
            break
    return should_break

def remove_duplicate(tweet):
    removed_tweet = []
    for token in tweet:
        token = re.sub(r'(.)\1+', r'\1\1', token)
        removed_tweet.append(token)
    return removed_tweet

# use this to process tweets
def process_tokens(tweet, stop, punctuation, emojis, WORDS, neg_list):
    terms_all = [term for term in preprocess(tweet)]
    pos_string = '[:;=＝]+\s*-*\s*[oO]*[dD)pP\]]'
    neg_string = r'[:;=＝]+\s*-*\s*[oO]*[(/\\]*'
    pos_regex = re.compile(pos_string)
    neg_regex = re.compile(neg_string)
    filter_words = [word for word in terms_all if word not in stop and not word.startswith('http') and word not in punctuation]

    filter_words = remove_duplicate(filter_words)
    filter_words = [word if word in WORDS 
                        or word.startswith('#') 
                        or word.startswith('@')
                        or word in emojis
                        or word in neg_list
                        or pos_regex.findall(word)
                        or neg_regex.findall(word)
                        else spell_checker.correction(word) for word in filter_words]
    # use to correct the tokens
    filter_words = [word for word in filter_words if word is not None]
    return filter_words

# use this to process tweets
def process_tokens_no_spell(tweet, stop, punctuation, emojis):
    terms_all = [term for term in preprocess(tweet)]

    filter_words = [word for word in terms_all if word not in stop and not word.startswith('http') and word not in punctuation]

    filter_words = remove_duplicate(filter_words)

    # use to correct the tokens
    filter_words = [word for word in filter_words if word is not None]
    return filter_words

# combine this with below function, we can process string vectors from douchdb
def multiple_replace(dict, text):

    regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))

    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text) 


def format_couchdata(features):
    dict = {
        "[" : "",
        "]" : "",
    } 

    train_features = [multiple_replace(dict, row) for row in train_features]
    # print(train_features)
    train_features = [row.split(',') for row in train_features]

    for i in range(len(train_features)):
        train_features[i] = list(map(int, train_features[i]))
    train_features = numpy.asarray(train_features)
    return train_features


def find_negation(target, text):
    result = []
    m = re.search(r'((?:\w+\W+){,1})('+ target + ')\W+((?:\w*\W*){,1})', text)
    if m:
        l = [ x.strip().split() for x in m.groups()]
    
        if l:
            for item in l[0]:
                result.append(item)
            for item in l[2]:
                result.append(item)

    return result