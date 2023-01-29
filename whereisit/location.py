"""
This module contains the implementation of the Location class.
"""
import helpers


class Location:
    """
    This class stores location information including address, country,
    subdivision, latitude, longitude and location type

    Attributes:
        location_id (int): The unique identifier for the location.
        address (str): The street address of the location.
        country (str): The country the location is in.
        country_subdivision (str): The primary subdivision of the location's
                                   country (e.g. state, province).
        country_secondary_subdivision (str): The secondary subdivision of the
                                             location's country (e.g. county).
        country_subdivision_name (str): The name of the primary subdivision
                                        of the location's country.
        latitude (float): The latitude coordinate of the location.
        longitude (float): The longitude coordinate of the location.
        loc_type (str): The type of location (e.g. residential, commercial, etc.).
    """

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

    def sub_division(self) -> str:
        """
        Get the entire subdivision if exists.
        Concatenate primary and seconday subdivision.

        Returns:
            str: Subdivison
        """

        if self.country_subdivision is None:
            return ""

        subdivision = self.country_subdivision

        if self.country_subdivision_name is not None:
            subdivision += f" ({self.country_subdivision_name})"

        if self.country_secondary_subdivision is not None:
            subdivision += f", {self.country_secondary_subdivision}"

        return subdivision

    def __str__(self) -> str:
        """
        Location representation.

        Returns:
            str: A string representation of the Address object.
        """

        sub_division = f" - {self.sub_division()}" if self.country_subdivision else ""

        string_repr = (
            f"<b>Address: {self.address}\n"
            f"</b>Country: {self.country}{sub_division}\n"
            f"Lat: {self.latitude} Lon: {self.longitude}\n"
            f"Type: {self.loc_type}\n"
            f"<i>Show:</i> /{helpers.encode_lat_lon(self.latitude, self.longitude)}\n"
        )

        return string_repr
