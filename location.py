class Location:
	def __init__(self, Id, address, country, countrySubdivision, countrySecondarySubdivision, countrySubdivisionName, latitude, longitude, locType):
		self.id = Id
		self.address = address
		self.country = country
		self.countrySubdivision = countrySubdivision
		self.countrySecondarySubdivision = countrySecondarySubdivision
		self.countrySubdivisionName = countrySubdivisionName
		self.latitude = latitude
		self.longitude = longitude
		self.locType = locType

	def subDivision(self):
		string_ret = ""

		if self.countrySubdivision is not None:
			string_ret = self.countrySubdivision
			if self.countrySubdivisionName is not None:
				string_ret += " ({0})".format(self.countrySubdivisionName)
			if self.countrySecondarySubdivision is not None:
				string_ret += ", {0}".format(self.countrySecondarySubdivision)

		return string_ret

	def toString(self):
		if self.countrySubdivision is not None:
			return "<b>Address: {0}\n</b>Country: {1} - {2}\nLat: {3} Lon: {4}\nType: {5}\n<i>Show:</i> /{6}\n".format(self.address, self.country, self.subDivision(), self.latitude, self.longitude, self.locType, self.id)
		else:
			return "<b>Address: {0}\n</b>Country: {1}\nLat: {2} Lon: {3}\nType: {4}\n<i>Show:</i> /{5}\n".format(self.address, self.country, self.latitude, self.longitude, self.locType, self.id)

# 