# internal libs
from src.place import Place
from src.google_maps import GoogleMapsAPI
from src.config import config
# 3rd party
import googlemaps
from loguru import logger


def main(gmaps_client: googlemaps.Client, place_name: str) -> "Place":
    # Google Maps API
    gmaps_api = GoogleMapsAPI(gmaps_client)
    # Get places ID by name
    place_id = gmaps_api.get_place_id(place_name)
    # Get places info by ID
    place_info = gmaps_api.get_place_info(place_id)

    return place_info



if __name__ == "__main__":
    # Google Maps Client
    gmaps_client = googlemaps.Client(key=config.googlemaps_api_key)
    place_info = main(gmaps_client, "La Sagrada Familia")
    logger.info(f"Place info: {place_info}")
    # upload to DB

