import re
def calculate_pos_neg(sum_sentiment, pos, neg, threshold, is_emo):
    if is_emo:
        if sum_sentiment > threshold:
            pos += 2
        elif sum_sentiment < -threshold:
            neg += 2
    else:
        if sum_sentiment > threshold:
            pos += 1
        elif sum_sentiment < -threshold:
            neg += 1
    return pos, neg


def calculate_emoti_senti(tweet, pos, neg):
    count_t_pos = 0
    count_t_neg = 0
    threshold = 0
    is_emo = True

    pos_string = '[:;=＝]+\s*-*\s*[oO]*[dD)pP\]]'
    neg_string = r'[:;=＝]+\s*-*\s*[oO]*[(/\\]*'
    pos_regex = re.compile(pos_string)
    neg_regex = re.compile(neg_string)


    for word in tweet:
        if pos_regex.findall(word):
            count_t_pos += 1
            continue
        if neg_regex.findall(word):
            count_t_neg += 1
    sum_senti = count_t_pos - count_t_neg
    pos, neg = calculate_pos_neg(sum_senti, pos, neg, threshold, is_emo)
    
    return pos, neg

def calculate_emoji_senti(tweet, emojis, pos, neg):

    cur_senti = 0.0
    threshold = 0.0
    is_emo = True
    for word in tweet:
        if word in emojis:
            cur_senti += emojis[word]

    pos, neg = calculate_pos_neg(cur_senti, pos, neg, threshold, is_emo)

    return pos, neg
    

def calculate_afinn_senti(tweet, afinn, pos, neg):
    sum_senti = 0.0
    threshold = 3
    is_emo = False
    for word in tweet:
        if word in afinn:
            sum_senti += afinn.get(word)
    
    pos, neg = calculate_pos_neg(sum_senti, pos, neg, threshold, is_emo)
    
    return pos, neg
            
def calculate_minqing_senti(tweet, pos_minging, neg_minging, pos, neg):
    
    tweet_set = set(tweet)
    threshold = 0
    is_emo = False
    pos_num = len(tweet_set & pos_minging)
    neg_num = len(tweet_set & neg_minging)
    
    sum_sentiment = pos_num - neg_num
    
    
    pos, neg = calculate_pos_neg(sum_sentiment, pos, neg, threshold, is_emo)
    
    return pos, neg



def create_data(tweet, tweets):
    each_tweet = ' '.join(tweet)
    tweets.append(tweet)

    return tweets

def total_sentiment(pos, neg):
    if pos >= 2 and pos>neg:
        p_or_n = 1
        return p_or_n
    elif neg >= 2 and pos < neg:
        p_or_n = -1
        return p_or_n
    elif pos == 0 and neg == 0:
        p_or_n = 0
        return p_or_n
    return 5
