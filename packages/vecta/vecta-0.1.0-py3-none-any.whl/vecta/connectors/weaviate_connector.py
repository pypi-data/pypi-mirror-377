"""Weaviate connector implementation."""

from typing import List, Dict, Any, Optional, cast
import json
import os

import weaviate  # type: ignore[import-untyped]
from weaviate.classes.init import Auth  # type: ignore[import-untyped]
from weaviate.classes.query import MetadataQuery  # type: ignore[import-untyped]
from weaviate.client import WeaviateClient  # type: ignore[import-untyped]

from vecta.connectors.base import BaseVectorDBConnector
from vecta.core.schemas import ChunkData, VectorDBSchema


class WeaviateConnector(BaseVectorDBConnector):
    """
    Connector for Weaviate vector database.

    Supports both Weaviate Cloud and local instances.
    """

    def __init__(
        self,
        collection_name: str,
        schema: VectorDBSchema,
        cluster_url: Optional[str] = None,
        api_key: Optional[str] = None,
        # For local Weaviate instances
        host: str = "localhost",
        port: int = 8080,
        grpc_port: int = 50051,
        use_cloud: bool = True,
        # Additional configuration
        headers: Optional[Dict[str, str]] = None,
        tenant: Optional[str] = None,
        # Pagination settings
        batch_size: int = 100,
    ):
        """
        Initialize Weaviate connector.

        Args:
            collection_name: Name of the Weaviate collection to use
            schema: Schema for data extraction (REQUIRED)
            cluster_url: Weaviate Cloud cluster URL (required for cloud)
            api_key: Weaviate API key (required for cloud)
            host: Host for local Weaviate instance
            port: Port for local Weaviate instance
            grpc_port: gRPC port for local Weaviate instance
            use_cloud: Whether to connect to Weaviate Cloud or local instance
            headers: Additional headers for third-party API keys (e.g., OpenAI, Cohere)
            tenant: Tenant name for multi-tenant collections
            batch_size: Number of objects to fetch per batch for pagination
        """
        super().__init__(schema)
        self.collection_name = collection_name
        self.tenant = tenant
        self.batch_size = batch_size

        try:
            if use_cloud:
                if not cluster_url or not api_key:
                    # Try to get from environment
                    cluster_url = cluster_url or os.environ.get("WEAVIATE_URL")
                    api_key = api_key or os.environ.get("WEAVIATE_API_KEY")

                    if not cluster_url or not api_key:
                        raise ValueError(
                            "Weaviate Cloud requires cluster_url and api_key. "
                            "Provide them directly or set WEAVIATE_URL and WEAVIATE_API_KEY environment variables."
                        )

                # Connect to Weaviate Cloud
                self.client = weaviate.connect_to_weaviate_cloud(
                    cluster_url=cluster_url,
                    auth_credentials=Auth.api_key(api_key),
                    headers=headers,
                )
            else:
                # Connect to local Weaviate instance
                self.client = weaviate.connect_to_local(
                    host=host,
                    port=port,
                    grpc_port=grpc_port,
                    headers=headers,
                )

            # Check if client is ready
            if not self.client.is_ready():
                raise ValueError("Weaviate client is not ready")

            # Get the collection
            self.collection = self.client.collections.get(collection_name)

            # Configure for multi-tenancy if specified
            if self.tenant:
                self.collection = self.collection.with_tenant(self.tenant)

        except Exception as e:
            raise ValueError(
                f"Could not connect to Weaviate or access collection '{collection_name}': {e}"
            )

    def __del__(self):
        """Close the Weaviate client connection."""
        try:
            if hasattr(self, "client"):
                self.client.close()
        except Exception:
            pass  # Ignore errors during cleanup

    def close(self):
        """Explicitly close the Weaviate client connection."""
        try:
            self.client.close()
        except Exception:
            pass

    def get_all_chunks(self) -> List[ChunkData]:
        """
        Retrieve all chunks from the Weaviate collection.

        Uses pagination to handle large collections efficiently.

        Returns:
            List of ChunkData objects with all chunks from the collection.
        """
        try:
            chunks: List[ChunkData] = []
            offset = 0

            while True:
                response = self.collection.query.fetch_objects(
                    limit=self.batch_size,
                    offset=offset,
                )

                if not response.objects:
                    break

                for obj in response.objects:
                    chunk_data = self._create_chunk_data_from_raw(obj)
                    chunks.append(chunk_data)

                # If we got fewer objects than the batch size, we've reached the end
                if len(response.objects) < self.batch_size:
                    break

                offset += self.batch_size

            return chunks

        except Exception as e:
            raise RuntimeError(f"Failed to retrieve all chunks: {e}")

    def semantic_search(self, query_str: str, k: int = 10) -> List[ChunkData]:
        """
        Perform similarity search using query string.

        Uses Weaviate's near_text operator to find semantically similar chunks.

        Args:
            query_str: Text query to search with
            k: Number of top results to return

        Returns:
            List of most similar ChunkData objects ranked by similarity
        """
        try:
            response = self.collection.query.near_text(
                query=query_str,
                limit=k,
                return_metadata=MetadataQuery(distance=True),
            )

            chunks: List[ChunkData] = []
            for obj in response.objects:
                chunk_data = self._create_chunk_data_from_raw(obj)

                # Add distance/score to metadata if available
                if (
                    hasattr(obj.metadata, "distance")
                    and obj.metadata.distance is not None
                ):
                    chunk_data.metadata["score"] = float(obj.metadata.distance)

                chunks.append(chunk_data)

            return chunks

        except Exception as e:
            raise RuntimeError(f"Similarity search failed: {e}")

    def get_chunk_by_id(self, chunk_id: str) -> ChunkData:
        """
        Retrieve a specific chunk by its UUID.

        Args:
            chunk_id: The chunk UUID (Weaviate object identifier)

        Returns:
            ChunkData object for the specified chunk

        Raises:
            ValueError: If chunk is not found
            RuntimeError: If retrieval fails for other reasons
        """
        try:
            # Weaviate uses UUIDs as object identifiers
            obj = self.collection.query.fetch_object_by_id(uuid=chunk_id)

            if obj is None:
                raise ValueError(f"Chunk with ID '{chunk_id}' not found")

            return self._create_chunk_data_from_raw(obj)

        except Exception as e:
            if "not found" in str(e).lower() or "does not exist" in str(e).lower():
                raise ValueError(f"Chunk with ID '{chunk_id}' not found")
            raise RuntimeError(f"Failed to retrieve chunk '{chunk_id}': {e}")

    def semantic_search_vector(
        self,
        query_vector: List[float],
        k: int = 10,
        target_vector: Optional[str] = None,
    ) -> List[ChunkData]:
        """
        Perform similarity search using a pre-computed vector.

        Args:
            query_vector: Pre-computed embedding vector
            k: Number of top results to return
            target_vector: Name of target vector for multi-vector collections

        Returns:
            List of most similar ChunkData objects
        """
        try:
            response = self.collection.query.near_vector(
                near_vector=query_vector,
                limit=k,
                target_vector=target_vector,
                return_metadata=MetadataQuery(distance=True),
            )

            chunks: List[ChunkData] = []
            for obj in response.objects:
                chunk_data = self._create_chunk_data_from_raw(obj)

                # Add distance/score to metadata if available
                if (
                    hasattr(obj.metadata, "distance")
                    and obj.metadata.distance is not None
                ):
                    chunk_data.metadata["score"] = float(obj.metadata.distance)

                chunks.append(chunk_data)

            return chunks

        except Exception as e:
            raise RuntimeError(f"Vector similarity search failed: {e}")
