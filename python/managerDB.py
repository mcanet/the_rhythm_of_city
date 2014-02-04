#!/usr/bin/python
import sqlite3 as lite
import time
from datetime import datetime

class managerDB:
	def __init__(self):
		init = ''

	def insertRequestSQL(self,sql):
		try:
			conn = lite.connect('test.db')
			c = conn.cursor()
			c.execute(sql)
			c.close()
			conn.commit()
			conn.close()
		except:
			print "ERROR insert at Mysql :"+sql
	
	def selectRequestSQL(self,sql):
		try:
			conn = lite.connect('test.db')
			c = conn.cursor()
			c.execute(sql)
			row = c.fetchone()
			c.close()
			conn.close()
		except:
			print "ERROR select at Mysql "
			row = ['','','']
		return row
	
	def recordRythm(self, tableName, city, count):
		try:
			sql = "INSERT INTO "+tableName+" (city,count) VALUES('"+city+"',"+str(count)+")"
			print sql
			self.insertRequestSQL(sql)	
		except:
			print "ERROR: database record Rythm"
		
	def recordItem(self, tableName, city, count):
		try:
			sql = "INSERT INTO "+tableName+" (city,count) VALUES('"+city+"',"+str(count)+")"
			print sql
			self.insertRequestSQL(sql)
		except:
			print "ERROR: database record Item"
		
	def recordLogError(self, service, city, where):
		try:
			sql = "INSERT INTO error_log (city,service, place) VALUES('"+city+"','"+service+"','"+where+"')"
			print sql
			self.insertRequestSQL(sql)
		except:
			print "ERROR: database record Error"
			
	def closeDB(self):
		print "close db connection!!"
			
if __name__ == "__main__":
	m = managerDB()