"""Base connector interface for vector databases."""

from abc import ABC, abstractmethod
from typing import List
from vecta.core.schemas import ChunkData, VectorDBSchema
from typing import Any


class BaseVectorDBConnector(ABC):
    """Abstract base class for vector database connectors."""

    def __init__(self, schema: VectorDBSchema):
        """
        Initialize the connector with database schema configuration.

        Args:
            schema: Schema defining how to extract data from this database (REQUIRED)
        """
        if schema is None:
            raise ValueError("Schema is required for all vector database connectors")
        self.schema = schema

    @abstractmethod
    def get_all_chunks(self) -> List[ChunkData]:
        """
        Retrieve all chunks and their metadata from the vector database.

        Returns:
            List of ChunkData objects containing id, content, and metadata.
        """
        pass

    @abstractmethod
    def semantic_search(self, query_str: str, k: int = 10) -> List[ChunkData]:
        """
        Perform similarity search to find top-k most similar chunks.

        Args:
            query_str: The text query to search with
            k: Number of top similar chunks to return

        Returns:
            List of ChunkData objects ranked by similarity
        """
        pass

    @abstractmethod
    def get_chunk_by_id(self, chunk_id: str) -> ChunkData:
        """
        Retrieve a specific chunk by its ID.

        Args:
            chunk_id: The unique identifier for the chunk

        Returns:
            ChunkData object for the specified chunk
        """
        pass

    def _create_chunk_data_from_raw(self, raw_result: Any) -> ChunkData:
        """
        Helper method to create ChunkData from raw database result using schema.

        Args:
            raw_result: Raw result from database query

        Returns:
            ChunkData object with extracted information
        """
        return ChunkData.from_schema_extraction(self.schema, raw_result)
