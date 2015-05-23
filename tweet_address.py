#!/usr/bin/env python
# encoding: utf-8

import re
import sys
import string
import pandas as pd


### This script is designed specifically for "Scan BC" tweets, 
### it searches tweets for anything that looks like an address
### and extracts it to be used in a map. 

# Load CSV of tweets from tweet_scrapper.py as Pandas DataFrame
df = pd.read_csv('C:/Users/user/Documents/ScanBC_tweets.csv')
tweets = list(df.text)

streets  = ['Street', 'Road', 'Avenue', 'Drive','&amp;']
sts = ['St', 'Rd', 'Ave', 'Dr', 'and']
place_names = ["Cambie Bridge","Granville Street Bridge","Stanley Park","Lost Lagoon","Jericho Beach", "Kitsilano Beach","Olympic Village","Oppenheimer Park","Spanish Banks","Richmond Centre","Steveston","Pacific Spirit","Grouse Mountain","Buntzen Lake", "Tamanawis Park", "yvrairport", "Lighthouse Park","English Bay Beach", "Oakridge Mall", "Canada Place", "Convention Centre", "Pacific Centre", "Waterfront Station", "GM Place", "Lions Gate Bridge", "Burrard Bridge", "Yaletown", "Gastown", "Downtown", "Golden Ears", "Arthur Laing", "Port Mann", "Alex Frasier"]

### This is the first of several functions that try to find 
### addresses in tweets. As addresses can be formatted in a
### number of different ways, there are several functions to
### look for different formatting. 

### look to see if street types are used and build an address

def address_finder(tweet):
	for n in range(len(streets)):
		tweet = tweet.replace(streets[n], sts[n])
	punc_regex = re.compile('[%s]' % re.escape(string.punctuation))
	tweet = punc_regex.sub('', tweet)

	words = tweet.split()
	
	end_index = None
	start_index = None

	for i in range(len(words)): # Probably should just be for i in words, but I found the index # useful
		if  words[i]  in sts[:3]:
			end_index = i
	if end_index and re.search(r"[A-Z0-9][a-z]+", words[end_index-1]) and re.search(r"[A-Z0-9][a-z]+", words[end_index-2]) and re.search(r"[0-9]+", words[end_index-3]):
			start_index = end_index-3
	elif end_index and re.search(r"[A-Z0-9][a-z]+", words[end_index-1]) and re.search(r"[A-Z]+", words[end_index-2]) and re.search(r"[0-9]+", words[end_index-3]):
			start_index = end_index-3
	elif end_index and re.search(r"[A-Z0-9][a-z]+", words[end_index-1]) and re.search(r"[0-9]+", words[end_index-2]):
			start_index = end_index-2
	elif end_index and re.search(r"[A-Z0-9][a-z]+", words[end_index-1]):
			start_index = end_index-1
	  

	if end_index and start_index:
		address = ' '.join(words[start_index:end_index+1])
		return address

	else: 
		return None

### Look to see if there is an "and" in the tweet and look forward and back if it meets
### the criteria of an address (Capitalization or numbered words on either end)

def intersection_finder(tweet):
	
	def intersection_guts(tweet, and_index):
		
		address = None
		end_index = None
		start_index = None

		if words[and_index-1] in sts and re.search(r"[A-Z0-9][a-z0-9]+", words[and_index-2]) and re.search(r"[A-Z0-9][a-z0-9]+", words[and_index-3]):
			start_index = and_index-3
		elif words[and_index-1] in sts and re.search(r"[A-Z0-9][a-z0-9]+", words[and_index-2]) and re.search(r"[A-Z]", words[and_index-3]):
			start_index = and_index-3
		elif words[and_index-1] in sts and re.search(r"[A-Z0-9][a-z0-9]+", words[and_index-2]):
			start_index = and_index-2
		elif re.search(r"[A-Z0-9][a-z0-9]+", words[and_index-1]) and re.search(r"[A-Z0-9][a-z0-9]+", words[and_index-2]):
			start_index = and_index-2
		elif re.search(r"[A-Z0-9][a-z0-9]+", words[and_index-1]): 
			start_index = and_index-1
		elif re.search(r"[A-Z][a-z]+", words[and_index-1]): 
			start_index = and_index-1
		elif re.search(r"[0-9]+", words[and_index-1]): 
			start_index = and_index-1
		
		if start_index and and_index+3 < len(words):
			if words[and_index+3] in sts:
				end_index = and_index+3
			if words[and_index+2] in sts:
				end_index = and_index+2
			elif re.search(r"[A-Z0-9][a-z0-9]+", words[and_index+1]) and re.search(r"[A-Z0-9][a-z0-9]+", words[and_index+2]):
				end_index = and_index+2
			elif re.search(r"[A-Z0-9][a-z0-9]*", words[and_index+1]):
				end_index = and_index+1
		elif start_index and and_index+2 < len(words):
			if words[and_index+2] in sts:
				end_index = and_index+2
			elif re.search(r"[A-Z0-9][a-z0-9]+", words[and_index+1]) and re.search(r"[A-Z0-9][a-z0-9]+", words[and_index+2]):
				end_index = and_index+2
			elif re.search(r"[A-Z0-9][a-z0-9]*", words[and_index+1]):
				end_index = and_index+1
		else:
			if re.search(r"[A-Z0-9][a-z0-9]*", words[and_index+1]):
				end_index = and_index+1

		if start_index and end_index:
			address = ' '.join(words[start_index:end_index+1])

		return address

	for n in range(len(streets)):
	    tweet = tweet.replace(streets[n], sts[n])
	
	tweet = tweet.replace("near", "and")
	tweet = tweet.replace(".", " p ")

	punc_regex = re.compile('[%s]' % re.escape(string.punctuation))
	tweet = punc_regex.sub('', tweet)

	and_index = None
	address = None

	words = tweet.split()

	if 'and' in words:
		for i in range(len(words)):
			if words[i] == 'and' and address == None:
				and_index = i
				address = intersection_guts(tweet, and_index)
				if address: 
					return address
		else: 
			return None


### Addresses can be very informal, so this is one last ditch effor to extract anything
### address-like

def address_no_street(tweet):
	punc_regex = re.compile('[%s]' % re.escape(string.punctuation))
	tweet = punc_regex.sub('', tweet)
	words = tweet.split()
	address = None

	for i in range(len(words[:-2])):
		if re.search(r"[0-9]+", words[i]) and re.search(r"[A-Z0-9][a-z0-9]+", words[i+1]) and re.search(r"[A-Z0-9][a-z0-9]+", words[i+2]):
			address = ' '.join(words[i:i+2])
		elif re.search(r"[0-9]+", words[i]) and re.search(r"[A-Z0-9][a-z0-9]+", words[i+1]):
			address = ' '.join(words[i:i+1])
	if address:
		return address
	else:
		return None

### If a common place-name is called instead of an address, this function
### looks to see if it is in a pre-defined list of places in BC

def place_finder(tweet):
	punc_regex = re.compile('[%s]' % re.escape(string.punctuation))
	tweet = punc_regex.sub('', tweet)

	address = None

	for i in range(len(place_names)):
		if  place_names[i] in tweet:
			address = place_names[i]
	
	return address

### Returns the city based on the use of hashtags #City

def city_finder(tweet):
	words = tweet.split()
	city = None
	city_instance = re.search(r'#\w*', tweet)
	if city_instance:
		city = city_instance.group(0)
		return city[1:]


### Puts all of the helper functions together. 

def address(tweet):
	city = None
	address = None
	city = city_finder(tweet)
	address = intersection_finder(tweet)
	if address and city: 
		return address + ", " + city + ", British Columbia, Canada"
	elif address:
		return address + ", British Columbia, Canada"
	else:
		address = address_finder(tweet)
	
	if address and city: 
		return address + ", " + city + ", British Columbia, Canada"
	elif address:
		return address + ", British Columbia, Canada"
	else:
		address = address_no_street(tweet)
	if address and city: 
		return address + ", " + city + ", British Columbia, Canada"
	elif address:
		return address + ", British Columbia, Canada"
	else:
		address = place_finder(tweet)
	if address and city: 
		return address + ", " + city + ", British Columbia, Canada"
	elif address:
		return address + ", British Columbia, Canada"
	else: 
		return None

addresses = []
city = []
latlong = []

for n in range(len(tweets)):
 	addresses.append(address(tweets[n]))

for n in range(len(tweets)):
 	city.append(city_finder(tweets[n]))

df['address'] = addresses
df['city'] = city

df = df.dropna()


df.to_csv("ScanBC_tweets_w_address.csv") #Saves addresses
