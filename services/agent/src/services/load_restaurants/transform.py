from ...config import config
from .base import PlacesAPI
from .place import GooglePlace, GooglePlaceID
from ..exceptions import NoPlaceFound
import googlemaps
import polars as pl
from loguru import logger


class GoogleMapsAPI(PlacesAPI):
    def __init__(self, gmaps_client: googlemaps.Client):
        self.gmaps_client = gmaps_client
        self.fields_place = [
            "place_id",
            "name",
            "international_phone_number",
            "formatted_address",
            "formatted_phone_number",
            "website",
            "url",
            "business_status",
            "current_opening_hours",
            "editorial_summary",
            "geometry/location",
            "price_level",
            "rating",
            "type",
            "reservable",
            "delivery",
            "dine_in",
            "user_ratings_total",
            "wheelchair_accessible_entrance",
            "serves_beer",
            "serves_wine",
            "serves_breakfast",
            "serves_brunch",
            "serves_lunch",
            "serves_dinner",
            "serves_vegetarian_food",
            "takeout",
            "reviews",
        ]

    def get_places_by_name(self, places_names: list) -> list[GooglePlace]:
        # get all places id from place name
        places_id = [self.get_place_id(place_name) for place_name in places_names]

        return self.get_places_by_id(places_id)

    def get_places_by_id(self, places_id: list[GooglePlaceID]) -> list[GooglePlace]:
        # get place info - filter None values
        return [self.get_place_info(id) for id in places_id if id is not None]

    def get_place_id(self, place_name: str) -> "GooglePlaceID":
        """Get place ID field from place name from Google Maps API"""
        place_id = self.gmaps_client.find_place(
            place_name,
            "textquery",
            fields=["name", "place_id", "business_status"],
            location_bias="rectangle:41.372098117358036, 2.0780330895482972|41.412617353541314, 2.2242588063253073",
            language="en-US",
        )
        place = place_id.get("candidates", [])
        if place:
            logger.info(f"places ID: {place[0].get('name', None)}")
            return GooglePlaceID(
                name=place[0].get("name", None),
                id=place[0].get("place_id", None),
                business_status=place[0].get("business_status", None),
            )
        raise NoPlaceFound(f"No place found for {place_name}")

    def get_place_info(self, place_id: GooglePlaceID) -> "GooglePlace":
        """Get place info from place_id in Google Maps API"""
        place_info = self.gmaps_client.place(
            place_id.id,
            fields=self.fields_place,
            language="en-US",
            reviews_no_translations=True,
            reviews_sort="newest",
        )

        return GooglePlace.from_googlemaps_api_response(place_info)


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
    logger.info(places_id[0])
    # places = gmaps_api.get_places_by_id(places_id)
    place = gmaps_api.get_place_info(places_id[0])
    logger.info(place)
    breakpoint()
    # complet_place = Place.get_place(place)
    # logger.info(complet_place)
