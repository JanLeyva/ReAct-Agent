# internal libs
from src.services.load_restaurants.upload_place import GetUploadPlace
from src.services.search_engine.vector_store import VectorStore

# 3rd party
import polars as pl
from loguru import logger


if __name__ == "__main__":
    # Google Maps Client
    # gmaps_api = GoogleMapsAPI()
    vec = VectorStore()
    get_upload_place = GetUploadPlace()
    # Mock
    places_id = pl.read_parquet(
        "/Users/esengineer/Documents/_dev/whatsapp-agent/docs/data/filtered_data.parquet"
    )
    places_names = places_id["name"].to_list()
    # places_names = places_names[:2]
    [get_upload_place.get_upload_places_by_name(name) for name in places_names]
    # logger.info(places_names)
    # places_info = gmaps_api.get_places_bulk(places_names)
    # records = vec.process_data_for_vector_db(places_info)
    # logger.info("Upload Data to Database")
    # vec.upsert(records)
    # once we have upload data we can index db
    # logger.info("indexing Database")
    # vec.create_index()
    # vec.create_keyword_search_index()
