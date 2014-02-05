#!/usr/bin/env python
# documentation API: https://developer.foursquare.com/docs/venues/trending
from time import sleep
import time
from geoLocationCities import geoLocationCities

class foursquare():
	def __init__(self):
		myGeoLocationCities = geoLocationCities()
		self.url = "https://api.foursquare.com/v2/venues/trending?ll="+ myGeoLocationCities.getLatLon(city) +"&limit=50&radius=2000&oauth_token=PD1TXEZIYLL1BJ01W1XMAVOC4301UZPME155XPT31THGLCCI&v=20121207"
	
	def getData(self, arg):
		try:
			print self.url
			response = urllib2.urlopen(self.url)
			# prepare for a string in UTF-8
		except:
			print "Error RSS urllib2"
			self.managerDB.recordLogError('youtube', self.city, "internet")
			return
		try:	
			html = unicode(response.read(), "utf-8" )

if __name__ == "__main__":
	foursquare = foursquare("sao+paulo")
	foursquare.getData("")