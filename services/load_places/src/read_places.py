# internal libs
from config import config
# 3rd party libs
import googlemaps
import polars as pl
from loguru import logger

fields_place = [
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
                # "reviews"                
                ]


# https://places.googleapis.com/v1/places/
gmaps = googlemaps.Client(key=config.googlemaps_api_key)

hi_vull_anar = pl.read_csv("/Users/esengineer/Downloads/Takeout-2/Saved/Hi vull anar.csv", separator=",")

restaurant_name = hi_vull_anar.select(pl.col("Títol")).to_series().to_list()


all_data = pl.DataFrame()
for restaurant in restaurant_name:
    logger.info(restaurant)
    # find place id from Name
    place_id = gmaps.find_place(
                restaurant,
                "textquery",
                fields=["place_id", "business_status"],
                location_bias="rectangle:41.372098117358036, 2.0780330895482972|41.412617353541314, 2.2242588063253073",
                language="en-US",
    )
    place = place_id.get("candidates", [])
    logger.info(place_id)
    if place:
        # search: https://maps.googleapis.com/maps/api/place/details/json
        response_place = gmaps.place(
                    place[0].get("place_id", None),
                    fields=fields_place,
                    language="en-US",
                    reviews_no_translations=True,
                    reviews_sort="newest",
                )
        
        response_place = response_place.get("result", {})
        coordinates = response_place.get("geometry", "").get("location", "")
        summary = response_place.get("editorial_summary", None)
        open_hours = response_place.get("current_opening_hours", None)
        geo = [coordinates['lat'], coordinates['lng']]

        formatted_data = pl.DataFrame({
            "place_id": [response_place.get("place_id", None)],
            "name": [response_place.get("name", None)],
            "international_phone_number": [response_place.get("international_phone_number", None)],
            "formatted_address": [response_place.get("formatted_address", None)],
            "formatted_phone_number": [response_place.get("formatted_phone_number", None)],
            "website": [response_place.get("website", None)],
            "url": [response_place.get("url", None)],
            "business_status": [response_place.get("business_status", None)],
            "current_opening_hours": [open_hours.get("open_now", None) if open_hours else None],
            "weekday_text": [open_hours.get("weekday_text", None) if open_hours else None],
            "language": [summary.get("language", None) if summary else None],
            "overview": [summary.get("overview", None) if summary else None],
            "geometry": [geo],
            "price_level": [response_place.get("price_level", None)],
            "rating": [response_place.get("rating", None)],
            "type": [response_place.get("type", None)],
            "reservable": [response_place.get("reservable", None)],
            "delivery": [response_place.get("delivery", None)],
            "dine_in": [response_place.get("dine_in", None)],
            "user_ratings_total": [response_place.get("user_ratings_total", None)],
            "wheelchair_accessible_entrance": [response_place.get("wheelchair_accessible_entrance", None)],
            "serves_beer": [response_place.get("serves_beer", None)],
            "serves_wine": [response_place.get("serves_wine", None)],
            "serves_breakfast": [response_place.get("serves_breakfast", None)],
            "serves_brunch": [response_place.get("serves_brunch", None)],
            "serves_lunch": [response_place.get("serves_lunch", None)],
            "serves_dinner": [response_place.get("serves_dinner", None)],
            "serves_vegetarian_food": [response_place.get("serves_vegetarian_food", None)],
            "takeout": [response_place.get("takeout", None)],
            # "reviews": [response_place.get("reviews", None)]
            })

        logger.info(formatted_data)
        all_data = pl.concat([all_data, formatted_data])



breakpoint()

all_data = pl.DataFrame(all_data)
all_data.write_parquet("restaurants.parquet")
logger.info(all_data)
