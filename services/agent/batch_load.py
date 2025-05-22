from src.config import config
from src.services.load_restaurants.place import GooglePlaceID, Place
from services.agent.src.services.load_restaurants.googlemaps_api import GoogleMapsAPI

# 3rd party
import googlemaps
import polars as pl
from loguru import logger


if __name__ == "__main__":
    # Google Maps Client
    gmaps_client = googlemaps.Client(key=config.googlemaps_api_key)
    gmaps_api = GoogleMapsAPI(gmaps_client)

    # Places from my persnal list - Uncomment below in case GET places from NAME
    # hi_vull_anar = pl.read_csv(
    #     "data/Hi vull anar.csv", separator=","
    # )
    # places_names = hi_vull_anar.select(pl.col("Títol")).to_series().to_list()

    places_id = pl.read_parquet(
        "/Users/esengineer/Documents/_dev/whatsapp-agent/docs/data/filtered_data.parquet"
    )

    places_id = [
        GooglePlaceID(name="fake", id=id, business_status="fake")
        for id in places_id["place_id"].to_list()
    ]
    places_id = places_id[:3]
    logger.info(places_id)

    # places = gmaps_api.get_places_by_id(places_id)
    places_info = [gmaps_api.get_place_info(place) for place in places_id]
    complet_places = [Place.get_place(place_id) for place_id in places_info]
    logger.info(complet_places)
    breakpoint()
