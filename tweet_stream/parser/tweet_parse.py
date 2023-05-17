#! /usr/bin/python

import json
import pygmaps
from pprint import pprint
import re
import nltk
import classify

#TODO ensure that json file is valid

def extract_features(document):
	document_words = set(document)
	return {
		f'contains({word})': (word in document_words) for word in word_features
	}

########## GATHER TWEET DATA #########################################
with open('../json/twituni.json') as json_data:
	tweets = []

	for line in json_data:
		try: 
			tweets.append(json.loads(line))
		except:
			pass

########## PREPROCESS TWEET DATA #####################################
comments = []
for tweet in tweets:
	try:
		proc_tweet = tweet['text']
		#Convert to lower case
		proc_tweet = proc_tweet.lower()
  	#Convert www.* or https?://* to URL
		proc_tweet = re.sub('((www\.[\s]+)|(https?://[^\s]+))','URL',proc_tweet)
  	#Convert @username to AT_USER
		proc_tweet = re.sub('@[^\s]+','AT_USER',proc_tweet)
  	#Remove additional white spaces
		proc_tweet = re.sub('[\s]+', ' ', proc_tweet)
  	#Replace #word with word
		proc_tweet = re.sub(r'#([^\s]+)', r'\1', proc_tweet)
  	#trim
		proc_tweet = proc_tweet.strip('\'"')
		comments.append(proc_tweet)
	except:
		pass

with open('../sentiment_data/rt-polaritydata/rt-polarity.pos') as posfile:
	pos_tweets = []
	for line in posfile:
		try:
			pos_tweets.append((line, 'positive'))
		except ValueError:
			pass

with open('../sentiment_data/rt-polaritydata/rt-polarity.neg') as negfile:
	neg_tweets = []
	for line in negfile:	
		try:
			neg_tweets.append((line, 'negative'))
		except ValueError:
			pass

train_tweets = []
for (words, sentiment) in pos_tweets + neg_tweets:
	words_filtered = [e.lower() for e in words.split() if len(e) >= 3]
	train_tweets.append((words_filtered, sentiment))

########## TRAIN CLASSIFIER #########################################
word_features = classify.get_word_features(classify.get_words_in_tweets(train_tweets))
training_set = nltk.classify.apply_features(extract_features, train_tweets)
classifier = nltk.NaiveBayesClassifier.train(training_set)

########## RUN CLASSIFIER ON DATA #########################################
#coordinates are the center of the map, zoom level 0~20
mymap = pygmaps.maps(35.689, 139.706, 16)

for comment in comments:
	print(
		f"comment: {comment}, class: {classifier.classify(extract_features(comment.split()))}"
	)
	#print("comment: " + comment)

'''
count = 0
for comment in comments:
	key = 'coordinates'
	if key in tweet.keys():
		if tweet[key] is not None:
			if tweet[key][key] is not None:
				x = tweet[key][key][0]
				y = tweet[key][key][1]
				print ("x was: " + str(x) + ", y was: " + str(y))
				mymap.addpoint(y, x, "#0000FF")
				count = count + 1
'''

mymap.draw('./mymap.html')
