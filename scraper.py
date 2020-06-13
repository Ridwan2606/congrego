#importing necessary libraries
import twitter
import os
import nltk


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

#print(globalScrapeByWord("BLM"))

