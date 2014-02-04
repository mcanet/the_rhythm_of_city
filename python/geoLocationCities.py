
class geoLocationCities():
	def __init__(self):
		self.cities = dict()
		self.cities["istambul"] = "41.012379,28.975926"
		self.cities["london"] = "51.500152,-0.126236"
		self.cities["new+york"] = "40.75604,-73.986941"
		self.cities["tokio"] = "35.6894875,139.6917064"
		self.cities["barcelona"] = "41.387917,2.169919"
		self.cities["paris"] = "48.856667,2.350987"
		self.cities["berlin"] = "52.52348,13.411494"
		self.cities["mexicodf"] = "19.42705,-99.127571"
		self.cities["rome"] = "41.895466,12.482324"
		self.cities["praha"] = "50.08333,14.41667"
		self.cities["moscou"] = "55.755786,37.617633"
		self.cities["san+francisco"] = "37.775196,-122.419204"
		self.cities["new+delhi"] = "28.635308,77.22496"	
		self.cities["vienna"] = "48.209206,16.372778"
		self.cities["rosario"] = "-32.950741,-60.6665"
		self.cities["buenos_aires"] = "-34.595569,-58.385269"
		self.cities["sao+paulo"] = "-23.548943,-46.638818"
		self.cities["adelaide"] = "-34.933333,138.5833333"
		
	def getLatLon(self, city):
		return self.cities[city]
		
