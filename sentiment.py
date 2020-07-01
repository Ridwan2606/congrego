from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import twitter_samples, stopwords
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from nltk import FreqDist, classify, NaiveBayesClassifier
import pickle
import re, string, random
from string import punctuation

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

def get_all_words(cleaned_tokens_list):
    for tokens in cleaned_tokens_list:
        for token in tokens:
            yield token

def get_tweets_for_model(cleaned_tokens_list):
    for tweet_tokens in cleaned_tokens_list:
        yield dict([token, True] for token in tweet_tokens)

if __name__ == "__main__":

    '''
    positive_tweets = twitter_samples.strings('positive_tweets.json')
    negative_tweets = twitter_samples.strings('negative_tweets.json')
    text = twitter_samples.strings('tweets.20150430-223406.json')
    tweet_tokens = twitter_samples.tokenized('positive_tweets.json')[0]
    '''
    print(" - SCRIPT LAUNCHED - \n")

    try: 
        classifier_f = open("model.pickle", "rb")
        classifier = pickle.load(classifier_f)
        classifier_f.close()
        print(" - MODEL HAS BEEN LOADED - \n")

    except FileNotFoundError:
        print("model.pickle is not present. Proceeding to build the model from corpus data...")
        print(" -  COLLECTING DATA (TWEETS) FROM CORPUS - ")
        print("Loading English stopwords...")
        stop_words = stopwords.words('english')

        print("Loading 500 positive tweets...")
        positive_tweet_tokens = twitter_samples.tokenized('positive_tweets.json')
        print("Loading 500 negative tweets...\n")
        negative_tweet_tokens = twitter_samples.tokenized('negative_tweets.json')

        positive_cleaned_tokens_list = []
        negative_cleaned_tokens_list = []

        print( " - PREPOCESSING DATA ( REMOVING NOISE, LEMMATIZATION, NORMALIZATION, TOKENISATION) - \n")
        print( "Preprocessing the 5000 positive tweets... ")
        count = 1
        for tokens in positive_tweet_tokens:
            positive_cleaned_tokens_list.append(remove_noise(tokens, stop_words))
            print("Tweet " + str(count) + " preprocessed ... ")
            count+=1
        print( "Preprocessing the 5000 negative tweets... ")
        count = 1
        for tokens in negative_tweet_tokens:
            negative_cleaned_tokens_list.append(remove_noise(tokens, stop_words))
            print("Tweet " + str(count) + " preprocessed ... ")
            count+=1

        '''
        all_pos_words = get_all_words(positive_cleaned_tokens_list)
        freq_dist_pos = FreqDist(all_pos_words)
        print(freq_dist_pos.most_common(10))
        '''

        print("\n - BUILDING NLP MODEL - \n")

        print("Creating dictionaries... ")
        positive_tokens_for_model = get_tweets_for_model(positive_cleaned_tokens_list)
        negative_tokens_for_model = get_tweets_for_model(negative_cleaned_tokens_list)

        print("Assigining labels to the data...")
        positive_dataset = [(tweet_dict, "Positive")
                            for tweet_dict in positive_tokens_for_model]

        negative_dataset = [(tweet_dict, "Negative")
                            for tweet_dict in negative_tokens_for_model]

        dataset = positive_dataset + negative_dataset

        print("Merging and shuffling positive and negative tweets...")
        random.shuffle(dataset)

        print("Splitting into training data (7000 tweets) and test data(3000 tweets) ...")
        train_data = dataset[:7000]
        test_data = dataset[7000:]

        print("Training model...\n")
        classifier = NaiveBayesClassifier.train(train_data)

        print(" - TESTING DATA - \n")
        print("Accuracy is:", classify.accuracy(classifier, test_data))

        print(classifier.show_most_informative_features(10))
        
        print("Saving classifier as 'model.pickle' ")
        save_classifier = open("model.pickle","wb")
        pickle.dump(classifier,save_classifier)
        save_classifier.close()

    while (True):
        custom_tweet = input("Please enter a sentence to analyse the sentiment predicted by the model.\nType 'end' to terminate script:\n")
        if custom_tweet.lower() == "end":
            break
        print(word_tokenize(custom_tweet))
        custom_tokens = remove_noise(word_tokenize(custom_tweet))
        prediction = classifier.classify(dict([token, True] for token in custom_tokens))
        print("Model predicts that the sentence is : " + prediction + "\n")