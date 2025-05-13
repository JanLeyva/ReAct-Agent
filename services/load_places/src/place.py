from typing import List
from pydantic import BaseModel


class Place(BaseModel):
    """
    A place from Google Maps API.
    """

    place_id: str
    name: str
    url: str
    international_phone_number: str | None
    formatted_address: str | None
    formatted_phone_number: str | None
    website: str | None
    business_status: str | None
    current_opening_hours: bool | None
    weekday_text: List[str] | None
    language: str | None
    overview: str | None
    geometry: list[float] | None
    price_level: int | None
    rating: float | None
    type: list[str] | None
    reservable: bool | None
    delivery: bool | None
    dine_in: bool | None
    user_ratings_total: int | None
    wheelchair_accessible_entrance: bool | None
    serves_beer: bool | None
    serves_wine: bool | None
    serves_breakfast: bool | None
    serves_brunch: bool | None
    serves_lunch: bool | None
    serves_dinner: bool | None
    serves_vegetarian_food: bool | None
    takeout: bool | None

    @classmethod
    def from_googlemaps_api_response(cls, response) -> "Place":
        """
        Returns a Place object from the Google Maps REST API response.

        Args:
            response: Google Maps API response from `place` method using `place_id`. d
        """
        result = response.get("result", {})

        return cls(
            place_id=result.get("place_id", None),
            name=result.get("name", None),
            international_phone_number=result.get("international_phone_number", None),
            formatted_address=result.get("formatted_address", None),
            formatted_phone_number=result.get("formatted_phone_number", None),
            website=result.get("website", None),
            url=result.get("url", None),
            business_status=result.get("business_status", None),
            current_opening_hours=cls.get_current_opening_hours(result),
            weekday_text=cls.get_weekday_text(result),
            language=cls.get_language(result),
            overview=cls.get_overview(result),
            geometry=cls.get_coordinates(result),
            price_level=result.get("price_level", None),
            rating=result.get("rating", None),
            type=result.get("type", None),
            reservable=result.get("reservable", None),
            delivery=result.get("delivery", None),
            dine_in=result.get("dine_in", None),
            user_ratings_total=result.get("user_ratings_total", None),
            wheelchair_accessible_entrance=result.get(
                "wheelchair_accessible_entrance", None
            ),
            serves_beer=result.get("serves_beer", None),
            serves_wine=result.get("serves_wine", None),
            serves_breakfast=result.get("serves_breakfast", None),
            serves_brunch=result.get("serves_brunch", None),
            serves_lunch=result.get("serves_lunch", None),
            serves_dinner=result.get("serves_dinner", None),
            serves_vegetarian_food=result.get("serves_vegetarian_food", None),
            takeout=result.get("takeout", None),
        )

    @staticmethod
    def get_coordinates(result: dict) -> list:
        """format coordinates from Google Maps API response."""
        geometry = result.get("geometry", None)
        if geometry:
            location = geometry.get("location", "")
            return [location["lat"], location["lng"]]
        raise ValueError(f"No coordinates for {result['name']}")

    @staticmethod
    def get_summary(result: dict) -> dict | None:
        return result.get("editorial_summary", None)

    @staticmethod
    def get_overview(result: dict) -> str | None:
        summary = Place.get_summary(result)
        if summary:
            return summary.get("overview", None)
        return None

    @staticmethod
    def get_language(result: dict) -> str | None:
        summary = Place.get_summary(result)
        if summary:
            return summary.get("language", None)
        return None

    @staticmethod
    def get_open_hours(result: dict) -> dict | None:
        return result.get("current_opening_hours", None)

    @staticmethod
    def get_current_opening_hours(result: dict) -> bool:
        open_hours = Place.get_open_hours(result)
        if open_hours:
            return open_hours.get("open_now", None)
        return None

    @staticmethod
    def get_weekday_text(result: dict) -> str | None:
        open_hours = Place.get_open_hours(result)
        if open_hours:
            return open_hours.get("weekday_text", None)
        return None

    def to_str(self) -> str:
        # pydantic method to convert the model to a dict
        return self.model_dump_json()

    def to_dict(self) -> dict:
        return self.model_dump()


class PlaceID(BaseModel):
    name: str | None
    id: str | None
    business_status: str | None
