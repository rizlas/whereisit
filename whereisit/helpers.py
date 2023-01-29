"""
Helper functions for the entire bot.
"""

import logging
import json
import requests
import base58

from location import Location

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


def coordinate_search(
    lat: str, lon: str, api_url_base_reverse_geocode: str, api_key: str
) -> tuple[int, str, str]:
    """
    Performs a coordinate search to retrieve information about a location
    based on its latitude and longitude.

    Args:
        lat (str): Latitude of the location to be searched.
        lon (str): Longitude of the location to be searched.
        api_url_base_reverse_geocode (str): Base URL of the reverse geocode api.
        api_key (str): Api key to access the apis.

    Returns:
        tuple[int, str, str]: A tuple of status code, title, and address of the location.
        The status code is an integer indicating the success
        or failure of the API request.
        The title is a string representing the country and/or state of the location.
        The address is a string representing the complete address of the location.
        If the api request fails, the title will contain an error message and
        the address will be an empty string.
    """

    api_url = f"{api_url_base_reverse_geocode}{lat}, {lon}.json?key={api_key}"

    logger.info("Api requests url: %s", api_url)

    response = requests.get(api_url, timeout=60)
    status_code = response.status_code

    if status_code == 200:
        json_data = json.loads(response.content.decode("utf-8"))

        address = json_data["addresses"][0]["address"]
        country = address.get("country")
        country_subdivision = address.get("countrySubdivision")

        if country is not None:
            title = country
            if country_subdivision is not None:
                title += f", {country_subdivision}"
        else:
            title = f"{lat}, {lon}"

        address = address.get("freeformAddress", f"{lat}, {lon}")

        return status_code, title, address

    if status_code == 400:
        return status_code, "One or more parameters were incorrectly specified.", ""

    return status_code, "An error has occured", ""


def get_locations(
    param: str, api_url_base_geocode: str, api_key: str
) -> tuple[int, list, int]:
    """
    This function makes an API request to a geocoding service
    to retrieve location information based on a search parameter.

    If the API call returns a 200 status code, the response content
    is loaded as a JSON object and the location information is extracted.
    The number of locations returned is stored in 'location_count' and a
    list of Location objects, 'locations', is created from the extracted information.

    If the location count is 0, the function returns a 204 HTTP No Content response.

    If the API call returns any other status code, an error message is logged
    and the function returns the response status code along with None for
    the location data and 0 for location count.

    Args:
        param (str): Search parameter
        api_url_base_geocode (str): Base URL of the geocode api
        api_key (str): Api key to access the apis.

    Returns:
        tuple[int, list, int]:  the response status code,
        a list of Location objects (or None), and the number of locations (or 0).
    """

    api_url = f"{api_url_base_geocode}{param}.json?key={api_key}"
    logger.info("Api url: %s", api_url_base_geocode)
    response = requests.get(api_url, timeout=60)

    if response.status_code == 200:
        data_json = json.loads(response.content.decode("utf-8"))
        location_count = int(data_json["summary"]["numResults"])
        locations = []

        logger.info("COUNT %s", location_count)

        if location_count == 0:
            return 204, None, None  # HTTP No content

        for i in data_json["results"]:
            address = i["address"]
            country_subdivision = address.get("country_subdivision")
            country_secondary_subdivision = address.get("country_secondary_subdivision")
            country_subdivision_name = address.get("country_subdivision_name")

            loc_tmp = Location(
                location_id=i["id"].replace("/", "_"),
                address=address["freeformAddress"],
                country=address["country"],
                country_subdivision=country_subdivision,
                country_secondary_subdivision=country_secondary_subdivision,
                country_subdivision_name=country_subdivision_name,
                latitude=i["position"]["lat"],
                longitude=i["position"]["lon"],
                loc_type=i["type"],
            )

            locations.append(loc_tmp)

        return response.status_code, locations, location_count

    logger.error("Error response code: %s", response.status_code)
    return response.status_code, None, 0


def encode_lat_lon(lat: str, lon: str) -> str:
    """
    This function takes in latitude and longitude as inputs
    and encodes them into a Base58 string format.

    Args:
        lat (str): Latitude value
        lon (str): Longitude value

    Returns:
        str: Base58 encoded string representation of latitude and longitude
    """

    return str(base58.b58encode(f"{lat},{lon}".encode("utf-8")), "utf-8")


def decode_lat_lon(lat_lon_encoded: str) -> str:
    """
    Decodes the encoded latitude and longitude using base58 encoding.

    Args:
        lat_lon_encoded (str): Encoded latitude and longitude.

    Returns:
        str: Decoded latitude and longitude.
    """

    return str(base58.b58decode(lat_lon_encoded.encode("utf-8")), "utf-8")


def lat_lon_parse(lat: str, lon: str) -> bool:
    """
    Checks if the provided latitude and longitude values can be converted to float.

    Args:
        lat (str): Latitude value
        lon (str): Longitude value

    Returns:
        bool: True if both values can be converted to float, False otherwise.
    """

    try:
        lat = lat.strip()
        lon = lon.strip()

        float(lat)
        float(lon)
        return True
    except ValueError:
        return False


def is_coordinate_search(param: str) -> str:
    """
    Check if a given search parameter is a latitude and longitude coordinate string.

    Args:
        param (str): The search parameter to check.

    Returns:
        str: True if the search parameter is a coordinate string, False otherwise.
    """

    lat, lon = param.split(",")
    logger.info("is_coordinate_search: %s", param)

    return lat_lon_parse(lat, lon)
