"""Azure Cosmos DB (NoSQL) vector-search connector."""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Sequence, Union, cast
import json
import os

from azure.cosmos import CosmosClient, exceptions  # type: ignore

from vecta.connectors.base import BaseVectorDBConnector
from vecta.core.schemas import ChunkData, VectorDBSchema


Embed = Sequence[float]


class AzureCosmosConnector(BaseVectorDBConnector):
    """
    Vecta connector for Azure Cosmos DB for NoSQL with vector search.
    """

    def __init__(
        self,
        *,
        database_name: str,
        container_name: str,
        schema: VectorDBSchema,
        # Either pass an existing client or (endpoint,key)
        client: Optional[CosmosClient] = None,
        endpoint: Optional[str] = None,
        key: Optional[str] = None,
        # Field names in your documents
        embedding_field: str = "embedding",
        # Partitioning
        partition_key_path: Optional[str] = None,
        default_partition_key_value: Optional[Any] = None,
        # Embeddings (optional: only needed if you want text->vector here)
        openai_api_key: Optional[str] = None,
        embedding_model: str = "text-embedding-3-small",
    ):
        super().__init__(schema)

        # Resolve SDK client
        if client is None:
            if not endpoint or not key:
                raise ValueError(
                    "Provide either an existing `client` or both `endpoint` and `key`."
                )
            client = CosmosClient(endpoint, key)  # type: ignore[arg-type]
        self._client = client

        # DB/Container
        try:
            self._db = self._client.get_database_client(database_name)
            self._container = self._db.get_container_client(container_name)
        except Exception as e:
            raise ValueError(
                f"Could not access Cosmos DB container '{database_name}/{container_name}': {e}"
            )

        # Fields & partitioning
        self._embedding_f = embedding_field
        self._pk_path = partition_key_path
        self._pk_default = default_partition_key_value

        # Embeddings
        self._embedding_model = embedding_model
        self._openai = None
        key_from_env = openai_api_key or os.getenv("OPENAI_API_KEY")
        if key_from_env:
            try:
                from openai import OpenAI  # lazy import

                self._openai = OpenAI(api_key=key_from_env)
            except Exception as e:
                raise ImportError(
                    "openai package is required to embed text queries here. "
                    "Install with `pip install openai`, or pass vectors directly."
                ) from e

    def get_all_chunks(self) -> List[ChunkData]:
        """
        Stream all docs and map to ChunkData.

        Uses a simple SELECT projection; set `max_item_count` to page results.
        For very large containers, prefer server-side filtering/paging by IDs you track.
        """
        query = "SELECT * FROM c"
        items = self._iter_query(query)
        out: List[ChunkData] = []
        for item in items:
            chunk_data = self._create_chunk_data_from_raw(item)
            out.append(chunk_data)
        return out

    def semantic_search(self, query_str: str, k: int = 10) -> List[ChunkData]:
        """
        Text -> embedding (if configured) -> vector search via VectorDistance ORDER BY.

        If no embedder is available, this will raise a helpful error suggesting
        `semantic_search_vector` instead (passing a pre-computed vector).
        """
        if self._openai is None:
            raise ValueError(
                "No embedder configured. Provide `openai_api_key` or use `semantic_search_vector` with a vector."
            )
        qvec = self._embed_text(query_str)
        return self.semantic_search_vector(qvec, k=k)

    def get_chunk_by_id(self, chunk_id: str) -> ChunkData:
        """Fetch by id (uses read_item if we know a partition key value; else a query)."""
        # Best path: if caller provided a default PK value, use read_item
        if self._pk_path and self._pk_default is not None:
            try:
                doc = self._container.read_item(
                    item=chunk_id, partition_key=self._pk_default
                )
                return self._create_chunk_data_from_raw(doc)
            except exceptions.CosmosResourceNotFoundError:
                raise ValueError(f"Chunk with ID '{chunk_id}' not found")
            except Exception as e:
                raise RuntimeError(f"Failed to retrieve chunk '{chunk_id}': {e}")

        # Fallback: cross-partition query by id
        query = "SELECT * FROM c WHERE c.id = @id"
        params = [{"name": "@id", "value": chunk_id}]
        items = list(self._iter_query(query, parameters=params))
        if not items:
            raise ValueError(f"Chunk with ID '{chunk_id}' not found")
        return self._create_chunk_data_from_raw(items[0])

    def semantic_search_vector(
        self,
        query_vector: Union[str, Sequence[float]],
        *,
        k: int = 10,
        exact_search: Optional[bool] = None,
        spec: Optional[Dict[str, Any]] = None,
        project_score_field: Optional[str] = "SimilarityScore",
    ) -> List[ChunkData]:
        """
        Perform vector search with a *provided* vector (no embedding step).

        Args:
            query_vector: Python list/tuple of floats OR a JSON-like string "[...]" to embed in the SQL.
            k: TOP k
            exact_search: If set, passes the optional exact flag to VectorDistance
            spec: Optional spec dict (e.g., {'dataType': 'float32', 'distanceFunction': 'cosine'})
            project_score_field: Name of projected score column in results

        Returns:
            Top-k similar ChunkData
        """
        # Build VectorDistance call string with optional args
        vd = f"VectorDistance(c.{self._embedding_f}, @q)"
        params: List[Dict[str, Any]] = [
            {"name": "@q", "value": query_vector}
        ]  # SDK will serialize arrays

        if exact_search is not None or spec is not None:
            # We must build the optional params in-query; SDK doesn't expand dicts into JSON automatically,
            # so we pass spec through @spec and reference it.
            vd = f"VectorDistance(c.{self._embedding_f}, @q"
            if exact_search is not None:
                vd += ", @exact"
                params.append({"name": "@exact", "value": bool(exact_search)})
            if spec is not None:
                vd += ", @spec"
                params.append({"name": "@spec", "value": spec})
            vd += ")"

        score_alias = project_score_field or "SimilarityScore"
        query = (
            f"SELECT TOP {int(k)} *, {vd} AS {score_alias} " f"FROM c " f"ORDER BY {vd}"
        )

        rows = self._iter_query(query, parameters=params)
        out: List[ChunkData] = []
        for r in rows:
            chunk = self._create_chunk_data_from_raw(r)
            # preserve numeric score if projected
            if score_alias in r:
                md = dict(chunk.metadata or {})
                md.setdefault("score", float(r[score_alias]))
                chunk.metadata = md
            out.append(chunk)
        return out

    def _iter_query(
        self,
        query: str,
        *,
        parameters: Optional[List[Dict[str, Any]]] = None,
        partition_key: Optional[Any] = None,
        enable_cross_partition: Optional[bool] = True,
        max_item_count: Optional[int] = 100,
    ):
        """
        Iterate a Cosmos query.

        - query: Cosmos SQL string
        - parameters: list of {"name": "@p", "value": ...}
        - partition_key: scope to a single PK value if you have one
        - enable_cross_partition: True for cross-partition queries (default)
        - max_item_count: page size hint
        """
        return self._container.query_items(
            query=query,
            parameters=parameters or [],
            partition_key=partition_key,
            enable_cross_partition_query=enable_cross_partition,
            max_item_count=max_item_count,
        )

    def _embed_text(self, text: str) -> Embed:
        assert self._openai is not None
        resp = self._openai.embeddings.create(
            input=text.replace("\n", " "),
            model=self._embedding_model,
        )
        return cast(Embed, resp.data[0].embedding)
