import sys
import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def loadkeys(filename):
    """"
    load twitter api keys/tokens from CSV file with form
    consumer_key, consumer_secret, access_token, access_token_secret
    """
    with open(filename) as f:
        items = f.readline().strip().split(', ')
        return items


def authenticate(twitter_auth_filename):
    """
    Given a file name containing the Twitter keys and tokens,
    create and return a tweepy API object.
    """
    consumer_key, consumer_secret, \
    access_token, access_token_secret \
        = loadkeys(twitter_auth_filename)
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    return api


def fetch_tweets(api, name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    create a list of tweets where each tweet is a dictionary with the
    following keys:

       id: tweet ID
       created: tweet creation date
       retweeted: number of retweets
       text: text of the tweet
       hashtags: list of hashtags mentioned in the tweet
       urls: list of URLs mentioned in the tweet
       mentions: list of screen names mentioned in the tweet
       score: the "compound" polarity score from vader's polarity_scores()

    Return a dictionary containing keys-value pairs:

       user: user's screen name
       count: number of tweets
       tweets: list of tweets, each tweet is a dictionary

    For efficiency, create a single Vader SentimentIntensityAnalyzer()
    per call to this function, not per tweet.
    """
    rdict = {}
    user = api.get_user(name)
    rdict['user'] = name
    rdict['count'] = user.statuses_count
    rdict['tweets'] = []
    SIA = SentimentIntensityAnalyzer()
    for status in tweepy.Cursor(api.user_timeline, id=name).items(100):
        tweet = {}
        tweet['id'] = status.id
        tweet['created'] = status.created_at
        tweet['retweeted'] = status.retweet_count
        tweet['text'] = status.text
        tweet['hashtags'] = status.entities['hashtags']
        tweet['urls'] = [u['url'] for u in status.entities['urls']]
        tweet['mentions'] = [d['screen_name'] for d in status.entities['user_mentions']]
        tweet['score'] = SIA.polarity_scores(status.text)['compound']
        rdict['tweets'].append(tweet)
    return rdict


def fetch_following(api,name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    return a a list of dictionaries containing the followed user info
    with keys-value pairs:

       name: real name
       screen_name: Twitter screen name
       followers: number of followers
       created: created date (no time info)
       image: the URL of the profile's image

    To collect data: get a list of "friends IDs" then get
    the list of users for each of those.
    """
    rlist = []
    for friend in tweepy.Cursor(api.friends, id=name).items(100):
        udict = {}
        udict['name'] = friend.name
        udict['screen_name'] = friend.screen_name
        udict['followers'] = friend.followers_count
        udict['created'] = friend.created_at
        udict['image'] = friend.profile_image_url
        rlist.append(udict)
    return rlist

