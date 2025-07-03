# 1st party
import time
from datetime import datetime
from typing import Any, List, Tuple, Union

# internal libs
from src.config import config
from src.services.search_engine.distance_coordinates import calculate_square_corners

# 3rd party
import vecs
import cohere
import time_uuid
import pandas as pd
import polars as pl
import numpy as np
import psycopg
from loguru import logger
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding


class VectorStore:
    """A class for managing vector operations and database interactions."""

    def __init__(self):
        """Initialize the VectorStore with settings, OpenAI client, and Timescale Vector client."""
        self.settings = config
        self.gclient_client = GoogleGenAIEmbedding(
            model_name="text-embedding-004",
            embed_batch_size=100,
            api_key=config.api_key_google_genai,
        )
        self.cohere_client = cohere.ClientV2(api_key=self.settings.cohere_api_key)
        self.vec_client = vecs.create_client(config.database_service_url)
        self.vx_db = self.vec_client.get_or_create_collection(
            name=config.table_name, dimension=config.embedding_dimensions
        )

    def create_keyword_search_index(self):
        """Create a GIN index for keyword search if it doesn't exist."""
        index_name = f"idx_{self.settings.table_name}_contents_gin"
        create_index_sql = f"""
        CREATE INDEX IF NOT EXISTS {index_name}
        ON {self.settings.table_name} USING gin(to_tsvector('english', contents));
        """
        try:
            with psycopg.connect(self.settings.database_service_url) as conn:
                with conn.cursor() as cur:
                    cur.execute(create_index_sql)
                    conn.commit()
                    logger.info(f"GIN index '{index_name}' created or already exists.")
        except Exception as e:
            logger.error(f"Error while creating GIN index: {str(e)}")

    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for the given text.

        Args:
            text: The input text to generate an embedding for.

        Returns:
            A list of floats representing the embedding.
        """
        text = text.replace("\n", " ")
        start_time = time.time()
        embedding = self.gclient_client.get_text_embedding(text)
        elapsed_time = time.time() - start_time
        logger.info(f"Embedding generated in {elapsed_time:.3f} seconds")
        return embedding

    def create_index(self) -> None:
        """Create the StreamingDiskANN index to spseed up similarity search"""
        self.vx_db.create_index(
            measure=vecs.IndexMeasure.cosine_distance
            # method=IndexMethod.hnsw,
            # index_arguments=IndexArgsHNSW(m=8),
        )

    def upsert(self, df: pl.DataFrame) -> None:
        """
        Insert or update records in the database from a pandas DataFrame.

        Args:
            df: A pandas DataFrame containing the data to insert or update.
                Expected columns: id, metadata, contents, embedding
        """
        # proper format to upload data to pgvector
        records = [
            (row["id"], np.array(row["embedding"]), row["metadata"])
            for row in df.iter_rows(named=True)
        ]
        self.vx_db.upsert(records)
        logger.info(f"Inserted {len(df)} records into {self.settings.table_name}")

    def semantic_search(
        self,
        query: str,
        limit: int = 3,
        metadata_filter: Union[dict, List[dict]] = None,
        formatted: bool = True,
    ) -> Union[List[Tuple[Any, ...]], pd.DataFrame]:
        """
        Query the vector database for similar embeddings based on input text.

        More info:
            https://github.com/timescale/docs/blob/latest/ai/python-interface-for-pgvector-and-timescale-vector.md

        Args:
            query: The input text to search for.
            limit: The maximum number of results to return.
            metadata_filter: A dictionary or list of dictionaries for equality-based metadata filtering.
            predicates: A Predicates object for complex metadata filtering.
                - Predicates objects are defined by the name of the metadata key, an operator, and a value.
                - Operators: ==, !=, >, >=, <, <=
                - & is used to combine multiple predicates with AND operator.
                - | is used to combine multiple predicates with OR operator.
            time_range: A tuple of (start_date, end_date) to filter results by time.
            formatted: Whether to return results as a formatted string (default: True).

        Returns:
            Either a list of tuples or a pandas DataFrame containing the search results or a formatted string with the results.

        Basic Examples:
            Basic search:
                vector_store.semantic_search("What are your shipping options?")
            Search with metadata filter:
                vector_store.semantic_search("Shipping options", metadata_filter={"category": "Shipping"})
        
        Predicates Examples:
            Search with predicates:
                vector_store.semantic_search("Pricing", predicates=client.Predicates("price", ">", 100))
            Search with complex combined predicates:
                complex_pred = (client.Predicates("category", "==", "Electronics") & client.Predicates("price", "<", 1000)) | \
                               (client.Predicates("category", "==", "Books") & client.Predicates("rating", ">=", 4.5))
                vector_store.semantic_search("High-quality products", predicates=complex_pred)
        
        Time-based filtering:
            Search with time range:
                vector_store.semantic_search("Recent updates", time_range=(datetime(2024, 1, 1), datetime(2024, 1, 31)))
        """
        query_embedding = self.get_embedding(query)

        start_time = time.time()

        search_args = {
            "limit": limit,
            "measure": "cosine_distance",  # distance measure to use
            "include_value": False,  # should distance measure values be returned?
            "include_metadata": True,  # should record metadata be returned?
        }

        if metadata_filter:
            search_args["filters"] = metadata_filter

        results = self.vx_db.query(query_embedding, **search_args)
        elapsed_time = time.time() - start_time

        self._log_search_time("Vector", elapsed_time)

        if not results:
            # raise NoResultsFoundInVectorDB("No results for the search with metadata (coordinates).")
            return "No Results where found for your localization"

        pl_results = self._create_dataframe_from_results(results)
        if formatted:
            return self._format_result_str(pl_results)

        return pl_results

    def semantic_search_with_filter(
        self,
        query: str,
        lat: float,
        long: float,
        side: int = 1000,
        limit: int = 5,
        formatted: bool = True,
    ):
        """
        Query the vector database for similar embeddings based on input text and coordinates (long, lat).

        Args:
            query: The input text to search for.
            long: The longitude coordinate.
            lat: The latitude coordinate.
            side: The square longitude around the point.
            limit: The maximum number of results to return.
            formatted: Whether to return results as a formatted string (default: True).

        Returns:
            Either a polars DataFrame containing the search results or a formatted string with the results.
        """
        # calculate the square around a point
        coordinates_right, coordinates_left = calculate_square_corners(
            latitude=lat, longitude=long, side=side
        )
        metadata_filter = {
            "$and": [
                {"lat": {"$lte": coordinates_right[0]}},
                {"long": {"$lte": coordinates_right[1]}},
                {"lat": {"$gte": coordinates_left[0]}},
                {"long": {"$gte": coordinates_left[1]}},
            ]
        }

        results = self.semantic_search(
            query, metadata_filter=metadata_filter, limit=limit, formatted=False
        )

        if formatted and isinstance(results, pl.DataFrame):
            return self._format_result_str(results)
        return results

    def _create_dataframe_from_results(
        self,
        results: List[Tuple[Any, ...]],
    ) -> pl.DataFrame:
        """
        Create a pandas DataFrame from the search results.

        Args:
            results: A list of tuples containing the search results.

        Returns:
            A pandas DataFrame containing the formatted search results.
        """
        # Convert results to DataFrame
        df = pl.DataFrame(results, schema={"id": str, "metadata": None})
        # actually metadata is a pl -> struct[12]

        # Expand metadata column
        df = df.unnest("metadata")

        return df

    def _format_result_str(self, results: pl.DataFrame) -> str:
        """
        Format the search results into a string for display.

        Args:
            results: A list of tuples containing the search results.

        Returns:
            A formatted string representation of the search results.
        """

        def _fill_template(
            idx, place: pl.Series
        ) -> str:  # <--- Type hint here is pl.Series
            """fill the output template of the agent"""
            template = f"{idx+1}: <b>{place['name']}</b>: {place['contents']}\n"  # <--- Accessing as if it's a dict or Series with string index
            template += (
                f"<a href='{place['website']}'>website</a> | "
                if place["website"] is not None
                else ""
            )
            template += (
                f"<a href='{place['url']}'>maps</a> | "
                if place["url"] is not None
                else ""
            )
            template += (
                f"{place['international_phone_number']}"
                if place["international_phone_number"] is not None
                else ""
            )

            return template

        result_formatted = [
            _fill_template(idx, place)
            for idx, place in enumerate(
                results.iter_rows(named=True)
            )  # <--- This yields dictionaries
        ]

        return "".join(result_formatted)

    def delete(
        self,
        ids: List[str] = None,
        metadata_filter: dict = None,
        delete_all: bool = False,
    ) -> None:
        """Delete records from the vector database.

        Args:
            ids (List[str], optional): A list of record IDs to delete.
            metadata_filter (dict, optional): A dictionary of metadata key-value pairs to filter records for deletion.
            delete_all (bool, optional): A boolean flag to delete all records.

        Raises:
            ValueError: If no deletion criteria are provided or if multiple criteria are provided.

        Examples:
            Delete by IDs:
                vector_store.delete(ids=["8ab544ae-766a-11ef-81cb-decf757b836d"])

            Delete by metadata filter:
                vector_store.delete(metadata_filter={"category": "Shipping"})

            Delete all records:
                vector_store.delete(delete_all=True)
        """
        if sum(bool(x) for x in (ids, metadata_filter, delete_all)) != 1:
            raise ValueError(
                "Provide exactly one of: ids, metadata_filter, or delete_all"
            )

        if delete_all:
            self.vec_client.delete_all()
            logger.info(f"Deleted all records from {self.vector_settings.table_name}")
        elif ids:
            self.vec_client.delete_by_ids(ids)
            logger.info(
                f"Deleted {len(ids)} records from {self.vector_settings.table_name}"
            )
        elif metadata_filter:
            self.vec_client.delete_by_metadata(metadata_filter)
            logger.info(
                f"Deleted records matching metadata filter from {self.vector_settings.table_name}"
            )

    def _log_search_time(self, search_type: str, elapsed_time: float) -> None:
        """
        Log the time taken for a search operation.

        Args:
            search_type: The type of search performed (e.g., 'Vector', 'Keyword').
            elapsed_time: The time taken for the search operation in seconds.
        """
        logger.info(f"{search_type} search completed in {elapsed_time:.3f} seconds")

    def keyword_search(
        self, query: str, limit: int = 5, return_dataframe: bool = True
    ) -> Union[List[Tuple[str, str, float]], pd.DataFrame]:
        """
        Perform a keyword search on the contents of the vector store.

        Args:
            query: The search query string.
            limit: The maximum number of results to return. Defaults to 5.
            return_dataframe: Whether to return results as a DataFrame. Defaults to True.

        Returns:
            Either a list of tuples (id, contents, rank) or a pandas DataFrame containing the search results.

        Example:
            results = vector_store.keyword_search("shipping options")
        """
        search_sql = f"""
        SELECT id, contents, ts_rank_cd(to_tsvector('english', contents), query) as rank
        FROM {self.settings.table_name}, websearch_to_tsquery('english', %s) query
        WHERE to_tsvector('english', contents) @@ query
        ORDER BY rank DESC
        LIMIT %s
        """

        start_time = time.time()

        # Create a new connection using psycopg3
        with psycopg.connect(self.settings.database_service_url) as conn:
            with conn.cursor() as cur:
                cur.execute(search_sql, (query, limit))
                results = cur.fetchall()

        elapsed_time = time.time() - start_time
        self._log_search_time("Keyword", elapsed_time)

        if return_dataframe:
            df = pd.DataFrame(results, columns=["id", "contents", "rank"])
            df["id"] = df["id"].astype(str)
            return df
        return results

    def hybrid_search(
        self,
        query: str,
        keyword_k: int = 5,
        semantic_k: int = 5,
        rerank: bool = False,
        top_n: int = 5,
    ) -> pl.DataFrame:
        """
        Perform a hybrid search combining keyword and semantic search results,
        with optional reranking using Cohere.

        Args:
            query: The search query string.
            keyword_k: The number of results to return from keyword search. Defaults to 5.
            semantic_k: The number of results to return from semantic search. Defaults to 5.
            rerank: Whether to apply Cohere reranking. Defaults to True.
            top_n: The number of top results to return after reranking. Defaults to 5.

        Returns:
            A polars DataFrame containing the combined search results with a 'search_type' column.

        Example:
            results = vector_store.hybrid_search("shipping options", keyword_k=3, semantic_k=3, rerank=True, top_n=5)
        """
        # Perform keyword search
        keyword_results = self.keyword_search(
            query, limit=keyword_k, return_dataframe=True
        )
        keyword_results["search_type"] = "keyword"
        keyword_results = keyword_results[["id", "contents", "search_type"]]

        # Perform semantic search
        semantic_results = self.semantic_search(
            query, limit=semantic_k, return_dataframe=True
        )
        semantic_results["search_type"] = "semantic"
        semantic_results = semantic_results[["id", "contents", "search_type"]]

        # Combine results
        combined_results = pd.concat(
            [keyword_results, semantic_results], ignore_index=True
        )

        # Remove duplicates, keeping the first occurrence (which maintains the original order)
        combined_results = combined_results.drop_duplicates(subset=["id"], keep="first")

        if rerank:
            return self._rerank_results(query, combined_results, top_n)

        return combined_results

    def _rerank_results(
        self, query: str, combined_results: pd.DataFrame, top_n: int
    ) -> pd.DataFrame:
        """
        Rerank the combined search results using Cohere.

        Args:
            query: The original search query.
            combined_results: DataFrame containing the combined keyword and semantic search results.
            top_n: The number of top results to return after reranking.

        Returns:
            A pandas DataFrame containing the reranked results.
        """
        rerank_results = self.cohere_client.v2.rerank(
            model="rerank-english-v3.0",
            query=query,
            documents=combined_results["contents"].tolist(),
            top_n=top_n,
            return_documents=True,
        )

        reranked_df = pd.DataFrame(
            [
                {
                    "id": combined_results.iloc[result.index]["id"],
                    "contents": result.document,
                    "search_type": combined_results.iloc[result.index]["search_type"],
                    "relevance_score": result.relevance_score,
                }
                for result in rerank_results.results
            ]
        )

        return reranked_df.sort_values("relevance_score", ascending=False)

    def process_data_for_vector_db(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Transforms the input DataFrame rows into a structured format suitable for a vector database.

        Args:
            df: The input Polars DataFrame containing restaurant data.

        Returns:
            A Polars DataFrame with a single column of type Struct,
            where each row is a dictionary containing 'id', 'metadata', 'contents', and 'embedding'.
        """

        # Ensure 'description' is Utf8 and handle potential None values
        # by filling them with an empty string for embedding generation.
        # This prevents map_elements from failing on None.
        df_processed = df.with_columns(
            pl.col("description")
            .cast(pl.Utf8)
            .fill_null("")
            .alias("description_for_embedding")
        )
        # 1. Generate 'embedding' column using map_elements
        #    This is necessary because self.get_embedding is a Python function.
        df_processed = df_processed.with_columns(
            pl.col("description_for_embedding")
            .map_elements(
                lambda content: self.get_embedding(content),
                return_dtype=pl.List(
                    pl.Float32
                ),  # Crucial for performance and type inference
            )
            .alias("embedding")
        )
        # 2. Generate 'id' column using map_elements (or simpler series creation)
        #    We generate a UUID for each row.
        df_processed = df_processed.with_columns(
            pl.Series(
                name="id",
                values=[
                    str(time_uuid.TimeUUID.with_timestamp(time_uuid.utctime()))
                    for _ in range(df.height)
                ],
                dtype=pl.Utf8,  # UUIDs are strings
            )
        )

        metadata_struct = pl.struct(
            [
                pl.lit(datetime.now().isoformat()).alias("created_at"),  # Literal value
                pl.col("name").alias("name"),
                pl.col("url").alias("url"),
                pl.col("description").alias("contents"),
                pl.col("web_text").alias("web_text"),
                pl.col("summary_review").alias("summary_review"),
                pl.col("international_phone_number").alias(
                    "international_phone_number"
                ),
                pl.col("formatted_address").alias("formatted_address"),
                pl.col("website").alias("website"),
                pl.col("geometry").list.get(0).alias("long"),
                pl.col("geometry").list.get(1).alias("lat"),
                pl.col("price_level").alias("price_level"),
            ]
        ).alias("metadata")

        # Select only the newly constructed column
        return df_processed.with_columns(
            [pl.col("id"), pl.col("embedding"), metadata_struct]
        ).select(["id", "embedding", "metadata"])
