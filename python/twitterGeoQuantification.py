#!/usr/bin/python

from urllib2 import Request, urlopen, URLError, HTTPError
from BeautifulSoup import BeautifulSoup
import time
from datetime import datetime
import threading
from managerDB import managerDB
from geoLocationCities import geoLocationCities
import twitter
import datetime
import calendar
from settings import settings
 
#-------------------------------------------		
class twitterGeoQuantification():
	def __init__(self, city):
		self.difference_gm_time =  3 * 3600 # depending server is place
		self.managerDB = managerDB()
		self.setCity(city)
		self.hourTwees = dict()
		self.lastId = ""
		self.currentMinute = 0
		self.newTweets = True
		self.numTweetsMinute = 0
		self.numTweetsHour = 0
		self.lastMinute = 0
		self.firstMesure = True
		# default values to minutes
		for i in range(0,60):
			self.hourTwees[i] = 0	
		self.lastRhythm = 0
		self.minimHistoric = 10
		self.settings = settings()
		self.api = twitter.Api(
			self.settings.twitter_consumer_key,
			self.settings.twitter_consumer_secret,
			self.settings.twitter_access_token_key,
			self.settings.twitter_access_token_secret
			)
	def setCity(self, city):
		geo = geoLocationCities()
		self.lat = float(geo.getLatLon(city).split(',')[0])
		self.lon = float(geo.getLatLon(city).split(',')[1])
		self.city = city
		
	def getData(self, args):			
		# Browser
		data = ""
		try:
			data = self.api.GetSearch(geocode=[self.lat,self.lon,'25.0mi'],count=100)
			#req = Request(self.url)
			#response = urlopen(req)
			#data = str(response.read())
		except HTTPError, e:
			print 'ERROR1:The server couldn\'t fulfill the request. Error code: ', e.code
		except URLError, e:
			print 'ERROR1:We failed to reach a server. Reason: ', e.reason
		except:
			print 'ERROR1:We failed to reach a server. Reason: general error'
		else:
			#print "Call Tweeter : %s" % time.ctime()
			self.parseData(data)
			
	def parseData(self,data):
		try:
			print "total tweets:"+str(len(data))
			extra = len(data)-100
			self.numTweetsMinute = 0
			if extra<0:
				extra = 0
			minuteNow = str(datetime.datetime.now())[14:16]
			secondNow = str(datetime.datetime.now())[11:13]
			currentTimestamp = time.time()
			lastTimestampProcess = currentTimestamp
			currentTimestamp = currentTimestamp - self.difference_gm_time
			
			for d in data[extra:len(data)]:
				datetimestring = str(d.GetCreatedAt())
				timestamp = time.mktime(time.strptime(datetimestring, '%a %b %d %H:%M:%S +0000 %Y'))
				minute = datetimestring[14:16]
				second = datetimestring[11:13]
				#print minute+":"+second
				#print minuteNow+":"+secondNow
				#if( minute==minuteNow or (str(int(minute)-1)==minuteNow) )
				
				if (currentTimestamp-timestamp)<60:
					self.numTweetsMinute +=1
					lastTimestampProcess = timestamp
				#print "created_at:"+str(encoded_data['created_at'])
			if	self.numTweetsMinute>=99:
				self.numTweetsMinute = 100/(float(currentTimestamp-lastTimestampProcess)/60)
			if	self.numTweetsMinute<0:
				self.numTweetsMinute=0
			print "numTweetsMinute:"+str(self.numTweetsMinute)
			self.managerDB.recordItem( 'twitter', self.city, self.numTweetsMinute) 
			self.calculateRythm_twitter()
		except:
			self.managerDB.recordLogError('twitter', str(self.city), "parse")
			print "ERROR2: parsing data: "+ str(self.city)
		
	def close(self):
		print "twitter-close"	
	
	def closeDB(self):
		self.managerDB.closeDB()
		# twitter: have every minute number messages 	
		
	def calculateRythm_twitter(self):
		try:
			
			currentRythm = 0
			print "start calculation"
			dateLast24hTS_start = int(time.time())
			#dateLast24hTemp_start = datetime.fromtimestamp(dateLast24hTS_start ).strftime("%Y-%m-%d %H:%M:%S")
			dateLast24hTS_end = int(time.time())-( 60*60*24*30)
			#dateLast24hTemp_end = datetime.fromtimestamp(dateLast24hTS_end ).strftime("%Y-%m-%d %H:%M:%S")
			
			# Get last date
			currentValue = self.getCurrentValue()
			print self.city+":currentValue twitter:"+ str(currentValue)
			
			maxValue = self.getMaxValue(dateLast24hTS_end,dateLast24hTS_start,currentValue)
			print self.city+":maxValue twitter:"+str(maxValue) 
			
			minValue = self.getMinValue(dateLast24hTS_end,dateLast24hTS_start,currentValue)
			print self.city+":minValue twitter:"+ str(minValue)
			if( minValue== 0 and maxValue==0):
				print "force to ZERO"
				currentRythm = 0
			else:	
				currentRythm = int( 255.0*( (float(currentValue)-float(minValue)) / (float(maxValue)- float(minValue))  ) )
				# Keep values on range
				currentRythm = self.safeCurrentRhythms(currentRythm)
			
			print "currentRythm:"+str(currentRythm)
			# Store twitter of this city
			sql = "INSERT INTO twitter_rythm (city,count) VALUES('"+self.city+"',"+str(currentRythm)+")"
			print sql
			self.managerDB.insertRequestSQL(sql)
		except:
			print "ERROR TWITTER calculating: "+str(self.city)
			self.managerDB.recordLogError('twitter', str(self.city), "calculation")
			
	def safeCurrentRhythms(self, currentRythm):
		if currentRythm>255:
			currentRythm = 255
		if currentRythm<0:
			currentRythm = 0
		# Avoid jumps to stop
		if currentRythm==0:
			if self.lastRhythm !=0:
				currentRythm = self.lastRhythm
			self.lastRhythm = 0
		else:
			self.lastRhythm = currentRythm	
		return currentRythm
		
	def getTotalValue(self,timeEnd, timeStart):
		try:
			sql = "SELECT * FROM twitter WHERE city=\'"+self.city+"\'  and strftime('%s',date) >"+str(timeEnd)+" and strftime('%s',date) <"+str(timeStart)
			row = self.managerDB.selectRequestSQL(sql)
			return len(row)
		except:
			return 0
	
	def getCurrentValue(self):
		try:
			sql = "SELECT * FROM twitter WHERE city=\'"+self.city+"\' ORDER BY id DESC"
			row = self.managerDB.selectRequestSQL(sql)
			currentValue = row[2]
			return currentValue
		except:
			return 0
	
	def getMinValue(self, timeEnd, timeStart, current):
		try:
	 		sql = "SELECT MIN(count) FROM twitter WHERE city='"+self.city+"' and strftime('%s',date) >"+str(timeEnd)
	 		print sql
	 		row = self.managerDB.selectRequestSQL(sql)
	 		minValue = row[0]
	 		return minValue
	 	except:
	 		return current
	
	def getMaxValue(self, timeEnd, timeStart, current):
	 	try:
	 		sql = "SELECT MAX(count) FROM twitter WHERE city='"+self.city+"' and strftime('%s',date) >"+str(timeEnd)
	 		print sql
	 		row = self.managerDB.selectRequestSQL(sql)
	 		maxValue = row[0]
			return maxValue
	 	except:
	 		return current
	
#-------------------------------------------
if __name__ == "__main__":
	myTweets = twitterGeoQuantification("sao+paulo")
	myTweets.getData("")