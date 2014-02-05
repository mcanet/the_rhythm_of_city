import flickrapi
from time import sleep
import time
from datetime import datetime
from managerDB import managerDB

'''
Documentation 
+Code: http://spanring.eu/blog/2010/02/25/python-flickr-api-geo-search-example/
+Found new place-id:search in normal search with city name and then at right side list places with this name
'''

class flickr:
	def __init__(self, city):
		self.urlPath = "http://www.flickr.com/map?place_id="
		self.city = city
		self.flickrPlaces = dict()
		self.flickrPlaces["istambul"] 		= "6NGXevKbAphp2QAz"
		self.flickrPlaces["london"] 		= ".2P4je.dBZgMyQ"
		self.flickrPlaces["new+york"] 		= "hVUWVhqbBZlZSrZU"
		self.flickrPlaces["tokio"] 			= "V5QAdQebApgw_9XH"
		self.flickrPlaces["barcelona"] 		= "2HQ7FIeeBJ_vRb8"
		self.flickrPlaces["paris"] 			= "bV4EOqafAJnqoz4"
		self.flickrPlaces["berlin"] 		= "sRdiycKfApRGrrU"
		self.flickrPlaces["mexicodf"] 		= "MuLDKdiYAJo.QrA"
		self.flickrPlaces["rome"] 			= "xbTF9RCeA51vjuk"
		self.flickrPlaces["praha"] 			= "UEddssmbAZwXVqZt7g"
		self.flickrPlaces["moscou"] 		= "ZLXvFuGbAJ6JI5bc"
		self.flickrPlaces["san+francisco"] 	= "kH8dLOubBZRvX_YZ"
		self.flickrPlaces["new+delhi"] 		= "7gGxOnGbApgQ3.2i2g"
		self.flickrPlaces["vienna"] 		= "wL4AEK2cBJ0UQdc"
		self.flickrPlaces["rosario"] 		= "vzJ2RFBSUbveaB0"
		self.flickrPlaces["buenos+aires"] 	= "SG5jj75SUbqEFrc"
		self.flickrPlaces["sau+paulo"] 		= "ou6W9HJTUL1op5q6RA"
		#http://www.flickr.com/places/info/466862
		
		self.flickrPlacesSel = 	self.flickrPlaces[city]
		self.managerDB = managerDB()
		# flickr API
		self.api_key = "aea45f1f97c70a68b3e56beb2601d29e"
		self.api_secret = "68751d7ac51f388e" 
		self.flickr = flickrapi.FlickrAPI(self.api_key, self.api_secret)
		self.lastRhythm = 0
		self.minimHistoric = 10
		
	def getData(self, arg):
		totalPictures = 0
		try:
			photos = self.flickr.photos_search(place_id=self.flickrPlacesSel, radius='15')
			
			totalPictures = photos[0].attrib["total"]
			print "total pictures:"+str(totalPictures)
			self.managerDB.recordItem( 'flickr', self.city, totalPictures)   
		except:
			print self.city +"_ ERROR1: Flickr INTERNET"
			self.managerDB.recordLogError( 'flickr', self.city, "internet")
		else:
			# data from last hour
			dateLast1hTS = int(time.time())-( 60*30 )
			dateLast1hTemp = datetime.fromtimestamp(dateLast1hTS ).strftime("%Y-%m-%d %H:%M:%S")
			
			sql = "SELECT count FROM flickr WHERE city='"+self.city+"' and date <'"+str(dateLast1hTemp)+"'"
			print sql
			row = self.managerDB.selectRequestSQL(sql)
			try:
				yesterdayValue = int(row[0])
				# data from last flickr
				totalNewPictures = (int(totalPictures)-int(yesterdayValue))
				if totalNewPictures<0:
					totalNewPictures=0
				self.managerDB.recordItem( 'flickr_clean', self.city, totalNewPictures )
				self.calculateRythm_flickr()
			except:
				print self.city+":ERROR2 calculating FLICKR: "+str(self.city)
				
				
	# flickr: total photos from one city
	def calculateRythm_flickr(self):
		try:
			# last 24 hours
			dateLast24hTS_start = int(time.time())
			dateLast24hTemp_start = datetime.fromtimestamp( dateLast24hTS_start ).strftime("%Y-%m-%d %H:%M:%S")
			print dateLast24hTemp_start
			dateLast24hTS_end = int(time.time())-( 60*60*24 )
			dateLast24hTemp_end = datetime.fromtimestamp(dateLast24hTS_end ).strftime("%Y-%m-%d %H:%M:%S")
			
			# Current
			currentValue = self.getCurrentValue()
			print self.city+":currentValue flickr:"+ str(currentValue)
			
			maxValue = self.getMaxValue(dateLast24hTemp_start, dateLast24hTemp_end, currentValue)
			print self.city+":maxValue flickr:"+ str(maxValue)
			
			minValue = self.getMinValue(dateLast24hTemp_start, dateLast24hTemp_end, currentValue)
			print self.city+":minValue flickr:"+ str(minValue)
			if( minValue== 0 and maxValue==0):
				print "force to ZERO"
				currentRythm = 0
			else:
				currentRythm = int( 255.0 *(  (float(currentValue) - float(minValue))  /  (float(maxValue)- float(minValue)) ) )
				print "currentRythm:"+str(currentRythm)
				currentRythm = self.safeCurrentRhythms(currentRythm)
			
			# Store twitter of this city
			sql = "INSERT INTO flickr_rythm (city,count) VALUES(\'"+self.city+"\',"+str(currentRythm)+")"
			print sql
			self.managerDB.insertRequestSQL(sql)
		except:
			print self.city+":ERROR3 calculating FLICKR: "+str(self.city)
			
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
			sql = "SELECT * FROM flickr_clean WHERE city=\'"+self.city+"\'  and date >\'"+str(timeEnd)+"\'"
			row = self.managerDB.selectRequestSQL(sql)
			return len(row)
		except:
			return 0
			
	def getMinValue(self, timeStart,timeEnd, current):
		try:
			sql = "SELECT MIN(count) FROM flickr_clean WHERE city=\'"+self.city+"\' and date >\'"+str(timeEnd)+"\'"
			print sql
			row = self.managerDB.selectRequestSQL(sql)
			minValue = row[0]
			return minValue
		except:
			return current
			
	def getCurrentValue(self):
		try:
			sql = "SELECT * FROM flickr_clean WHERE city=\'"+self.city+"\' ORDER BY id DESC"
			row = self.managerDB.selectRequestSQL(sql)
			currentValue = row[2]
			return currentValue
		except:
			return 0
    
	def getMaxValue(self, timeStart,timeEnd,current):
		try:
			sql = "SELECT MAX(count) FROM flickr_clean WHERE city=\'"+self.city+"\' and date >\'"+str(timeEnd)+"\'"
			print sql
			row = self.managerDB.selectRequestSQL(sql)
			maxValue = row[0]
			return maxValue
		except:
			return current
			
#-------------------------------------------
if __name__ == "__main__":
	flickrAPI = flickr("sau+paulo")
	flickrAPI.getData("")


