# internal lib
from typing import Annotated, Optional

# 3rd party
from llama_index.core.tools import FunctionTool


def get_restaurant_recommendation(
    text: Annotated[str, "user preferences for the restaurant"],
    coordinates: Annotated[
        Optional[list], "Longitute and Latitue of user such as (41.387535, 2.175552)"
    ],
) -> str:
    """Useful for getting restaurants recommendations base on user request and optional coordinates"""
    # TODO delete the mook
    if not coordinates:
        coordinates = "fake"
    return "Restaurant Lombo"


def get_coordinates_from_street(street: Annotated[str, "from street get coordinates"]):
    """Useful to convert a street to coordinates to be used in `get_restaurant_recommendation`"""
    return [41.387588, 2.175582]


def ask_more_information(
    input: Annotated[str, "Ask questions to gather more information"],
):
    return input


tools = [
    FunctionTool.from_defaults(get_restaurant_recommendation),
    FunctionTool.from_defaults(get_coordinates_from_street),
    # FunctionTool.from_defaults(ask_more_information),
]
