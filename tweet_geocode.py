
import pandas as pd
import geocoder
import logging
import time
import csv

### Important: get your own damn keys
bing_key = ''
bing_url = ''

df = pd.read_csv('C:/Users/user/Documents/ScanBC_tweets_w_address.csv')

address = df.address
text = df.text

address2 = address[0:2]
text2 = text[0:2]

address1000 = address[0:1000]
text1000 = text[0:1000]
time = df.created_at[0:1000]

results = []
lat = []
lon = []
pcode = []
coord = []
attempts = 0

for addr in address1000:	
	g = geocoder.bing(addr, key = bing_key, url = bing_url)
	attempts += 1
	time.sleep(1) #Probably should report g.ok here 

	results.append(g)
	lat.append(g.lat)
	lon.append(g.lng)
	pcode.append(g.postal)
	coord.append(",".join([str(g.lat), str(g.lng)]))
	print attempts


df_1000 = pd.DataFrame()
df_1000["address"] = address1000
df_1000["text"] = text1000
df_1000["lat"] = lat
df_1000["lon"] = lon
df_1000["pcode"] = pcode
df_1000["coord"] = coord
df_1000["results"] = results
df_1000["time"] = time


df_1000.to_csv("ScanBC_tweets_w_coords1000.csv")

