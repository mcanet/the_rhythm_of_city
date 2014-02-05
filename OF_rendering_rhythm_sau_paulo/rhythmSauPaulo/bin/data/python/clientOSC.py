#!/usr/bin/env python
from OSC import *
from OSC import _readString, _readFloat, _readInt

class clientOSC():
	def __init__(self):
		self.default_port = 12345
		self.listen_address = ('localhost', self.default_port)
		
	def sendOSC(self,rhythmValue):
		c = OSCClient()
		c.connect(self.listen_address)
		subreq = OSCMessage("/rhythm")
		subreq.append(rhythmValue)
		c.send(subreq)
		c.close()