#!/usr/bin/env python
'''
Notes:
because change winter time I add in youtube a - 2 hours in line 31
if mktime(struct_time)-(60*60*2) > (int(time.time())-(60*60)):
'''
import time  
import threading, time  
from twitterGeoQuantification import twitterGeoQuantification
from clientOSC import clientOSC
from flickr import flickr
from youtube import youtubeRSS
from managerDB import managerDB

class twitterThread(threading.Thread):  
      def __init__(self):  
          threading.Thread.__init__(self)
          self.myTweeterGeo = twitterGeoQuantification("sao+paulo")
      def run(self):
      	while 1:
      		self.myTweeterGeo.getData("")
      		time.sleep(2)

class dataRhythmSaoPaulo():
	def __init__(self):
		self.managerDB = managerDB()
		self.cOSC = clientOSC()
		t1 = twitterThread()  
		t1.start()  
		lastUpdateTimstamp	= 0
		f = flickr("sau+paulo")
		y = youtubeRSS("sao+paulo")
		self.currentRhythm = 100
		while 1:
			if int(time.time())-lastUpdateTimstamp>60 :
				lastUpdateTimstamp	= int(time.time())
				self.rhythmCalculation("sao+paulo") 
				print "currentRhythm ======>"+str(self.currentRhythm)
				self.cOSC.sendOSC(self.currentRhythm)
				# get data from services FLICKR and Youtube
				f.getData("")
				y.getData("")
			time.sleep(10)
		
	def rhythmCalculation(self, city):
		try:
			sql = "SELECT count FROM flickr_rythm WHERE city=\'"+city+"\' ORDER BY id DESC"
			print sql
			row = self.managerDB.selectRequestSQL(sql)
			flickr = int(row[0])
				
			sql = "SELECT count FROM twitter_rythm WHERE city=\'"+city+"\' ORDER BY id DESC"
			print sql
			row = self.managerDB.selectRequestSQL(sql)
			twitter = int(row[0])
				
			sql = "SELECT count FROM youtube_rythm WHERE city=\'"+city+"\'  ORDER BY id DESC"
			print sql
			row = self.managerDB.selectRequestSQL(sql)
			youtube = int(row[0])
			finalRythm =0
			finalRythm = int( float(youtube)*0.35 + float(twitter)*0.45 + float(flickr)*0.25 )
			print "rythm:"+str(finalRythm)
			if finalRythm>255:
				finalRythm = 255
			if finalRythm<0:
				finalRythm = 0
			self.currentRhythm = finalRythm
		except:
			print "Error calculating final Rhythm"
		
    
if __name__ == '__main__': 
	dataRhythmSaoPaulo()














