from config import config
from base import PlacesAPI
from place import Place, PlaceID

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

    def get_places_by_name(self, places_names: list) -> list[Place]:
        # get all places id from place name
        places_id = [self.get_place_id(place_name) for place_name in places_names]
        logger.info(f"places ID: {places_id}")

        return self.get_places_by_id(places_id)

    def get_places_by_id(self, places_id: list[PlaceID]) -> list[Place]:
        # get place info - filter None values
        places = [self.get_place_info(id) for id in places_id if id is not None]
        logger.info(f"places FULL info: {places}")

        return places

    def get_place_id(self, place_name: str) -> "PlaceID":
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
            return PlaceID(
                name=place[0].get("name", None),
                id=place[0].get("place_id", None),
                business_status=place[0].get("business_status", None),
            )

    def get_place_info(self, place_id: PlaceID) -> "Place":
        """Get place info from place_id in Google Maps API"""
        place_info = self.gmaps_client.place(
            place_id.id,
            fields=self.fields_place,
            language="en-US",
            reviews_no_translations=True,
            reviews_sort="newest",
        )

        return Place.from_googlemaps_api_response(place_info)


if __name__ == "__main__":
    # Google Maps Client
    gmaps_client = googlemaps.Client(key=config.googlemaps_api_key)

    # Places from my persnal list
    hi_vull_anar = pl.read_csv(
        "/Users/esengineer/Downloads/Takeout-2/Saved/Hi vull anar.csv", separator=","
    )
    places_names = hi_vull_anar.select(pl.col("Títol")).to_series().to_list()

    gmaps_api = GoogleMapsAPI(gmaps_client)
    # places = gmaps_api.get_places_by_name(places_names)
    # asd = gmaps_api.get_place_info(PlaceID(name="test",
    #                                         id="ChIJSTemK5CipBIRNV6PIhXQ3bk",
    #                                         business_status="fake"))
    places_id = pl.read_excel(
        "/Users/esengineer/Documents/_dev/whatsapp-agent/services/load_places/data_filter.xlsx"
    )
    places_id = [
        PlaceID(name="fake", id=id, business_status="fake")
        for id in places_id["place_id"].to_list()
    ]
    logger.info(places_id)
    places = gmaps_api.get_places_by_id(places_id)

    breakpoint()
    # pl.DataFrame(places).write_parquet(
    #     f"{datetime.now().strftime("%Y%m%d")}_restaurants.parquet"
    # )
