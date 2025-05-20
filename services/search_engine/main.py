from datetime import datetime

# internal lib
from src.database.vector_store import VectorStore

# 3rd party
import pandas as pd
from loguru import logger
from timescale_vector.client import Predicates, uuid_from_time

# Initialize VectorStore
vec = VectorStore()


def prepare_record(row):
    """Prepare a record for insertion into the vector store.

    Args:
        row (pandas.Series): A row from the dataset containing an 'article' column.

    Returns:
        pandas.Series: A series containing the prepared record for insertion.

    Note:
        This function uses the current time for the UUID. To use a specific time,
        create a datetime object and use uuid_from_time(your_datetime).
    """
    content = row["overview"]
    if content:
        embedding = vec.get_embedding(content)
        # TODO check if we can insert dif data types
        return pd.Series(
            {
                "id": str(uuid_from_time(datetime.now())),
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "place_id": row["place_id"],
                    "name": row["name"],
                    "url": row["url"],
                    "international_phone_number": row["international_phone_number"],
                    "formatted_address": row["formatted_address"],
                    "website": row["website"],
                    "long": row["geometry"][0],
                    "lat": row["geometry"][1],
                    "price_level": row["price_level"],
                    "reservable": row["reservable"],
                    "delivery": row["delivery"],
                    "dine_in": row["dine_in"],
                    "wheelchair_accessible_entrance": row[
                        "wheelchair_accessible_entrance"
                    ],
                    "serves_breakfast": row["serves_breakfast"],
                    "serves_brunch": row["serves_brunch"],
                    "takeout": row["takeout"],
                },
                "contents": content,
                "embedding": embedding,
            }
        )
    return None


def main():
    # read data
    data = pd.read_parquet(
        "/Users/esengineer/Documents/_dev/whatsapp-agent/docs/data/filtered_data.parquet"
    )
    data = data[~data["overview"].isnull()][:5].reset_index(drop=True)
    # create vector df
    records = data.apply(prepare_record, axis=1)
    vec.create_tables()
    vec.create_index()  # DiskAnnIndex
    vec.create_keyword_search_index()  # GIN Index
    vec.upsert(records)
    breakpoint()
    # Search - example
    metadata_filter = Predicates(
        Predicates(("lat", "<=", 3.2)), Predicates(("long", ">=", 2.1))
    )
    results = vec.semantic_search("burguers", predicates=metadata_filter)
    logger.info(results)


if __name__ == "__main__":
    main()
