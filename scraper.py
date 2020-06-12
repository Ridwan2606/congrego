
import twitter
import os

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

def buildTestSet(search_keyword):
    try:
        tweets_fetched = twitter_api.GetSearch(search_keyword, count = 100)
        
        print("Fetched " + str(len(tweets_fetched)) + " tweets for the term " + search_keyword)
        
        return [status.text for status in tweets_fetched]
    except:
        print("Unfortunately, something went wrong..")
        return None

count = 1
for status in buildTestSet("Covid-19"):
    print( str(count) + ".) " + status)
    count+=1