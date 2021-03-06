class Location:
    def __init__(
        self,
        location_id,
        address,
        country,
        country_subdivision,
        country_secondary_subdivision,
        country_subdivision_name,
        latitude,
        longitude,
        loc_type,
    ):
        self.location_id = location_id
        self.address = address
        self.country = country
        self.country_subdivision = country_subdivision
        self.country_secondary_subdivision = country_secondary_subdivision
        self.country_subdivision_name = country_subdivision_name
        self.latitude = latitude
        self.longitude = longitude
        self.loc_type = loc_type

    def sub_division(self):
        string_ret = ""

        if self.country_subdivision is not None:
            string_ret = self.country_subdivision
            if self.country_subdivision_name is not None:
                string_ret += " ({0})".format(self.country_subdivision_name)
            if self.country_secondary_subdivision is not None:
                string_ret += ", {0}".format(self.country_secondary_subdivision)

        return string_ret

    def __str__(self):
        import logic

        if self.country_subdivision is not None:
            string_repr = (
                f"<b>Address: {self.address}\n"
                f"</b>Country: {self.country} - {self.sub_division()}\n"
                f"Lat: {self.latitude} Lon: {self.longitude}\n"
                f"Type: {self.loc_type}\n"
                f"<i>Show:</i> /{logic.encode_lat_lon(self.latitude, self.longitude)}\n"
            )
            return string_repr
        else:
            string_repr = (
                f"<b>Address: {self.address}\n"
                f"</b>Country: {self.country}\n"
                f"Lat: {self.latitude} Lon: {self.longitude}\n"
                f"Type: {self.loc_type}\n"
                f"<i>Show:</i> /{logic.encode_lat_lon(self.latitude, self.longitude)}\n"
            )

            return string_repr

