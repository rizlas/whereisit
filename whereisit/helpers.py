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


def coordinate_search(lat, lon, api_url_base_reverse_geocode, api_key):
    # TODO add docstring
    api_url = f"{api_url_base_reverse_geocode}{lat}, {lon}.json?key={api_key}"

    logger.info("Api requests url: %s", api_url)

    response = requests.get(api_url)
    status_code = response.status_code

    if status_code == 200:
        json_data = json.loads(response.content.decode("utf-8"))

        if json_data["addresses"][0]["address"].get("country") is not None:
            title = json_data["addresses"][0]["address"]["country"]
            if (
                json_data["addresses"][0]["address"].get("countrySubdivision")
                is not None
            ):
                title += (
                    ", " + json_data["addresses"][0]["address"]["countrySubdivision"]
                )
        else:
            title = f"{lat}, {lon}"

        if json_data["addresses"][0]["address"].get("freeformAddress") is not None:
            address = json_data["addresses"][0]["address"]["freeformAddress"]
        else:
            address = f"{lat}, {lon}"

        return status_code, title, address
    elif status_code == 400:
        return status_code, "One or more parameters were incorrectly specified.", ""
    else:
        return status_code, "An error has occured", ""


def get_locations(param, api_url_base_geocode, api_key):
    # TODO add docstring
    api_url = f"{api_url_base_geocode}{param}.json?key={api_key}"
    logger.info("Api url: %s", api_url_base_geocode)
    response = requests.get(api_url)

    if response.status_code == 200:
        data_json = json.loads(response.content.decode("utf-8"))
        location_count = int(data_json["summary"]["numResults"])
        locations = []

        logger.info("COUNT %s", location_count)

        if location_count > 0:
            for i in data_json["results"]:
                loc_tmp = Location(
                    location_id=i["id"].replace("/", "_"),
                    address=i["address"]["freeformAddress"],
                    country=i["address"]["country"],
                    country_subdivision=None,
                    country_secondary_subdivision=None,
                    country_subdivision_name=None,
                    latitude=i["position"]["lat"],
                    longitude=i["position"]["lon"],
                    loc_type=i["type"],
                )

                if i["address"].get("country_subdivision") is not None:
                    loc_tmp.country_subdivision = i["address"]["country_subdivision"]

                if i["address"].get("country_secondary_subdivision") is not None:
                    loc_tmp.country_secondary_subdivision = i["address"][
                        "country_secondary_subdivision"
                    ]

                if i["address"].get("country_subdivision_name") is not None:
                    loc_tmp.country_subdivision_name = i["address"][
                        "country_subdivision_name"
                    ]

                locations.append(loc_tmp)

            return response.status_code, locations, location_count

        return 204, None, None  # HTTP No content
    else:
        logger.error("Error response code: %s", response.status_code)
        return response.status_code, None, None


def encode_lat_lon(lat, lon):
    return str(base58.b58encode(f"{lat},{lon}".encode("utf-8")), "utf-8")


def decode_lat_lon(lat_lon_encoded):
    return str(base58.b58decode(lat_lon_encoded.encode("utf-8")), "utf-8")


def lat_lon_parse(lat, lon):
    try:
        lat = lat.strip()
        lon = lon.strip()

        float(lat)
        float(lon)
        return True
    except ValueError:
        return False


def is_coordinate_search(param):
    # TODO add docstring
    lat, lon = param.split(",")
    logger.info("is_coordinate_search: %s", param)

    return lat_lon_parse(lat, lon)
