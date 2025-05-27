from ...config import config
from .base import PlacesAPI
from .place import GooglePlace, GooglePlaceID, Place
from ..exceptions import NoPlaceFound
import googlemaps
import polars as pl
from loguru import logger


class GoogleMapsAPI(PlacesAPI):
    def __init__(self):
        self.gmaps_client = googlemaps.Client(key=config.googlemaps_api_key)
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
            place = place[0]
            logger.info(f"places ID: {place.get('name', None)}")
            return GooglePlaceID(
                name=place.get("name", None),
                id=place.get("place_id", None),
                business_status=place.get("business_status", None),
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

    def get_places_bulk(self, places_names: list) -> pl.DataFrame:
        """Get places from GoogleMaps API
        1. Get place ID from name
        2. Get place information from ID
        3. Refine place information with web scap, summary descriptions

        Input: list[str] of places names

        Return:
           (pl.DataFrame): with all places."""
        # get all places id from place name
        logger.info("get places ID")
        places_id = [self.get_place_id(place_name) for place_name in places_names]
        logger.info("get places details")
        places_info = self._get_places_by_id(places_id)
        logger.info("get places details")
        places_complet = [Place.get_place(place_id) for place_id in places_info]

        return pl.DataFrame(places_complet)

    def _get_places_by_id(self, places_id: list[GooglePlaceID]) -> list[GooglePlace]:
        """Get places information by ID in bulk"""
        # get place info - filter None values
        return [self.get_place_info(id) for id in places_id if id is not None]
