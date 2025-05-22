# internal lib
from typing import Annotated
from src.config import config

# 3rd party
from llama_index.core.tools import FunctionTool
import googlemaps
# from geopy.distance import geodesic

# init googlemaps SDK
gmaps = googlemaps.Client(config.api_key_google_maps)


def get_restaurant_recommendation_from_text_coordinates(
    text: Annotated[str, "user preferences for the restaurant"],
    coordinates: Annotated[
        list, "Longitute and Latitue of user such as (41.387535, 2.175552)"
    ],
) -> str:
    """Useful for getting restaurants recommendations base on user request and coordinates"""
    return "Restaurant Lombo"


def get_restaurant_recommendation_from_text(
    text: Annotated[str, "user preferences for the restaurant"],
) -> str:
    """Useful for getting restaurants recommendations base on user request"""
    return "Restaurant Alapar"


def get_restaurant_recommendation_from_coordinates(
    coordinates: Annotated[
        list, "Longitute and Latitue of user such as (41.387535, 2.175552)"
    ],
) -> str:
    """Useful for getting restaurants recommendations base on user coordinates"""
    return "Restaurant Shunka"


def get_coordinates_from_street(
    street: Annotated[str, "get coordinates from street"],
) -> dict:
    """Useful to convert a street to coordinates to be used in `get_restaurant_recommendation_from_text_coordinates` or `get_restaurant_recommendation_from_coordinates`"""
    return gmaps.geocode(street, region="es")[0].get("geometry", {}).get("location", {})


tools = [
    FunctionTool.from_defaults(get_restaurant_recommendation_from_text),
    FunctionTool.from_defaults(get_restaurant_recommendation_from_coordinates),
    FunctionTool.from_defaults(get_restaurant_recommendation_from_text_coordinates),
    FunctionTool.from_defaults(get_coordinates_from_street),
]
