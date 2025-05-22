# internal libs
from src.config import config
from src.services.load_restaurants.googlemaps_api import GoogleMapsAPI
from src.services.load_restaurants.place import GooglePlace, GooglePlaceID, Place

# 3rd party
import pytest
import googlemaps

# Google Maps Client
gmaps_client = googlemaps.Client(key=config.googlemaps_api_key)
gmaps_api = GoogleMapsAPI(gmaps_client)


@pytest.mark.parametrize(("place_name"), ["Gresca", "Majide"])
def test_get_id_from_name(place_name: str):
    """Get place from google maps API from name"""
    response_place = gmaps_api.get_place_id(place_name)
    print(response_place)
    print(response_place.name)
    print(type(response_place.name))

    assert isinstance(response_place.name, str)
    assert isinstance(response_place.id, str)
    assert isinstance(response_place, GooglePlaceID)


@pytest.mark.parametrize(
    ("place_id"),
    [
        GooglePlaceID(
            name="fake", id="ChIJWdrChwajpBIR0YX0LwHyVDc", business_status="fake"
        ),
        GooglePlaceID(
            name="fake", id="ChIJuxezLF25Z0ARnEy3Hz3TVig", business_status="fake"
        ),
    ],
)
def test_get_place_info(place_id: GooglePlaceID):
    """Get place from google maps API from name"""
    response_place = gmaps_api.get_place_info(place_id)
    print(response_place)
    print(response_place.name)
    print(type(response_place.name))

    assert isinstance(response_place.place_id, str)
    assert isinstance(response_place.name, str)
    assert isinstance(response_place.url, str)
    assert isinstance(response_place, GooglePlace)


@pytest.mark.parametrize(
    ("google_place"),
    [
        GooglePlace(
            name="fake",
            place_id="ChIJWdrChwajpBIR0YX0LwHyVDc",
            url="fake_url.com",
            website="https://lastresmentiras.cat",
            overview=None,
            reviews=["mediterranean restaurant, seafood and wine."],
            language=None,
            business_status=None,
            user_ratings_total=None,
            types=None,
            current_opening_hours=None,
            international_phone_number=None,
            formatted_address=None,
            weekday_text=None,
            geometry=None,
            price_level=None,
            rating=None,
            reservable=None,
            delivery=None,
            dine_in=None,
            wheelchair_accessible_entrance=None,
            serves_beer=None,
            serves_wine=None,
            serves_breakfast=None,
            serves_brunch=None,
            serves_lunch=None,
            serves_dinner=None,
            serves_vegetarian_food=None,
            takeout=None,
        ),
        GooglePlace(
            name="fake",
            place_id="ChIJWdrChwajpBIR0YX0LwHyVDc",
            url="fake_url.com",
            website="https://lastresmentiras.cat",
            overview="japanes restaurant, good sushi and ramen.",
            reviews=["japanes restaurant, good sushi and ramen."],
            language=None,
            business_status=None,
            user_ratings_total=None,
            types=None,
            current_opening_hours=None,
            international_phone_number=None,
            formatted_address=None,
            weekday_text=None,
            geometry=None,
            price_level=None,
            rating=None,
            reservable=None,
            delivery=None,
            dine_in=None,
            wheelchair_accessible_entrance=None,
            serves_beer=None,
            serves_wine=None,
            serves_breakfast=None,
            serves_brunch=None,
            serves_lunch=None,
            serves_dinner=None,
            serves_vegetarian_food=None,
            takeout=None,
        ),
        GooglePlace(
            name="fake",
            place_id="ChIJWdrChwajpBIR0YX0LwHyVDc",
            url="fake_url.com",
            website=None,
            overview="japanes restaurant, good sushi and ramen.",
            reviews=None,
            language=None,
            business_status=None,
            user_ratings_total=None,
            types=None,
            current_opening_hours=None,
            international_phone_number=None,
            formatted_address=None,
            weekday_text=None,
            geometry=None,
            price_level=None,
            rating=None,
            reservable=None,
            delivery=None,
            dine_in=None,
            wheelchair_accessible_entrance=None,
            serves_beer=None,
            serves_wine=None,
            serves_breakfast=None,
            serves_brunch=None,
            serves_lunch=None,
            serves_dinner=None,
            serves_vegetarian_food=None,
            takeout=None,
        ),
    ],
)
def test_get_full_place(google_place: GooglePlace):
    """
    Get full place info: full_description, web_text,
    summary_review
    """
    place = Place.get_place(google_place)

    assert isinstance(place.full_description, str)
    assert isinstance(place, Place)
