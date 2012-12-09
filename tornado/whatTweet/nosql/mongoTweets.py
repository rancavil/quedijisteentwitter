import pymongo
import bson.objectid

class TweetDBMongoDB:
	def __init__(self, host='localhost', port=27017):
		self._conn = pymongo.Connection(host,port)

	def getTweets(self,query):
		tweetsdb = self._conn.tweetsdb
		tweets   = tweetsdb.tweets
		tws   = []
		ts = tweets.find(query).sort(('created_at'))
		for t in ts:
			tws.append(t)
		return tws

	def insertTweet(self,json_tweet):
		tweetsdb  = self._conn.tweetsdb
		tweets    = tweetsdb.tweets
		id_object = tweets.insert(json_tweet, safe=True)

		return id_object

	def deleteTweets(self,query):
		tweetsdb  = self._conn.tweetsdb
		tweetsdb.tweets.remove(query,safe=True)

	def close(self):
		self._conn.close()