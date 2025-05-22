# 1st party
from typing import List

# internal libs
from src.templates.prompts import CLEAN_WEB_TEXT, SUMMARY_REVIEW
from src.llm.factory import llm

# 3rd party
import asyncio
from pydantic import BaseModel
from crawl4ai import AsyncWebCrawler


class PlaceModel(BaseModel):
    """Base model for validate Place"""

    place_id: str
    name: str
    url: str
    international_phone_number: str | None
    formatted_address: str | None
    website: str | None
    weekday_text: List[str] | None
    overview: str | None
    geometry: list[float] | None
    price_level: int | None
    rating: float | None
    reservable: bool | None
    delivery: bool | None
    dine_in: bool | None
    wheelchair_accessible_entrance: bool | None
    serves_beer: bool | None
    serves_wine: bool | None
    serves_breakfast: bool | None
    serves_brunch: bool | None
    serves_lunch: bool | None
    serves_dinner: bool | None
    serves_vegetarian_food: bool | None
    takeout: bool | None


class GooglePlace(PlaceModel):
    """
    A place from Google Maps API.
    """

    language: str | None
    business_status: str | None
    current_opening_hours: bool | None
    user_ratings_total: int | None
    types: list[str] | None
    reviews: list | None

    @classmethod
    def from_googlemaps_api_response(cls, response) -> "GooglePlace":
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
            types=result.get("types", None),
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
            reviews=cls.get_reviews(result),
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
        summary = GooglePlace.get_summary(result)
        if summary:
            return summary.get("overview", None)
        return None

    @staticmethod
    def get_language(result: dict) -> str | None:
        summary = GooglePlace.get_summary(result)
        if summary:
            return summary.get("language", None)
        return None

    @staticmethod
    def get_open_hours(result: dict) -> dict | None:
        return result.get("current_opening_hours", None)

    @staticmethod
    def get_current_opening_hours(result: dict) -> bool:
        open_hours = GooglePlace.get_open_hours(result)
        if open_hours:
            return open_hours.get("open_now", None)
        return None

    @staticmethod
    def get_weekday_text(result: dict) -> str | None:
        open_hours = GooglePlace.get_open_hours(result)
        if open_hours:
            return open_hours.get("weekday_text", None)
        return None

    @staticmethod
    def get_reviews(result: dict) -> list | None:
        reviews = result.get("reviews", None)
        if reviews:
            return [
                review.get("text", None)
                for review in reviews
                if review.get("text", None)
            ]
        return None

    def to_str(self) -> str:
        # pydantic method to convert the model to a dict
        return self.model_dump_json()

    def to_dict(self) -> dict:
        return self.model_dump()


class GooglePlaceID(BaseModel):
    name: str | None
    id: str | None
    business_status: str | None


class Place(PlaceModel):
    full_description: str
    web_text: str | None
    summary_review: str | None

    @classmethod
    def get_place(cls, google_place: GooglePlace) -> "Place":
        google_place_data = google_place.model_dump()
        web_text = (
            cls.summary_web_text(google_place.website) if google_place.website else None
        )
        reviews = (
            cls.summary_reviews(google_place.reviews) if google_place.reviews else None
        )
        # Add the new fields to the dictionary
        google_place_data["web_text"] = web_text
        google_place_data["summary_review"] = reviews
        # get full description from overview, web_text and summary_review
        google_place_data["full_description"] = cls.get_full_description(
            google_place_data
        )
        return cls.model_validate(google_place_data)

    def summary_web_text(url: str) -> str:
        """Summary the web text, clean and extract relevant info"""
        # scrap url
        web_text = asyncio.run(scrap_url(url))
        prompt = CLEAN_WEB_TEXT.format(web_text=web_text)
        return llm.complete(prompt).text

    def summary_reviews(rewiew: List[str]) -> str:
        """Summary place reviews"""
        rewiew = " ".join(rewiew)
        prompt = SUMMARY_REVIEW.format(reviews=rewiew)
        return llm.complete(prompt).text

    def get_full_description(place: "Place") -> str:
        """
        Join from the avaiable fills the FULL description
        overview, web_text and summary_review
        """
        all_descriptions = [
            place.get("overview"),
            place.get("summary_review"),
            place.get("web_text"),
        ]
        return "\n".join([desc for desc in all_descriptions if desc])


async def scrap_url(url: str) -> str:
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=url,
        )
        return result.markdown
