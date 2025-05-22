
from http.client import HTTPException
from src.config import config
from src.services.load_restaurants.place import GooglePlaceID, Place
from src.services.load_restaurants.googlemaps_api import GoogleMapsAPI
from src.services.search_engine.vector_store import VectorStore
# 3rd party
import googlemaps
from loguru import logger

class UploadPlace:
    def __init__(self):
        # Google Maps Client
        gmaps_client = googlemaps.Client(key=config.googlemaps_api_key)
        self.gmaps_api = GoogleMapsAPI(gmaps_client)
        self.vec = VectorStore()

    def upload_places_by_name(self, place_name: str) -> None:
        try:
            place_id = self.gmaps_api.get_place_id(place_name)
            logger.info(f"Upload place: {place_id}")
            places_info = self.gmaps_api.get_place_info(place_id)
            place_full = Place.get_place_df(places_info)
            records = self.vec.prepare_record(place_full)
            self.vec.upsert(records)
        except Exception as e:
            logger.error(f"Error uploading place {place_name}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to upload place: {e}")

    def upload_places_by_id(self, place_id: GooglePlaceID) -> None:
        try:
            places_info = self.gmaps_api.get_place_info(place_id)
            logger.info(f"Upload place: {places_info}")
            place_full = Place.get_place_df(places_info)
            records = self.vec.prepare_record(place_full)
            self.vec.upsert(records)
        except Exception as e:
            logger.error(f"Error uploading place {place_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to upload place: {e}")
