#!/usr/bin/python

from urllib2 import Request, urlopen, URLError, HTTPError
from BeautifulSoup import BeautifulSoup
import time
from datetime import datetime
import threading
from managerDB import managerDB
from geoLocationCities import geoLocationCities

#-------------------------------------------		
class twitterGeoQuantification():
	def __init__(self,city):
		self.managerDB = managerDB()
		geo = geoLocationCities()
		#+near:"+city+"
		self.url = "http://search.twitter.com/search.atom?geocode="+geo.getLatLon(city)+",25.0mi&q=+within:25mi&rpp=100" 
		print self.url
		self.hourTwees = dict()
		self.lastId = ""
		self.currentMinute = 0
		self.newTweets = True
		self.numTweetsMinute = 0
		self.numTweetsHour = 0
		self.lastMinute = 0
		self.city = city
		self.firstMesure = True
		# default values to minutes
		for i in range(0,60):
			self.hourTwees[i] = 0	
		self.lastRhythm = 0
		self.minimHistoric = 10
		
	def getData(self, args):			
		# Browser
		data = ""
		try:
			req = Request(self.url)
			response = urlopen(req)
			data = str(response.read())
		except HTTPError, e:
			print 'ERROR1:The server couldn\'t fulfill the request. Error code: ', e.code
		except URLError, e:
			print 'ERROR1:We failed to reach a server. Reason: ', e.reason
		except:
			print 'ERROR1:We failed to reach a server. Reason: general error'
		else:
			#print "Call Tweeter : %s" % time.ctime()
			self.parseData(data)
			
	def parseData(self,xml):
		try:
		    soup = BeautifulSoup(xml)
		    self.newTweets = True
		    idTempLast = ""
		    #print "lastId:"+ self.lastId
		    allTweets = soup.findAll('entry')
		    totalNewTweets = 0
		    
		    # tweet array (from newest to oldest tweet)
		    for tweets in allTweets:
		    	id = str(tweets.findAll("id")[0].contents)
		    	if self.lastId == id:
		    		#print "There is no any new tweets!!"
		    		break
		    	else:
		    		totalNewTweets+=1
		    	
		    # store last id to avoid duplications 
		    self.lastId = str(allTweets[0].findAll("id")[0].contents)
		    	
		    allTweets.reverse()
		    
		    # parse all last tweets (from old to newest)
		    for i in range(len(allTweets)-totalNewTweets,len(allTweets)-1):
		    	time = str(allTweets[i].findAll("updated")[0].contents)[14:22]
		    	minute = int( str(allTweets[i].findAll("updated")[0].contents)[17:19] )
		    	id = str(allTweets[i].findAll("id")[0].contents)
		    	idTempLast = id
		    	#print time
		    	#print minute
		    	self.eachTweet(id,minute)
		    	#print "new tweet "+time+" - "+id+" m:"+str(minute)
		except:
			self.managerDB.recordLogError('twitter', str(self.city), "parse")
			print "ERROR2: parsing data: "+ str(self.city)
		
	
	def eachTweet(self,id,minute):
		if self.currentMinute !=minute:
			#print "Clean minutes from hour before!! c:" + str(self.currentMinute)+" d:"+ str(minute)
			self.hourTwees[minute] = 0
			self.lastMinute = self.currentMinute
			self.currentMinute = minute
			# calculate tweets frequency each minute
			self.calculateTweetFrequency()
		self.hourTwees[minute] += 1
	
	def calculateTweetFrequency(self):
		self.numTweetsMinute = self.hourTwees[self.lastMinute]
		if self.firstMesure==False:
			print "--------"
			print "numTweetsMinute:"+str(self.numTweetsMinute)
			self.managerDB.recordItem( 'twitter', self.city, self.numTweetsMinute) 
			self.calculateRythm_twitter()
		self.firstMesure = False
		
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
	myTweeterRSS = twitterRSS("sao+paulo")
	count = 0
	while count<10:
		myTweeterRSS.getData("")
		time.sleep(10)
		count += 1 