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

types_df = {
                "place_id": str,
                "name": str,
                "international_phone_number": str,
                "formatted_address": str,
                "formatted_phone_number": str,
                "website": str,
                "url": str,
                "business_status": str,
                "current_opening_hours": str,
                "language": str,
                "summary": str,
                "geometry": str,
                "price_level": int,
                "rating": float,
                "type": str,
                "reservable": bool,
                "delivery": bool,
                "dine_in": bool,
                "user_ratings_total": bool,
                "wheelchair_accessible_entrance": bool,
                "serves_beer": bool,
                "serves_wine": bool,
                "serves_breakfast": bool,
                "serves_brunch": bool,
                "serves_lunch": bool,
                "serves_dinner": bool,
                "serves_vegetarian_food": bool,
                "takeout": bool,

}

# https://places.googleapis.com/v1/places/
gmaps = googlemaps.Client(key=config.googlemaps_api_key)

hi_vull_anar = pl.read_csv("/Users/esengineer/Downloads/Takeout-2/Saved/Hi vull anar.csv", separator=",")

restaurant_name = hi_vull_anar.select(pl.col("Títol")).to_series().to_list()


all_data = []
for restaurant in restaurant_name[:5]:
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
                    place[0].get("place_id", "NOT_FOUND"),
                    fields=fields_place,
                    language="en-US",
                    reviews_no_translations=True,
                    reviews_sort="newest",
                )
        
        response_place = response_place.get("result", {})
        coordinates = response_place.get("geometry", "").get("location", "")
        summary = response_place.get("editorial_summary", None)
        geo = [coordinates['lat'], coordinates['lng']]

        formatted_data = {
            "place_id": [response_place.get("place_id", pl.Null)],
            "name": [response_place.get("name", pl.Null)],
            "international_phone_number": [response_place.get("international_phone_number", pl.Null)],
            "formatted_address": [response_place.get("formatted_address", pl.Null)],
            "formatted_phone_number": [response_place.get("formatted_phone_number", pl.Null)],
            "website": [response_place.get("website", pl.Null)],
            "url": [response_place.get("url", pl.Null)],
            "business_status": [response_place.get("business_status", pl.Null)],
            "current_opening_hours": [response_place.get("current_opening_hours", pl.Null)],
            "language": [summary.get("language", pl.Null) if summary else pl.Null],
            "overview": [summary.get("overview", pl.Null) if summary else pl.Null],
            "geometry": [geo],
            "price_level": [response_place.get("price_level", pl.Null)],
            "rating": [response_place.get("rating", pl.Null)],
            "type": [response_place.get("type", pl.Null)],
            "reservable": [response_place.get("reservable", pl.Null)],
            "delivery": [response_place.get("delivery", pl.Null)],
            "dine_in": [response_place.get("dine_in", pl.Null)],
            "user_ratings_total": [response_place.get("user_ratings_total", pl.Null)],
            "wheelchair_accessible_entrance": [response_place.get("wheelchair_accessible_entrance", pl.Null)],
            "serves_beer": [response_place.get("serves_beer", pl.Null)],
            "serves_wine": [response_place.get("serves_wine", pl.Null)],
            "serves_breakfast": [response_place.get("serves_breakfast", pl.Null)],
            "serves_brunch": [response_place.get("serves_brunch", pl.Null)],
            "serves_lunch": [response_place.get("serves_lunch", pl.Null)],
            "serves_dinner": [response_place.get("serves_dinner", pl.Null)],
            "serves_vegetarian_food": [response_place.get("serves_vegetarian_food", pl.Null)],
            "takeout": [response_place.get("takeout", pl.Null)],
            # "reviews": [response_place.get("reviews", pl.Null)]
            }

        logger.info(formatted_data)
        # all_data = pl.concat([all_data, formatted_data])
        all_data.append(formatted_data)


breakpoint()

all_data = pl.DataFrame(all_data)
all_data.write_parquet("restaurants.parquet")
logger.info(all_data)
