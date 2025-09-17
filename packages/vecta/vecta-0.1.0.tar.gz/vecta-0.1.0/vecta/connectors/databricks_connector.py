"""Databricks Vector Search connector implementation."""

from typing import List, Dict, Any, Optional, cast
import json

from vecta.connectors.base import BaseVectorDBConnector
from vecta.core.schemas import ChunkData, VectorDBSchema
from databricks.vector_search.client import VectorSearchClient  # type: ignore[import-untyped]
from databricks.vector_search.index import VectorSearchIndex  # type: ignore[import-untyped]


class DatabricksConnector(BaseVectorDBConnector):
    """Connector for Databricks Vector Search."""

    def __init__(
        self,
        workspace_url: str,
        index_name: str,
        schema: VectorDBSchema,
        endpoint_name: Optional[str] = None,
        personal_access_token: Optional[str] = None,
        service_principal_client_id: Optional[str] = None,
        service_principal_client_secret: Optional[str] = None,
        azure_tenant_id: Optional[str] = None,
        azure_login_id: str = "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d",
        openai_api_key: Optional[str] = None,
        embedding_model: str = "text-embedding-3-small",
    ):
        """
        Initialize Databricks Vector Search connector.

        Args:
            workspace_url: The URL of the Databricks workspace
            index_name: Name of the vector search index
            schema: Schema for data extraction (REQUIRED)
            endpoint_name: Name of the vector search endpoint (optional for some operations)
            personal_access_token: Personal access token for authentication
            service_principal_client_id: Service principal client ID for authentication
            service_principal_client_secret: Service principal client secret for authentication
            azure_tenant_id: Azure tenant ID for Azure authentication
            azure_login_id: Azure login ID (Databricks Azure Application ID)
            openai_api_key: OpenAI API key for text embeddings (optional)
            embedding_model: OpenAI embedding model to use for text queries
        """
        super().__init__(schema)
        self.workspace_url = workspace_url
        self.index_name = index_name
        self.endpoint_name = endpoint_name
        self.embedding_model = embedding_model

        try:
            # Initialize Databricks Vector Search client
            self.client = VectorSearchClient(
                workspace_url=workspace_url,
                personal_access_token=personal_access_token,
                service_principal_client_id=service_principal_client_id,
                service_principal_client_secret=service_principal_client_secret,
                azure_tenant_id=azure_tenant_id,
                azure_login_id=azure_login_id,
            )

            # Get the vector search index
            self.index: VectorSearchIndex = self.client.get_index(
                endpoint_name=endpoint_name, index_name=index_name
            )

        except Exception as e:
            raise ValueError(
                f"Could not connect to Databricks Vector Search index '{index_name}': {e}"
            )

        # Initialize OpenAI client for embeddings if provided
        self.openai_client = None
        if openai_api_key:
            try:
                from openai import OpenAI

                self.openai_client = OpenAI(api_key=openai_api_key)
            except ImportError:
                raise ImportError(
                    "OpenAI package required for embedding generation. Install with: pip install openai"
                )

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI."""
        if not self.openai_client:
            raise ValueError(
                "OpenAI API key required for embedding generation. "
                "Provide openai_api_key parameter."
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
        Retrieve all chunks from the Databricks Vector Search index.

        Note: This operation may not be efficient for very large indexes.
        Consider implementing pagination or filtering for production use.
        """
        try:
            # Use a large limit to get as many results as possible
            # This is a limitation of vector search - there's no direct "get all" method
            results = self.index.similarity_search(
                query_vector=[0.0]
                * 1536,  # Dummy vector - this may need adjustment based on your embedding dimension
                columns=["*"],  # Get all columns
                num_results=10000,  # Adjust based on your index size
            )

            chunks = []
            if "result" in results and "data_array" in results["result"]:
                for row in results["result"]["data_array"]:
                    chunk_data = self._create_chunk_data_from_raw(row)
                    chunks.append(chunk_data)

            return chunks

        except Exception as e:
            # Fallback: if similarity_search doesn't work, try alternative approaches
            raise NotImplementedError(
                f"Could not retrieve all chunks from Databricks index. "
                f"This may be due to index configuration or API limitations: {e}"
            )

    def semantic_search(self, query_str: str, k: int = 10) -> List[ChunkData]:
        """
        Perform similarity search using query string.

        Args:
            query_str: Text query to search with
            k: Number of top results to return

        Returns:
            List of most similar ChunkData objects
        """
        try:
            # For indexes with embedding model endpoints, we can pass text directly
            # For other indexes, we need to convert text to embedding first
            results = None

            # Try text query first (for indexes with embedding model endpoints)
            try:
                results = self.index.similarity_search(
                    query_text=query_str,
                    columns=["*"],
                    num_results=k,
                )
            except Exception:
                # Fallback: convert text to embedding and search with vector
                if self.openai_client:
                    query_vector = self._get_embedding(query_str)
                    results = self.index.similarity_search(
                        query_vector=query_vector,
                        columns=["*"],
                        num_results=k,
                    )
                else:
                    raise ValueError(
                        "Index does not support text queries and no OpenAI API key provided for embedding generation"
                    )

            chunks = []
            if results and "result" in results and "data_array" in results["result"]:
                for row in results["result"]["data_array"]:
                    chunk_data = self._create_chunk_data_from_raw(row)
                    chunks.append(chunk_data)

            return chunks

        except Exception as e:
            raise RuntimeError(f"Similarity search failed: {e}")

    def get_chunk_by_id(self, chunk_id: str) -> ChunkData:
        """
        Retrieve a specific chunk by its ID.

        Args:
            chunk_id: The unique identifier for the chunk

        Returns:
            ChunkData object for the specified chunk
        """
        try:
            # Use filters to get specific chunk by ID
            # The exact filter syntax may depend on your index schema
            results = self.index.similarity_search(
                query_vector=[0.0] * 1536,  # Dummy vector
                columns=["*"],
                filters={"id": chunk_id},  # Adjust field name if different
                num_results=1,
            )

            if (
                not results
                or "result" not in results
                or "data_array" not in results["result"]
                or len(results["result"]["data_array"]) == 0
            ):
                raise ValueError(f"Chunk with ID '{chunk_id}' not found")

            row = results["result"]["data_array"][0]
            return self._create_chunk_data_from_raw(row)

        except Exception as e:
            raise RuntimeError(f"Failed to retrieve chunk '{chunk_id}': {e}")
