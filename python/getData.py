#!/usr/bin/env python
'''
Notes:
because change winter time I add in youtube a - 2 hours in line 31
if mktime(struct_time)-(60*60*2) > (int(time.time())-(60*60)):
'''
from time import time, sleep
import threading, time  
from twitterGeoQuantification import twitterGeoQuantification
from clientOSC import clientOSC
from flickr import flickr
from youtube import youtubeRSS
from managerDB import managerDB
import signal
from settings import settings

class dataRhythmSaoPaulo():
	def __init__(self):
		self.managerDB = managerDB()
		self.cOSC = clientOSC()
		self.f = flickr("adelaide")
		self.y = youtubeRSS("adelaide")
		self.t = twitterGeoQuantification("adelaide")
		self.currentRhythm = 100
		self.loopRun = True
		self.settings = settings()
		self.idAr = -1
	def loop(self):
		lastUpdateTimstamp	= 0
		while self.loopRun:
			if time.time()-lastUpdateTimstamp>60 :
				lastUpdateTimstamp	= int(time.time())
				self.idAr +=1
				if self.idAr==len(self.settings.cityAr):
					self.idAr = 0
				self.f.setCity(self.settings.cityAr[self.idAr])
				self.y.setCity(self.settings.cityAr[self.idAr])
				self.t.setCity(self.settings.cityAr[self.idAr])
				# get data from services FLICKR and Youtube
				self.f.getData("")
				self.y.getData("")
				self.t.getData("")
				self.rhythmCalculation(self.settings.cityAr[self.idAr]) 
				print "currentRhythm - "+self.settings.cityAr[self.idAr]+"======>"+str(self.currentRhythm)
				self.cOSC.sendOSC(self.currentRhythm,self.settings.cityAr[self.idAr].replace("+"," "))
				myFile = open('current_data.txt', 'w')
				myFile.write(str(self.currentRhythm)+','+self.settings.cityAr[self.idAr].replace("+"," "))
				myFile.close()
			time.sleep(10)
			
	def quit(self):	
		self.loopRun = False
		sys.exit(0)
		
	def rhythmCalculation(self, city):
		try:
			sql = "SELECT count FROM flickr_rythm WHERE city=\'"+city+"\' ORDER BY id DESC"
			print sql
			row = self.managerDB.selectRequestSQL(sql)
			print "-------"
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
			print "rhythm:"+str(finalRythm)
			if finalRythm>255:
				finalRythm = 255
			if finalRythm<0:
				finalRythm = 0
			self.currentRhythm = finalRythm
		except:
			print "Error calculating final Rhythm"
		
if __name__ == '__main__': 
	
	r = dataRhythmSaoPaulo()
	signal.signal(signal.SIGINT, r.quit)
	r.loop()













