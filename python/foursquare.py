#!/usr/bin/env python
# documentation API: https://developer.foursquare.com/docs/venues/trending
from time import sleep
import time
from geoLocationCities import geoLocationCities
from managerDB import managerDB
import requests
from settings import settings

class foursquare():
	def __init__(self,city):
		self.city = city
		self.settings = settings()
		myGeoLocationCities = geoLocationCities()
		self.url = "https://api.foursquare.com/v2/venues/trending?ll="+ myGeoLocationCities.getLatLon(self.city) +"&limit=50&radius=2000&oauth_token="+self.settings.foursquare_oauth_token
		self.managerDB = managerDB() 
	
	def getData(self, arg):
		try:
			print self.url
			response = requests.get(self.url)
			print response.json
			# prepare for a string in UTF-8
		except:
			print "Error RSS urllib2"
			self.managerDB.recordLogError('foursquare', self.city, "internet")
			return
		try:	
			html = unicode(response.read(), "utf-8" )
		except:
			pass

if __name__ == "__main__":
	foursquare = foursquare("sao+paulo")
	foursquare.getData("")