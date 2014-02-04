#!/usr/bin/python
#Documentation: http://code.google.com/apis/youtube/2.0/developers_guide_protocol.html
import urllib2
from urllib2 import Request, urlopen, URLError, HTTPError
from BeautifulSoup import BeautifulStoneSoup
from BeautifulSoup import BeautifulSoup
import threading
from geoLocationCities import geoLocationCities
from managerDB import managerDB

from datetime import datetime
import time
from time import mktime

#-------------------------------------------		
class youtubeRSS():
	def __init__(self,city):
		self.managerDB = managerDB()
		self.myGeoLocationCities = geoLocationCities()
		self.setCity(city)
		self.lastRhythm = 0
		self.minimHistoric = 10
		
	def setCity(self, city):
		self.city = city
		
	def getData(self, arg):
		try:
			self.url = "http://gdata.youtube.com/feeds/api/videos?location="+ self.myGeoLocationCities.getLatLon(self.city) +"&location-radius=50km&time=today&orderby=published&max-results=50" 	
			print self.url
			response = urllib2.urlopen(self.url)
			# prepare for a string in UTF-8
		except:
			print "Error youtube urllib2"
			self.managerDB.recordLogError('youtube', self.city, "internet")
			return
		try:	
			html = unicode(response.read(), "utf-8" )
			#print html
			soup = BeautifulSoup(html)	
			divs = soup.findAll("entry")
			totalVideos = 0
			print "totalVideos to check:"+str(len(divs))
			for d in divs:
				date = d.find("published").contents[0]
				struct_time = time.strptime(str(date)[:-5], "%Y-%m-%dT%H:%M:%S")
				
				# Videos from last 180 minuts ago
				if mktime(struct_time)-(60*60*2) > (int(time.time())-(60*60)):
					totalVideos = totalVideos +1
					#print struct_time	
					#print mktime(struct_time)-(60*60*2)	
					#print (int(time.time())-(60))
						
			print "totalVideos new last minute: "+str(totalVideos)
			self.managerDB.recordItem( 'youtube', self.city, totalVideos)  	
		except:
			print "ERROR"
			self.managerDB.recordLogError('youtube', self.city, "getData")
		self.calculateRythm_youtube()	
		# youtube: videos from today
		
	def calculateRythm_youtube(self):
		try:
			print "start calculation"
			dateLast24hTS_start = int(time.time())
			#dateLast24hTemp_start = datetime.fromtimestamp(dateLast24hTS_start ).strftime("%Y-%m-%d %H:%M:%S")
			dateLast24hTS_end = int(time.time())-( 60*60*24*30)
			#dateLast24hTemp_end = datetime.fromtimestamp(dateLast24hTS_end ).strftime("%Y-%m-%d %H:%M:%S")
			totalHistoric = self.getTotalValue(dateLast24hTS_end, dateLast24hTS_start)
			
			#if(totalHistoric<self.minimHistoric):
			#	print "Still not enought historic variables to normalize value, now is:"+str(totalHistoric)+"/"+str(self.minimHistoric)
			#	return
    
			# Get last date
			currentValue = self.getCurrentValue()
			print self.city+":currentValue youtube:"+ str(currentValue)
    
			maxValue = self.getMaxValue(dateLast24hTS_end,dateLast24hTS_start,currentValue)
			print self.city+":maxValue youtube:"+str(maxValue) 
            
			minValue = self.getMinValue(dateLast24hTS_end,dateLast24hTS_start,currentValue)
			print self.city+":minValue youtube:"+ str(minValue)
			
			if( minValue== 0 and maxValue==0):
				print "force to ZERO"
				currentRythm = 0;
			else:
				currentRythm = int(255.0*( (float(currentValue)-float(minValue)) / (float(maxValue)- float(minValue))))
				# Keep values on ranges
				currentRythm = self.safeCurrentRhythms(currentRythm)
				
			print self.city+":currentRythm youtube:"+str(currentRythm)
			
			# Store twitter of this city
			sql = "INSERT INTO youtube_rythm (city,count) VALUES('"+self.city+"',"+str(currentRythm)+")"
			print sql
			self.managerDB.insertRequestSQL(sql)
   
		except:
			print "ERROR calculating YOUTUBE: "+str(self.city)
			self.managerDB.recordLogError('youtube', str(self.city), "calculation")
			
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
			sql = "SELECT * FROM youtube WHERE city=\'"+self.city+"\'  and strftime('%s',date) >"+str(timeEnd)
			row = self.managerDB.selectRequestSQL(sql)
			return len(row)
		except:
			return 0
					
	def getCurrentValue(self):
		try:
			sql = "SELECT * FROM youtube WHERE city=\'"+self.city+"\' ORDER BY id DESC"
			row = self.managerDB.selectRequestSQL(sql)
			currentValue = row[2]
			return currentValue
		except:
			return 0
			
	def getMinValue(self, timeEnd, timeStart, current):
		try:
	 		sql = "SELECT MIN(count) FROM youtube WHERE city=\'"+self.city+"\' and strftime('%s',date) >"+str(timeEnd)
	 		print sql
	 		row = self.managerDB.selectRequestSQL(sql)
	 		minValue = row[0]
	 		return minValue
	 	except:
	 		return current
    
	def getMaxValue(self, timeEnd, timeStart, current):
	 	try:
	 		sql = "SELECT MAX(count) FROM youtube WHERE city=\'"+self.city+"\' and strftime('%s',date) >"+str(timeEnd)
	 		print sql
	 		row = self.managerDB.selectRequestSQL(sql)
	 		maxValue = row[0]
			return maxValue
	 	except:
	 		return current
	
	def closeDB(self):
		self.managerDB.closeDB()	

#-------------------------------------------
if __name__ == "__main__":
	youtubeRSS = youtubeRSS("sao+paulo")
	youtubeRSS.getData("")