# vecta_backend/vecta/api_client.py
"""API client for the Vecta RAG benchmarking platform."""

import os
import requests
from typing import List, Optional, Dict, Any, Union, Callable, Tuple
from urllib.parse import urljoin

from vecta.exceptions import (
    VectaAPIError,
    VectaAuthenticationError,
    VectaNotFoundError,
    VectaBadRequestError,
    VectaServerError,
    VectaForbiddenError,
    VectaRateLimitError,
    VectaInsufficientDataError,
    VectaNoBenchmarkError,
)
from vecta.core.schemas import (
    ChunkData,
    BenchmarkEntry,
    VectorDBType,
    EvaluationType,
    BenchmarkResults,
    RetrievalAndGenerationResults,
    GenerationOnlyResults,
    RenameRequest,
    VectorDBSchema,
)
from vecta.connectors.base import BaseVectorDBConnector
from vecta.core.benchmark import VectaClient


class VectaAPIClient:
    """
    API client that orchestrates between local Vecta SDK evaluation and remote server operations.

    The server handles AI operations (benchmark generation, evaluation scoring).
    The client handles local RAG pipeline evaluation using the Vecta SDK.
    """

    def __init__(
        self,
        api_key: Optional[str] = os.getenv("VECTA_API_KEY"),
        base_url: str = os.getenv("VECTA_API_BASE_URL", "https://vecta.up.railway.app"),
        timeout: int = 600,
    ):
        """
        Initialize the Vecta API client.

        Args:
            api_key: Your Vecta API key
            base_url: Base URL for the Vecta API
            timeout: Request timeout in seconds
        """
        if not api_key:
            raise ValueError(
                "API key is required. Set VECTA_API_KEY environment variable."
            )

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "vecta-sdk/0.1.0",
            }
        )

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Any:
        """Make an HTTP request to the API."""
        url = urljoin(self.base_url + "/", endpoint.lstrip("/"))

        kwargs.setdefault("timeout", self.timeout)
        if params:
            kwargs["params"] = params
        if json_data:
            kwargs["json"] = json_data

        try:
            response = self.session.request(method, url, **kwargs)

            if response.status_code in [200, 201]:
                return response.json() if response.content else {}
            elif response.status_code == 401:
                raise VectaAuthenticationError("Invalid API key")
            elif response.status_code == 403:
                raise VectaForbiddenError("Access forbidden - check your plan limits")
            elif response.status_code == 404:
                raise VectaNotFoundError("Resource not found")
            elif response.status_code == 400:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get("error", "Bad request")
                if "message" in error_data:
                    error_msg += f": {error_data['message']}"

                if "not enough chunks" in error_msg.lower():
                    raise VectaInsufficientDataError(error_msg)
                elif "benchmark not found" in error_msg.lower():
                    raise VectaNoBenchmarkError(error_msg)
                else:
                    raise VectaBadRequestError(error_msg)
            elif response.status_code == 429:
                raise VectaRateLimitError("Rate limit exceeded")
            elif response.status_code >= 500:
                raise VectaServerError("Server error occurred")
            else:
                raise VectaAPIError(
                    f"Request failed with status {response.status_code}"
                )

        except requests.exceptions.Timeout:
            raise VectaAPIError(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise VectaAPIError("Failed to connect to Vecta API")
        except requests.exceptions.RequestException as e:
            raise VectaAPIError(f"Request failed: {e}")

    # Database Management
    def connect_local_database(
        self,
        connector: BaseVectorDBConnector,
        db_type: VectorDBType,
        collection_name: str,
        name: Optional[str] = None,
        schema: Optional[VectorDBSchema] = None,
    ) -> Dict[str, Any]:
        """Connect a local vector database and upload its chunks."""
        # Create database record
        config = {
            "collection_name": collection_name,
            "host": "__LOCAL__",  # Marker for local database
        }

        db_config = {
            "db_type": db_type.value,
            "connection_config": config,
            "schema": schema.model_dump() if schema else None,
        }

        database = self._make_request("POST", "/databases", json_data=db_config)

        # Upload chunks
        print("Uploading chunks to server...")
        chunks = connector.get_all_chunks()
        print(f"Found {len(chunks)} chunks to upload")

        if chunks:
            self._upload_chunks_in_batches(database["id"], chunks)
            # Sync to update metadata
            database = self._make_request("POST", f'/databases/{database["id"]}/sync')

        return database

    def connect_chroma_cloud(
        self,
        tenant: str,
        database_name: str,
        api_key: str,
        collection_name: str,
        schema: Optional[VectorDBSchema] = None,
    ) -> Dict[str, Any]:
        """Connect to Chroma Cloud vector database."""
        config = {
            "tenant": tenant,
            "database": database_name,
            "api_key": api_key,
            "collection_name": collection_name,
        }

        db_config = {
            "db_type": VectorDBType.CHROMA_CLOUD.value,
            "connection_config": config,
            "schema": schema.model_dump() if schema else None,
        }

        print("Connecting Chroma Cloud database...")
        database = self._make_request("POST", "/databases", json_data=db_config)
        print(f"Successfully connected! Database ID: {database['id']}")
        return database

    def connect_pinecone(
        self,
        api_key: str,
        index_name: str,
        namespace: str = "",
        schema: Optional[VectorDBSchema] = None,
    ) -> Dict[str, Any]:
        """Connect to Pinecone vector database."""
        config = {
            "api_key": api_key,
            "index_name": index_name,
            "namespace": namespace,
            "collection_name": index_name,
        }

        db_config = {
            "db_type": VectorDBType.PINECONE.value,
            "connection_config": config,
            "schema": schema.model_dump() if schema else None,
        }

        print("Connecting Pinecone database...")
        database = self._make_request("POST", "/databases", json_data=db_config)
        print(f"Successfully connected! Database ID: {database['id']}")
        return database

    def connect_azure_cosmos(
        self,
        endpoint: str,
        key: str,
        database_name: str,
        container_name: str,
        embedding_field: str = "embedding",
        partition_key_path: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        schema: Optional[VectorDBSchema] = None,
    ) -> Dict[str, Any]:
        """Connect to Azure Cosmos DB vector database."""
        config = {
            "endpoint": endpoint,
            "key": key,
            "database_name": database_name,
            "container_name": container_name,
            "embedding_field": embedding_field,
            "partition_key_path": partition_key_path,
            "openai_api_key": openai_api_key,
            "collection_name": container_name,
        }

        db_config = {
            "db_type": VectorDBType.AZURE_COSMOS.value,
            "connection_config": config,
            "schema": schema.model_dump() if schema else None,
        }

        print("Connecting Azure Cosmos DB...")
        database = self._make_request("POST", "/databases", json_data=db_config)
        print(f"Successfully connected! Database ID: {database['id']}")
        return database

    def connect_databricks(
        self,
        workspace_url: str,
        index_name: str,
        endpoint_name: Optional[str] = None,
        personal_access_token: Optional[str] = None,
        service_principal_client_id: Optional[str] = None,
        service_principal_client_secret: Optional[str] = None,
        azure_tenant_id: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        schema: Optional[VectorDBSchema] = None,
    ) -> Dict[str, Any]:
        """Connect to Databricks Vector Search."""
        config = {
            "workspace_url": workspace_url,
            "index_name": index_name,
            "endpoint_name": endpoint_name,
            "personal_access_token": personal_access_token,
            "service_principal_client_id": service_principal_client_id,
            "service_principal_client_secret": service_principal_client_secret,
            "azure_tenant_id": azure_tenant_id,
            "openai_api_key": openai_api_key,
            "collection_name": index_name,
        }

        db_config = {
            "db_type": VectorDBType.DATABRICKS.value,
            "connection_config": config,
            "schema": schema.model_dump() if schema else None,
        }

        print("Connecting Databricks Vector Search...")
        database = self._make_request("POST", "/databases", json_data=db_config)
        print(f"Successfully connected! Database ID: {database['id']}")
        return database

    def connect_weaviate(
        self,
        cluster_url: Optional[str] = None,
        api_key: Optional[str] = None,
        collection_name: str = "Documents",
        use_cloud: bool = True,
        host: str = "localhost",
        port: int = 8080,
        headers: Optional[Dict[str, str]] = None,
        schema: Optional[VectorDBSchema] = None,
    ) -> Dict[str, Any]:
        """Connect to Weaviate vector database."""
        config = {
            "cluster_url": cluster_url,
            "api_key": api_key,
            "collection_name": collection_name,
            "use_cloud": use_cloud,
            "host": host,
            "port": port,
            "headers": headers,
        }

        db_config = {
            "db_type": VectorDBType.WEAVIATE.value,
            "connection_config": config,
            "schema": schema.model_dump() if schema else None,
        }

        print("Connecting Weaviate database...")
        database = self._make_request("POST", "/databases", json_data=db_config)
        print(f"Successfully connected! Database ID: {database['id']}")
        return database

    def connect_pgvector(
        self,
        connection_string: str,
        table_name: str = "chunks",
        embedding_col: str = "embedding",
        openai_api_key: Optional[str] = None,
        schema: Optional[VectorDBSchema] = None,
    ) -> Dict[str, Any]:
        """Connect to PostgreSQL with pgvector extension."""
        config = {
            "connection_string": connection_string,
            "table_name": table_name,
            "embedding_col": embedding_col,
            "openai_api_key": openai_api_key,
            "collection_name": table_name,
        }

        db_config = {
            "db_type": VectorDBType.PGVECTOR.value,
            "connection_config": config,
            "schema": schema.model_dump() if schema else None,
        }

        print("Connecting PostgreSQL with pgvector...")
        database = self._make_request("POST", "/databases", json_data=db_config)
        print(f"Successfully connected! Database ID: {database['id']}")
        return database

    def connect_cloud_database(
        self,
        db_type: VectorDBType,
        api_key: str,
        index_name: Optional[str] = None,
        collection_name: Optional[str] = None,
        namespace: str = "",
        schema: Optional[VectorDBSchema] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Connect a cloud vector database (Pinecone, Chroma Cloud, etc.).
        This is a legacy method, prefer the specific connect_* methods above.
        """
        # Build connection config based on database type
        config: Dict[str, Any] = {
            "api_key": api_key,
            "namespace": namespace,
        }

        if db_type == VectorDBType.PINECONE:
            if not index_name:
                raise ValueError("index_name is required for Pinecone")
            config.update(
                {
                    "index_name": index_name,
                    "collection_name": collection_name or index_name,
                }
            )
        elif db_type == VectorDBType.CHROMA_CLOUD:
            if not collection_name:
                raise ValueError("collection_name is required for Chroma Cloud")
            config.update(
                {
                    "collection_name": collection_name,
                    "tenant": kwargs.get("tenant"),
                    "database": kwargs.get("database"),
                }
            )
        else:
            # Add other cloud database types as needed
            config.update(kwargs)
            if collection_name:
                config["collection_name"] = collection_name

        db_config = {
            "db_type": db_type.value,
            "connection_config": config,
            "schema": schema.model_dump() if schema else None,
        }

        print(f"Connecting {db_type.value} database...")
        database = self._make_request("POST", "/databases", json_data=db_config)

        print(f"Successfully connected! Database ID: {database['id']}")
        return database

    def _upload_chunks_in_batches(
        self, db_id: str, chunks: List[ChunkData], batch_size: int = 100
    ):
        """Upload chunks to server in batches."""
        total_batches = (len(chunks) + batch_size - 1) // batch_size

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            batch_num = i // batch_size + 1

            print(f"Uploading batch {batch_num}/{total_batches} ({len(batch)} chunks)")

            chunk_data = [
                {"id": chunk.id, "content": chunk.content, "metadata": chunk.metadata}
                for chunk in batch
            ]

            self._make_request(
                "POST",
                f"/databases/{db_id}/chunks",
                json_data={"chunks": chunk_data},
            )

    def list_databases(self) -> List[Dict[str, Any]]:
        """List all databases."""
        return self._make_request("GET", "/databases")

    def get_database(self, db_id: str) -> Dict[str, Any]:
        """Get database details."""
        return self._make_request("GET", f"/databases/{db_id}")

    def sync_database(self, db_id: str) -> Dict[str, Any]:
        """Sync database metadata."""
        return self._make_request("POST", f"/databases/{db_id}/sync")

    def rename_database(self, db_id: str, data: RenameRequest) -> Dict[str, Any]:
        """Rename a vector database."""
        return self._make_request(
            "PATCH", f"/databases/{db_id}", json_data=data.model_dump()
        )

    def delete_database(self, db_id: str) -> Dict[str, Any]:
        """Delete a vector database."""
        return self._make_request("DELETE", f"/databases/{db_id}")

    def delete_chunk(self, db_id: str, chunk_id: str) -> Dict[str, Any]:
        """Delete a chunk from a database."""
        return self._make_request("DELETE", f"/databases/{db_id}/chunks/{chunk_id}")

    # Benchmark Management
    def create_benchmark(
        self,
        vector_db_id: str,
        questions_count: int = 100,
        similarity_threshold: float = 0.7,
        description: Optional[str] = None,
        random_seed: Optional[int] = None,
        wait_for_completion: bool = True,
    ) -> Dict[str, Any]:
        """Create and generate a benchmark on the server using AI."""
        config = {
            "vector_db_id": vector_db_id,
            "questions_count": questions_count,
            "similarity_threshold": similarity_threshold,
            "description": description,
            "random_seed": random_seed,
        }

        # Create benchmark
        benchmark = self._make_request("POST", "/benchmarks", json_data=config)

        # Generate questions
        print(f"Generating {questions_count} questions using AI...")
        benchmark = self._make_request(
            "POST", f'/benchmarks/{benchmark["id"]}/generations'
        )

        if wait_for_completion:
            print("Waiting for benchmark generation to complete...")
            benchmark = self._wait_for_benchmark_completion(benchmark["id"])

        return benchmark

    def _wait_for_benchmark_completion(
        self, benchmark_id: str, poll_interval: int = 5, max_wait: int = 1800
    ) -> Dict[str, Any]:
        """Wait for benchmark generation to complete."""
        import time

        start_time = time.time()

        while time.time() - start_time < max_wait:
            benchmark = self._make_request("GET", f"/benchmarks/{benchmark_id}")

            if benchmark["status"] == "active":
                print("Benchmark generation completed!")
                return benchmark
            elif benchmark["status"] == "error":
                raise VectaAPIError("Benchmark generation failed")

            print(f"Status: {benchmark['status']}...")
            time.sleep(poll_interval)

        raise VectaAPIError(f"Benchmark generation timed out after {max_wait} seconds")

    def download_benchmark(self, benchmark_id: str) -> List[BenchmarkEntry]:
        """Download benchmark entries for local evaluation."""
        print("Downloading benchmark entries...")
        data = self._make_request("GET", f"/benchmarks/{benchmark_id}/entries")
        entries = [BenchmarkEntry(**entry) for entry in data]
        print(f"Downloaded {len(entries)} benchmark entries")
        return entries

    def export_benchmark(self, benchmark_id: str) -> str:
        """Export benchmark as CSV."""
        print("Exporting benchmark as CSV...")
        return self._make_request("GET", f"/benchmarks/{benchmark_id}/exports/csv")

    def list_benchmarks(self) -> List[Dict[str, Any]]:
        """List all benchmarks."""
        return self._make_request("GET", "/benchmarks")

    def get_benchmark(self, benchmark_id: str) -> Dict[str, Any]:
        """Get benchmark details."""
        return self._make_request("GET", f"/benchmarks/{benchmark_id}")

    def rename_benchmark(
        self, benchmark_id: str, data: RenameRequest
    ) -> Dict[str, Any]:
        """Rename a benchmark."""
        return self._make_request(
            "PATCH", f"/benchmarks/{benchmark_id}", json_data=data.model_dump()
        )

    def delete_benchmark(self, benchmark_id: str) -> Dict[str, Any]:
        """Delete a benchmark."""
        return self._make_request("DELETE", f"/benchmarks/{benchmark_id}")

    # Local Evaluation with Server-side Computation
    def evaluate_retrieval(
        self,
        benchmark_id: str,
        retrieval_function: Callable[[str], List[str]],
        evaluation_name: str = "API Evaluation",
    ) -> BenchmarkResults:
        """
        Evaluate a retrieval function locally and upload results to server.

        Args:
            benchmark_id: Benchmark ID to evaluate against
            retrieval_function: Function that takes query and returns chunk IDs
            evaluation_name: Name for this evaluation

        Returns:
            BenchmarkResults with computed metrics
        """
        print(f"Starting retrieval evaluation: {evaluation_name}")

        # Download benchmark entries
        entries = self.download_benchmark(benchmark_id)

        # Create local VectaClient instance for evaluation (no OpenAI key needed for eval)
        vecta = VectaClient(vector_db_connector=None)
        vecta.benchmark_entries = entries

        # Run local evaluation - timing is handled by the evaluator
        print("Running local evaluation...")
        results = vecta.evaluate_retrieval(retrieval_function, evaluation_name)

        print(f"Evaluation completed in {results.duration_seconds} seconds")

        # Upload results to server with timing
        self._upload_evaluation_results(
            benchmark_id=benchmark_id,
            evaluation_type=EvaluationType.RETRIEVAL_ONLY,
            evaluation_name=evaluation_name,
            results=results,
        )

        return results

    def evaluate_retrieval_and_generation(
        self,
        benchmark_id: str,
        retrieval_generation_function: Callable[[str], Tuple[List[str], str]],
        evaluation_name: str = "API RAG Evaluation",
    ) -> RetrievalAndGenerationResults:
        """
        Evaluate a retrieval + generation function using server-side evaluation.

        Args:
            benchmark_id: Benchmark ID to evaluate against
            retrieval_generation_function: Function that returns (chunk_ids, generated_text)
            evaluation_name: Name for this evaluation

        Returns:
            RetrievalAndGenerationResults with computed metrics
        """
        print(f"Starting retrieval + generation evaluation: {evaluation_name}")

        # Download benchmark entries
        entries = self.download_benchmark(benchmark_id)

        # Create local VectaClient instance to get the evaluation behavior
        vecta = VectaClient(vector_db_connector=None)
        vecta.benchmark_entries = entries

        # Run local evaluation for retrieval + generation - timing is handled by evaluator
        print("Running retrieval and generation locally...")
        results = vecta.evaluate_retrieval_and_generation(
            retrieval_generation_function, evaluation_name
        )

        print(f"Evaluation completed in {results.duration_seconds} seconds")

        # Store evaluation in database via API
        self._upload_evaluation_results(
            benchmark_id=benchmark_id,
            evaluation_type=EvaluationType.RETRIEVAL_AND_GENERATION,
            evaluation_name=evaluation_name,
            results=results,
        )

        return results

    def evaluate_generation_only(
        self,
        benchmark_id: str,
        generation_function: Callable[[str], str],
        evaluation_name: str = "API Generation Evaluation",
    ) -> GenerationOnlyResults:
        """
        Evaluate a generation function using server-side evaluation.

        Args:
            benchmark_id: Benchmark ID to evaluate against
            generation_function: Function that takes query and returns generated text
            evaluation_name: Name for this evaluation

        Returns:
            GenerationOnlyResults with computed metrics
        """
        print(f"Starting generation evaluation: {evaluation_name}")

        # Download benchmark entries
        entries = self.download_benchmark(benchmark_id)

        # Create local VectaClient instance to get the evaluation behavior
        vecta = VectaClient(vector_db_connector=None)
        vecta.benchmark_entries = entries

        # Run local evaluation for generation - timing is handled by evaluator
        print("Running generation locally...")
        results = vecta.evaluate_generation_only(generation_function, evaluation_name)

        print(f"Evaluation completed in {results.duration_seconds} seconds")

        # Store evaluation in database via API
        self._upload_evaluation_results(
            benchmark_id=benchmark_id,
            evaluation_type=EvaluationType.GENERATION_ONLY,
            evaluation_name=evaluation_name,
            results=results,
        )

        return results

    def _upload_evaluation_results(
        self,
        benchmark_id: str,
        evaluation_type: EvaluationType,
        evaluation_name: str,
        results: Union[
            BenchmarkResults, RetrievalAndGenerationResults, GenerationOnlyResults
        ],
    ):
        """Upload evaluation results to server for storage."""
        print("Uploading evaluation results to server...")

        evaluation_data = {
            "benchmark_id": benchmark_id,
            "evaluation_type": evaluation_type.value,
            "evaluation_name": evaluation_name,
            "results": results.model_dump(),
        }

        self._make_request("POST", "/evaluations", json_data=evaluation_data)
        print("Results uploaded successfully!")

    # Evaluation Management
    def list_evaluations(self) -> List[Dict[str, Any]]:
        """List all evaluations."""
        return self._make_request("GET", "/evaluations")

    def get_evaluation(self, evaluation_id: str) -> Dict[str, Any]:
        """Get evaluation details."""
        return self._make_request("GET", f"/evaluations/{evaluation_id}")

    def export_evaluation(self, evaluation_id: str) -> bytes:
        """Export evaluation as PDF report."""
        return self._make_request("GET", f"/evaluations/{evaluation_id}/exports/pdf")

    def rename_evaluation(
        self, evaluation_id: str, data: RenameRequest
    ) -> Dict[str, Any]:
        """Rename an evaluation."""
        return self._make_request(
            "PATCH", f"/evaluations/{evaluation_id}", json_data=data.model_dump()
        )

    def delete_evaluation(self, evaluation_id: str) -> Dict[str, Any]:
        """Delete an evaluation."""
        return self._make_request("DELETE", f"/evaluations/{evaluation_id}")

    # Server-side evaluation endpoints
    def evaluate_retrieval_and_generation_server(
        self,
        benchmark_id: str,
        evaluation_name: str,
        evaluation_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Evaluate retrieval and generation results on the server."""
        data = {
            "benchmark_id": benchmark_id,
            "evaluation_name": evaluation_name,
            "evaluation_results": evaluation_results,
        }
        return self._make_request(
            "POST", "/evaluations/evaluate-retrieval-and-generation", json_data=data
        )

    def evaluate_generation_only_server(
        self,
        benchmark_id: str,
        evaluation_name: str,
        evaluation_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Evaluate generation-only results on the server."""
        data = {
            "benchmark_id": benchmark_id,
            "evaluation_name": evaluation_name,
            "evaluation_results": evaluation_results,
        }
        return self._make_request(
            "POST", "/evaluations/evaluate-generation-only", json_data=data
        )
