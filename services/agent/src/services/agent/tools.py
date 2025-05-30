# internal lib
from typing import Annotated
from src.config import config
from ..search_engine.vector_store import VectorStore

# 3rd party
from llama_index.core.tools import FunctionTool
import googlemaps
from loguru import logger
# from geopy.distance import geodesic

# init googlemaps SDK
gmaps = googlemaps.Client(config.api_key_google_maps)
vec = VectorStore()


def get_restaurant_recommendation_from_text_and_coordinates(
    text: Annotated[str, "user preferences for the restaurant"],
    coordinates: Annotated[
        list, "Longitute and Latitue of user such as (41.387535, 2.175552)"
    ],
) -> str:
    """Useful for getting restaurants recommendations base on user request and coordinates"""
    logger.info("get_restaurant_recommendation_from_text_coordinates")
    return vec.semantic_search_with_filter(text, coordinates[0], coordinates[1])


def get_restaurant_recommendation_from_text(
    text: Annotated[str, "user preferences for the restaurant"],
) -> str:
    """
    Useful for getting restaurants recommendations base on user request.
    user request -> text. example is a description of the restaurant they want.
    """
    logger.info("get_restaurant_recommendation_from_text")
    return vec.semantic_search(text)


# TODO dev the function
# def get_restaurant_recommendation_from_just_coordinates(
#     coordinates: Annotated[
#         list, "Longitute and Latitue of user such as (41.387535, 2.175552)"
#     ],
# ) -> str:
#     """Useful for getting restaurants recommendations just using coordinates no any other information"""
#     logger.info("get_restaurant_recommendation_from_coordinates")
#     return "Restaurant Shunka"


def get_coordinates_from_street(
    street: Annotated[str, "get coordinates from street"],
) -> dict:
    """Useful to convert a street to coordinates to be used in `get_restaurant_recommendation_from_text_coordinates` or `get_restaurant_recommendation_from_coordinates`"""
    return gmaps.geocode(street, region="es")[0].get("geometry", {}).get("location", {})


tools = [
    FunctionTool.from_defaults(get_restaurant_recommendation_from_text),
    # FunctionTool.from_defaults(get_restaurant_recommendation_from_just_coordinates),
    FunctionTool.from_defaults(get_restaurant_recommendation_from_text_and_coordinates),
    FunctionTool.from_defaults(get_coordinates_from_street),
]
