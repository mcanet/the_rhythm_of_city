from serialManager import serialManager
from managerDB import managerDB

class rythmManager():
	def __init__(self):
		self.serial = serialManager()
		self.managerDB = managerDB() 
		
	def sendStopToMetronome(self):
		rhythmSerialList = [0,0,0,0,0,0,0,0,0,0]
		self.serial.write(rhythmSerialList)
				
	def sendDataToMetronome(self, cities):
		try:
			finalRythmStr = ""
			rhythmSerialList = list()
			for i in range(0, 10):
				sql = "SELECT count FROM flickr_rythm WHERE city=\'"+cities[i]+"\' ORDER BY id DESC"
				print sql
				row = self.managerDB.selectRequestSQL(sql)
				flickr = int(row[0])
				
				sql = "SELECT count FROM twitter_rythm WHERE city=\'"+cities[i]+"\' ORDER BY id DESC"
				print sql
				row = self.managerDB.selectRequestSQL(sql)
				twitter = int(row[0])
				
				sql = "SELECT count FROM youtube_rythm WHERE city=\'"+cities[i]+"\'  ORDER BY id DESC"
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
				
				# send each citi metronome
				rhythmSerialList.append(finalRythm)
				
				sql = "INSERT INTO cityRythm (city,count) VALUES(\'"+cities[i]+"\',"+str(finalRythm)+")"
				print sql
				self.managerDB.insertRequestSQL(sql)
				
			print "========> ready to write 10 methronomes data"
			#self.rhythmSerialList = [40,20,80,10,50,70,90,75,40,55]	
			print "========> Writing the data from 10 methronomes data"
			# when is all correct send
			self.serial.write(rhythmSerialList)
		except:
			print "========> Error writting to serial 10 methronomes data"
			
if __name__ == "__main__":
	myRythmManager = rythmManager()
	rhythmSerialList = [230,0,80,10,50,70,90,54,40,55]
	i=chr(240)
	for r in range(0,10):
		print rhythmSerialList[r]
		i = chr(int(rhythmSerialList[r]))
			