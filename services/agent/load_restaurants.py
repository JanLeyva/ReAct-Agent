# internal libs
from src.services.load_restaurants.googlemaps_api import GoogleMapsAPI
from src.services.search_engine.vector_store import VectorStore

# 3rd party
import polars as pl
from loguru import logger


if __name__ == "__main__":
    # Google Maps Client
    gmaps_api = GoogleMapsAPI()
    vec = VectorStore()
    # vec.create_tables()
    # vec.create_index()  # DiskAnnIndex
    # vec.create_keyword_search_index()  # GIN Index
    # logger.info("created db")
    # Mock
    places_id = pl.read_parquet(
        "/Users/janleyvamassague/Documents/agnostic-agent/docs/data/filtered_data.parquet"
    )
    places_names = places_id["name"].to_list()
    places_names = places_names[:2]
    logger.info(places_names)
    places_info = gmaps_api.get_places_bulk(places_names)
    logger.info(places_info)
    records = vec.process_data_for_vector_db(places_info)
    vec.upsert(records)
