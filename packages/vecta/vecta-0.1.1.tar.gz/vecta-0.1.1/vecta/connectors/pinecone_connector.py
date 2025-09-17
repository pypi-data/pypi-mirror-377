"""Pinecone connector implementation."""

import os
from typing import List, Dict, Any, Optional, cast
from pinecone import Pinecone
from pinecone.core.openapi.db_data.models import QueryResponse
from vecta.connectors.base import BaseVectorDBConnector
from vecta.core.schemas import ChunkData, VectorDBSchema


class PineconeConnector(BaseVectorDBConnector):
    """Connector for Pinecone vector database."""

    def __init__(
        self,
        index_name: str,
        namespace: str = "",
        api_key: str | None = os.getenv("PINECONE_API_KEY"),
        openai_api_key: Optional[str] = None,
        embedding_model: str = "text-embedding-3-small",
        schema: Optional[VectorDBSchema] = None,
    ):
        """
        Initialize Pinecone connector.

        Args:
            api_key: Pinecone API key
            index_name: Name of the Pinecone index
            namespace: Pinecone namespace (optional)
            openai_api_key: OpenAI API key for embeddings (optional)
            embedding_model: OpenAI embedding model to use
            schema: Schema for data extraction (REQUIRED - no default provided)
        """
        if not api_key:
            raise ValueError(
                "Pinecone API key is required. Provide api_key parameter or set PINECONE_API_KEY environment variable."
            )

        if schema is None:
            raise ValueError(
                "Schema is required for Pinecone connector. The data structure varies too much to provide a reliable default."
            )

        super().__init__(schema)
        self.api_key = api_key
        self.index_name = index_name
        self.namespace = namespace
        self.embedding_model = embedding_model

        try:
            # Initialize Pinecone client
            self.pc = Pinecone(api_key=api_key)
            self.index = self.pc.Index(index_name)
        except Exception as e:
            raise ValueError(f"Could not connect to Pinecone index '{index_name}': {e}")

        # Initialize OpenAI client for embeddings if provided
        self.openai_client = None
        openai_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                from openai import OpenAI

                self.openai_client = OpenAI(api_key=openai_key)
            except ImportError:
                raise ImportError(
                    "OpenAI package required for embedding generation. Install with: pip install openai"
                )

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI."""
        if not self.openai_client:
            raise ValueError(
                "OpenAI API key required for embedding generation. "
                "Provide openai_api_key parameter or set OPENAI_API_KEY environment variable."
            )

        try:
            response = self.openai_client.embeddings.create(
                input=text.replace("\n", " "), model=self.embedding_model
            )
            return response.data[0].embedding
        except Exception as e:
            raise RuntimeError(f"Failed to generate embedding: {e}")

    def get_all_chunks(self) -> List[ChunkData]:
        """
        Retrieve all chunks from Pinecone index.

        Note: This operation is not efficient with Pinecone as it doesn't support
        direct "get all" operations. This implementation uses query with a dummy vector
        which may not return all vectors for large datasets.

        For production use, consider maintaining chunk IDs externally or using
        alternative approaches for bulk data loading.
        """
        try:
            # Get index stats to understand the data size
            stats = self.index.describe_index_stats()

            # Check if namespace exists and has data
            namespace_stats = (
                stats.namespaces.get(self.namespace, None) if self.namespace else None
            )
            total_count = (
                namespace_stats.vector_count
                if namespace_stats
                else stats.total_vector_count
            )

            if total_count == 0:
                return []

            # For large datasets, warn about inefficiency
            if total_count > 10000:
                raise NotImplementedError(
                    f"Index contains {total_count} vectors. Pinecone doesn't support "
                    "efficient retrieval of large datasets. Consider a custom Vecta connector "
                    "using query operations instead."
                )

            # Get index dimension for dummy query
            index_info = self.pc.describe_index(self.index_name)
            dimension = index_info.dimension

            # Use a dummy vector query to get results
            dummy_vector = [0.0] * dimension

            # Query with high top_k to get as many results as possible
            # Explicitly set async_req=False to ensure we get QueryResponse
            results = cast(
                QueryResponse,
                self.index.query(
                    vector=dummy_vector,
                    top_k=min(total_count, 10000),  # Pinecone's max limit per query
                    namespace=self.namespace,
                    include_metadata=True,
                    async_req=False,  # Explicitly set to False
                ),
            )

            chunks = []
            for match in results.matches:
                chunk_data = self._create_chunk_data_from_raw(match)
                chunks.append(chunk_data)

            return chunks

        except Exception as e:
            raise RuntimeError(f"Failed to retrieve all chunks: {e}")

    def semantic_search(self, query_str: str, k: int = 10) -> List[ChunkData]:
        """Perform similarity search using query string."""
        try:
            # Convert query to embedding
            query_vector = self._get_embedding(query_str)

            # Query Pinecone
            # Explicitly set async_req=False to ensure we get QueryResponse
            results = cast(
                QueryResponse,
                self.index.query(
                    vector=query_vector,
                    top_k=k,
                    namespace=self.namespace,
                    include_metadata=True,
                    async_req=False,  # Explicitly set to False
                ),
            )

            chunks = []
            for match in results.matches:
                chunk_data = self._create_chunk_data_from_raw(match)
                chunks.append(chunk_data)

            return chunks

        except Exception as e:
            raise RuntimeError(f"Similarity search failed: {e}")

    def get_chunk_by_id(self, chunk_id: str) -> ChunkData:
        """Retrieve a specific chunk by ID."""
        try:
            results = self.index.fetch(ids=[chunk_id], namespace=self.namespace)

            if chunk_id not in results.vectors:
                raise ValueError(f"Chunk with ID '{chunk_id}' not found")

            vector_data = results.vectors[chunk_id]

            # Use the vector data directly as raw result
            return self._create_chunk_data_from_raw(vector_data)

        except Exception as e:
            raise RuntimeError(f"Failed to retrieve chunk '{chunk_id}': {e}")
