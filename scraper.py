#importing necessary libraries
import twitter
import os

from nltk.tag import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords

import re, string, pickle

import json
import pickle
import boto3


# Add some for sampling. Will define the real countries/cities to scrape from later.
# Geocodes maps from country name to city name to geocode (latitude,longitude,radius)
geocodes={
    "Canada": {
        "Toronto": [37.781157, -122.398720, "1mi"],
        "Montreal": [37.781157, -122.398720, "1mi"],
        "British Columbia": [37.781157, -122.398720, "1mi"]
    },
    "USA": {
        "New York": [37.781157, -122.398720, "1mi"]
    },
    "Australia":{
        "Perth": [37.781157, -122.398720, "1mi"],
        "Melbourne": [37.781157, -122.398720, "1mi"]
    }
}

# initialising the API keys from the environmental variables for security
con_key = os.environ.get("twitter_consumer_key")
con_secret = os.environ.get("twitter_consumer_secret")
token_key = os.environ.get("twitter_access_token_key")
token_secret = os.environ.get("twitter_access_token_secret")

# initialize api instance
twitter_api = twitter.Api(consumer_key=con_key,
                        consumer_secret=con_secret,
                        access_token_key=token_key,
                        access_token_secret=token_secret)

# test authentication
#print(twitter_api.VerifyCredentials())


#Fetching the NLP model from s3 bucket
s3 = boto3.resource('s3')

with open('/tmp/model.pickle', 'wb') as data:
    s3.Bucket("nlp-model-twitter").download_fileobj("model.pickle", data)

# classifier variable stores the NLP model
with open('/tmp/model.pickle', 'rb') as data:
    classifier = pickle.load(data)

dynamodb = boto3.resource('dynamodb')

def printTweets(tweetList):
    count = 1
    for tweet in tweetList:
        print( str(count) + ".) " + tweet)
        count+=1

def getTweetsByWord(search_keyword):
    try:
        tweets_fetched = twitter_api.GetSearch(search_keyword, count = 100,lang="en", result_type="recent")
        
        print("Fetched " + str(len(tweets_fetched)) + " tweets for the term " + search_keyword)
        
        return [status.text for status in tweets_fetched]
    except:
        print("Unfortunately, something went wrong..")
        return None

def getTweetsByWordCountry(search_keyword, search_country):
    tweets_fetched = []
    print("-- Gathering Tweets from " + search_country)
    try:
        for city,position in geocodes[search_country].items():
            new_tweets = twitter_api.GetSearch(search_keyword, geocode= position,count = 100,lang="en", result_type="recent")
            print("\tFetched " + str(len(new_tweets)) + " tweets for the keyword '" + search_keyword + "' from " + str(position) + " in " + city + ", " + search_country)
            tweets_fetched += new_tweets
        return [tweet.text for tweet in tweets_fetched]
    except:
        print("Error. Could not fetch tweets...")
        return None

def globalScrapeByWord(search_keyword):
    scrapeDict = {}
    for country in geocodes.keys():
        scrapeDict[country] = getTweetsByWordCountry(search_keyword,country)
    return scrapeDict

def remove_noise(tweet_tokens, stop_words = ()):

    cleaned_tokens = []

    for token, tag in pos_tag(tweet_tokens):
        token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', token)
        token = re.sub("(@[A-Za-z0-9_]+)","", token)

        if tag.startswith("NN"):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'

        lemmatizer = WordNetLemmatizer()
        token = lemmatizer.lemmatize(token, pos)

        if len(token) > 0 and token not in string.punctuation and token.lower() not in (stop_words + ('AT_USER','URL')):
            cleaned_tokens.append(token.lower())
    return cleaned_tokens

print(globalScrapeByWord("COVID"))

# Returns the percentage of positive tweets out of total number of tweets for that country
def getSentimentByCountry(tweetList):
    totalNo = len(tweetList)
    posNo = 0
    for tweet in tweetList:
        custom_tokens = remove_noise(word_tokenize(tweet))
        prediction = classifier.classify(dict([token, True] for token in custom_tokens))
        #print("Model predicts that the sentence is : " + prediction + "\n")
        if prediction="Positive":
            posNo += 1
    return (posNo*100)/totalNo

def lambda_handler(event, context):
    tweetsForCountry = globalScrapeByWord("COVID")
    countrySentimentDict = {}
    for country,tweetList in tweetsForCountry.items():
        countrySentimentDict[country] = getSentimentByCountry(tweetList)
    
    table = dynamodb.Table('Country_Sentiment')

    for country,sentiment in countrySentimentDict.items():
        table.put_item(
            Item={
                    'country': country,
                    'sentiment': sentiment
                }
        )

    #TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Scraping Done. Country_Sentiment table updated with sentiment analysis for each country')
    }





