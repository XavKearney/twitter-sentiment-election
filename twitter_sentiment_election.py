import threading
import json
from time import sleep
import twitter
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Define Twitter OAuth credentials.
CONSUMER_KEY = "CONSUMER_KEY"
CONSUMER_SECRET = "CONSUMER_SECRET"
ACCESS_TOKEN = "ACCESS_TOKEN"
ACCESS_TOKEN_SECRET = "ACCESS_TOKEN_SECRET"

# Define search language and keywords for stream
LANGUAGES = ['en']
SEARCH_TERMS = ["GE2017", "GeneralElection", "Labour", "Conservatives", "Lib Dems", "SNP", "Theresa May",
                "Tim Farron", "Corbyn", "Liberal Democrats", "GE", "GE17", "Farron", "Scottish National Party",
                "election"]

# Define keywords for determining the party each tweet discusses on
CON_WORDS = ["conservatives", "tory", "tories", "conservative", "theresa may", "may", "theresa"]
LAB_WORDS = ["labour", "lab", "jeremy corbyn", "corbyn"]
LIB_WORDS = ["lib dem", "lib dems", "lib", "liberal", "democrats", "farron"]
SNP_WORDS = ["snp", "nicola sturgeon", "scottish national party", "sturgeon"]


def get_tweets(tweets):
    """
    Connects to the Twitter API using python-twitter and starts a stream connection based on the keywords provided.
    Takes as input a list of tweets and adds to it.
    Tweets are preferred in their extended (not truncated) form.
    """
    api = twitter.Api(consumer_key=CONSUMER_KEY,
                      consumer_secret=CONSUMER_SECRET,
                      access_token_key=ACCESS_TOKEN,
                      access_token_secret=ACCESS_TOKEN_SECRET,
                      tweet_mode='extended',
                      sleep_on_rate_limit=True)
    for line in api.GetStreamFilter(track=SEARCH_TERMS, languages=LANGUAGES):
        try:
            if line['truncated']:
                tweets.append(line['extended_tweet']['full_text'].rstrip('\r\n'))
            else:
                tweets.append(line['text'].rstrip('\r\n'))
        except KeyError as e:
            print("Malformed/unexpected JSON - likely a truncated tweet.")
            print(e)
    return tweets


def get_tweet_sentiment(tweets):
    """
    Uses the VADER SentimentIntensityAnalyzer from NLTK to classify tweet sentiment polarity.
    Takes in input a list of tweets (text-only, not JSON).
    Checks which party a tweet refers to and averages the score for all tweets for each party.
    Returns a dictionary of the parties and their average sentiment score (compound).
    """
    scores = {"con": [], "lab": [], "lib": [], "snp": []}
    averages = {"con": [], "lab": [], "lib": [], "snp": []}

    sid = SentimentIntensityAnalyzer()
    for tweet in tweets:
        ss = sid.polarity_scores(tweet.replace("#", ""))  # get the sentiment analysis scores for each tweet
        c_score = ss['compound']  # take the compound score, between -1 and 1
        if any(word in tweet.lower() for word in CON_WORDS):
            scores['con'].append(c_score)
        if any(word in tweet.lower() for word in LAB_WORDS):
            scores['lab'].append(c_score)
        if any(word in tweet.lower() for word in LIB_WORDS):
            scores['lib'].append(c_score)
        if any(word in tweet.lower() for word in SNP_WORDS):
            scores['snp'].append(c_score)

    for party, score_list in scores.items():
        if len(score_list) != 0:
            average = sum(score_list)/len(score_list)  # average sentiment per party per tweet
        else:
            average = 0
        averages[party] = average
    return averages


def save_scores(scores_dict):
    """
    Saves the scores in a dictionary to a JSON file to be read by the website wrapper.
    """
    total = 0
    for party, score in scores_dict.items():
        total += abs(score)
    if total == 0:  # if no sentiment, set 25% as the default width on the page
        scores_dict.update({party: .25 for party, s in scores_dict.items()})
    else:
        scores_dict.update({party: score * (1/total) for party, score in current_scores.items()})
    with open('scores.json', 'w') as f:  # write the JSON to file (overwriting previous)
        json.dump(current_scores, f)

if __name__ == "__main__":
    """
    Analyses General Election Tweet Sentiment using VADER with NLTK.
    Author: Xav Kearney
    April 23rd 2017
    Live Version: http://xavkearney.com/sentiment
    Requirements:
        https://github.com/bear/python-twitter
        http://www.nltk.org/ with VADER lexicon.
    """
    tweet_list = []
    tweet_stream = threading.Thread(target=get_tweets, args=(tweet_list,))
    tweet_stream.start()

    moving_averages = {"con": [], "lab": [], "lib": [], "snp": []}
    current_scores = {"con": [], "lab": [], "lib": [], "snp": []}
    while True:
        sleep(2)  # takes approx 2s to get a reasonable number of tweets
        averages = get_tweet_sentiment(tweet_list)  # get the average sentiment per tweet
        for party, score in averages.items():
            if len(moving_averages[party]) > 4:  # keep a moving average of 3 time periods
                del moving_averages[party][-1]
            moving_averages[party].insert(0, score)
            current_scores[party] = sum(moving_averages[party])/len(moving_averages[party])
        print("Current party scores: ".format(current_scores))
        save_scores(current_scores)
        if len(tweet_list) > 1000:
            tweet_list.clear()
            print("Reset the tweet list.")
