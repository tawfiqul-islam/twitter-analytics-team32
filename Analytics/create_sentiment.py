
def calculate_pos_neg(sum_sentiment, pos, neg, threshold):
    if sum_sentiment > threshold:
        pos += 1
    elif sum_sentiment < -threshold:
        neg += 1
    return pos, neg


def calculate_emoti_senti(tweet, pos_emoticon, neg_emoticon, pos, neg):
    count_t_pos = 0
    count_t_neg = 0
    for word in tweet:
        if word in pos_emoticon:
            count_t_pos += 1
            continue
        if word in neg_emoticon:
            count_t_neg += 1
    if count_t_pos - count_t_neg > 0:
        pos += 1
    elif count_t_neg - count_t_pos > 0:
        neg += 1
    
    return pos, neg

def calculate_emoji_senti(tweet, emojis, pos, neg):

    cur_senti = 0.0
    for word in tweet:
        if word in emojis:
            cur_senti += emojis[word]

    if cur_senti > 0:
        pos += 1
    elif cur_senti < 0:
        neg += 1

    return pos, neg
    

def calculate_afinn_senti(tweet, afinn, pos, neg):
    sum_senti = 0.0
    threshold = 3
    for word in tweet:
        if word in afinn:
            sum_senti += afinn.get(word)
    
    pos, neg = calculate_pos_neg(sum_senti, pos, neg, threshold)
    
    return pos, neg
            
def calculate_minqing_senti(tweet, pos_minging, neg_minging, pos, neg):
    
    tweet_set = set(tweet)
    threshold = 0
    pos_num = len(tweet_set & pos_minging)
    neg_num = len(tweet_set & neg_minging)
    
    sum_sentiment = pos_num - neg_num
    
    
    pos, neg = calculate_pos_neg(sum_sentiment, pos, neg, threshold)
    
    return pos, neg


def create_training_set(tweet, train_data, train_label, pos, neg):
    p_or_n = 0
    if pos >= 2 and pos>neg:
        p_or_n = 1
        train_label.append(p_or_n)
        each_tweet = ' '.join(tweet)
        train_data.append(each_tweet)
    elif neg >= 2 and pos < neg:
        p_or_n = -1
        train_label.append(p_or_n)
        each_tweet = ' '.join(tweet)
        train_data.append(each_tweet)
    return pos, neg, train_data, train_label


def create_data(tweet, tweets):
    each_tweet = ' '.join(tweet)
    tweets.append(tweet)

    return tweets
