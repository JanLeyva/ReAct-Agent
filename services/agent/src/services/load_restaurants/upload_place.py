from http.client import HTTPException

# internal libs
from src.services.load_restaurants.place import GooglePlaceID, Place
from src.services.load_restaurants.googlemaps_api import GoogleMapsAPI
from src.services.search_engine.vector_store import VectorStore

# 3rd party
from loguru import logger


class GetUploadPlace:
    def __init__(self):
        # Google Maps Client
        self.gmaps_api = GoogleMapsAPI()
        self.vec = VectorStore()

    def get_upload_places_by_name(self, place_name: str) -> None:
        """Get places from GoogleMaps API
        1. Get place ID from name
        2. Get place information from ID
        3. Refine place information with web scap, summary descriptions
        4. Upload to database

        Input: (str) of the place name.
        """
        try:
            place_id = self.gmaps_api.get_place_id(place_name)
            self._get_upload_places_by_id(place_id)
        except Exception as e:
            logger.error(f"Error uploading place {place_name}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to upload place: {e}")

    def _get_upload_places_by_id(self, place_id: GooglePlaceID) -> None:
        """Get places from GoogleMaps API
        1. Get place information from ID
        2. Refine place information with web scap, summary descriptions
        3. Upload to database

        Input: (GooglePlaceID) of the place.
        """
        try:
            place_info = self.gmaps_api.get_place_from_id(place_id)
            place_complet = Place.get_place(place_info)
            records = self.vec.process_data_for_vector_db(place_complet.to_df())
            logger.info("Upload record to db")
            self.vec.upsert(records)
        except Exception as e:
            logger.error(f"Error uploading place {place_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to upload place: {e}")
