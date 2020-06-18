import tweepy
from textblob import TextBlob
import pandas as pd
import numpy as np
import redis
import schedule
import time
import re
import os


consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
key = os.getenv("KEY")
secret = os.getenv("SECRET")

client = redis.Redis(host="10.10.10.1", port=6379,
                     password=os.getenv("REDIS_PASS"))
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(key, secret)
auth.secure = True
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

tweets = api.mentions_timeline()


def read_last_seen():
    # file_read = open(FILE_NAME, 'r')
    # last_seen_id = int(file_read.read().strip())
    # file_read.close()
    last_seen_id = int(client.get('last_seen_id'))
    return last_seen_id


def store_last_seen(last_seen_id):
    # file_write = open(FILE_NAME, 'w')
    # file_write.write(str(last_seen_id))
    # file_write.close()
    client.set('last_seen_id', str(last_seen_id))
    return

#store_last_seen(FILE_NAME, '1194877411671724066')

def reply():
    # print("Checking for any mentions")
    # print(time.ctime())
    tweets = api.mentions_timeline(
        read_last_seen(), tweet_mode='extended')
    for tweet in reversed(tweets):
        #if 'bullish' in tweet.full_text.lower():
        try:
            print("Replied to ID - " + str(tweet.id) + " - " + tweet.full_text)
            username = tweet.user.screen_name
            if username != "CalendarKy":
                api.update_status("@" + username +
                                    " Hello, " + username + " this is an automated reply. @CalendarKy could you please help me out?", tweet.id)
            #api.retweet(tweet.id)
            api.create_favorite(tweet.id)
            store_last_seen(tweet.id)
        except tweepy.TweepError as e:
            print(e.reason)
            time.sleep(2)

tweetNumber = 2

tweets = tweepy.Cursor(api.search, "#bullmarket").items(tweetNumber)


def searchBot():
    print("Running first search.")
    print(time.ctime())
    for tweet in tweets:
        try:
            tweet.retweet()
            print("Retweet done!")
            api.create_favorite(tweet.id)
            time.sleep(2)
        except tweepy.TweepError as e:
            print(e.reason)
            time.sleep(2)

new_tweets = tweepy.Cursor(api.search, "bull gang").items(tweetNumber)


def searchBot2():
    print("Running second search.")
    print(time.ctime())
    for tweet in new_tweets:
        try:
            tweet.retweet()
            print("Retweet 2 done!")
            time.sleep(2)
        except tweepy.TweepError as e:
            print(e.reason)
            time.sleep(2)

newer_tweets = tweepy.Cursor(api.search, "stock market").items(200)

def searchBot3():
    print("Running third search.")
    print(time.ctime())
    i = 0
    for tweet in newer_tweets:
        i += 1
        try:
            api.create_favorite(tweet.id)
            if i % 20 == 0:
                print(f"Favorited {i} stock market tweets")
            time.sleep(2)
        except tweepy.TweepError as e:
            print(e.reason)
            time.sleep(2)

def tweet_sentiment():
    # print(time.ctime())
    client = redis.Redis(host="10.10.10.1", port=6379,
                         password=os.getenv("REDIS_PASS"))
    sentiment = client.get('twit_bot').decode("utf-8")
    status = "I am currently {} the stock market.".format(sentiment)
    print(status)
    print("Updating our status to our current sentiment.")
    api.update_status(status)


def follow_followers():
    # print(time.ctime())
    # print("Retrieving and following followers")
    for follower in tweepy.Cursor(api.followers).items():
        if not follower.following:
            print(f"Following {follower.name}")
            follower.follow()


def scrape_twitter(maxTweets, searchQuery, redisDataBase):
    # print(time.ctime())
    client.delete(redisDataBase)
    print(f"Downloading max {maxTweets} tweets")
    retweet_filter = '-filter:retweets'
    q = searchQuery+retweet_filter
    tweetCount = 0
    max_id = -1
    tweetsPerQry = 100
    redisDataBase = 'tweets_scraped'
    sinceId = None
    while tweetCount < (maxTweets-50):
        try:
            if (max_id <= 0):
                if (not sinceId):
                    new_tweets = api.search(
                        q=q, lang="en", count=tweetsPerQry, tweet_mode='extended')

                else:
                    new_tweets = api.search(q=q, lang="en", count=tweetsPerQry,
                                            since_id=sinceId, tweet_mode='extended')
            else:
                if (not sinceId):
                    new_tweets = api.search(q=q, lang="en", count=tweetsPerQry,
                                            max_id=str(max_id - 1), tweet_mode='extended')
                else:
                    new_tweets = api.search(q=q, lang="en", count=tweetsPerQry,
                                            max_id=str(max_id - 1),
                                            since_id=sinceId, tweet_mode='extended')

            if not new_tweets:
                print("No more tweets found")
                break
            for tweet in new_tweets:
                client.sadd(redisDataBase, (str(tweet.full_text.replace(
                    '\n', '').encode("utf-8"))+"\n"))
            tweetCount += len(new_tweets)
            # print(f"Downloaded {tweetCount} tweets")
            max_id = new_tweets[-1].id

        except tweepy.TweepError as e:
            # Just exit if any error
            print("some error : " + str(e))
            break

    print(f"Downloaded {tweetCount} tweets, Saved to {redisDataBase}")

    # print(client.smembers(redisDataBase))


def clean(tweet):
    tweet = re.sub(r'^RT[\s]+', '', tweet)
    tweet = re.sub(r'https?:\/\/.*[\r\n]*', '', tweet)
    tweet = re.sub(r'#', '', tweet)
    tweet = re.sub(r'@[A-Za-z0–9]+', '', tweet)
    return tweet


def read_tweets(redis_set):
    f = client.smembers(redis_set)
    tweets = [clean(sentence.decode("utf-8").strip()) for sentence in f]
    return tweets


def polarity(x): return TextBlob(x).sentiment.polarity


def subjectivity(x): return TextBlob(x).sentiment.subjectivity


def run_scraper():
    redisDataBase = "tweets_scraped"
    scrape_twitter(3000, 'stock market', redisDataBase)
    f = read_tweets(redisDataBase)
    # print(f)
    tweet_polarity = np.zeros(client.scard(redisDataBase))
    tweet_subjectivity = np.zeros(client.scard(redisDataBase))
    bullish_count = 0
    bearish_count = 0
    for idx, tweet in enumerate(f):
        tweet_polarity[idx] = polarity(tweet)
        tweet_subjectivity[idx] = subjectivity(tweet)
        if tweet_polarity[idx] > 0.15 and tweet_subjectivity[idx] < 0.5:
            bullish_count += 1

        elif tweet_polarity[idx] < 0.00 and tweet_subjectivity[idx] < 0.5:
            bearish_count += 1
    bullish_count -= 35
    sentiment = (bullish_count) - bearish_count
    print(f"Bullish count is {bullish_count}")
    print(f"Bearish count is {bearish_count}")
    print(f"Sentiment count is {sentiment}")
    to_string = "null"
    if sentiment > 30:
        to_string = "Twitter sentiment of the stock market is bullish with a reading of {}.".format(
            sentiment)
        current_high = int(client.get('highest_sentiment'))
        if sentiment > current_high:
            client.set('highest_sentiment', str(sentiment))
            to_string = "{} This is the highest reading to date.".format(to_string)
    elif sentiment > -5:
        to_string = "Twitter sentiment of the stock market is nuetral with a reading of {}.".format(
            sentiment)
    else:
        to_string = "Twitter sentiment of the stock market is bearish with a reading of {}.".format(
            sentiment)
        current_low = int(client.get('lowest_sentiment'))
        if sentiment < current_low:
            client.set('lowest_sentiment', str(sentiment))
            to_string = "{} This is the lowest reading to date.".format(
                to_string)
    print(to_string)
    api.update_status(to_string)


print(time.ctime())
schedule.every().day.at("15:13").do(tweet_sentiment)
schedule.every().day.at("09:17").do(searchBot)
schedule.every().day.at("12:12").do(searchBot2)
schedule.every().day.at("17:03").do(searchBot3)
schedule.every().day.at("09:06").do(searchBot3)
schedule.every(15).minutes.do(reply)
schedule.every(20).minutes.do(follow_followers)
schedule.every(5).hours.do(run_scraper)


while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except tweepy.TweepError as e:
        print(e.reason)
        time.sleep(1)
