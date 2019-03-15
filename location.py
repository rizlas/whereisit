class Location:
	def __init__(self, Id, address, country, countrySubdivision, latitude, longitude, locType):
		self.id = Id
		self.address = address
		self.country = country
		self.countrySubdivision = countrySubdivision
		self.latitude = latitude
		self.longitude = longitude
		self.locType = locType

	def toString(self):
		if self.countrySubdivision is not None:
			return "<b>Address: {0}\n</b>Country: {1} - {2}\nLat: {3} Lon: {4}\nType: {5}\n<i>Show:</i> /{6}\n".format(self.address, self.country, self.countrySubdivision, self.latitude, self.longitude, self.locType, self.id)
		else:
			return "<b>Address: {0}\n</b>Country: {1}\nLat: {2} Lon: {3}\nType: {4}\n<i>Show:</i> /{5}\n".format(self.address, self.country, self.latitude, self.longitude, self.locType, self.id)