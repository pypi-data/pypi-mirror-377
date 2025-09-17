"""PostgreSQL + pgvector connector implementation."""

from __future__ import annotations

import json
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Sequence,
    Tuple,
    Union,
    cast,
)

from vecta.connectors.base import BaseVectorDBConnector
from vecta.core.schemas import ChunkData, VectorDBSchema

# psycopg 3 (sync)
try:
    import psycopg
    from psycopg.rows import dict_row
except Exception as e:  # pragma: no cover
    raise ImportError("psycopg>=3 is required for PgVectorConnector") from e

# Optional: pgvector-python adapters for psycopg
from pgvector.psycopg import register_vector as _register_vector  # type: ignore[import-untyped]

Embedder = Callable[[str], Sequence[float]]
Metric = Literal["l2", "cosine", "ip", "l1", "hamming", "jaccard"]


class PgVectorConnector(BaseVectorDBConnector):
    """
    Connector for pgvector-backed Postgres tables.

    Requires explicit schema configuration since table structure varies.
    """

    def __init__(
        self,
        schema: VectorDBSchema,
        dsn: Optional[str] = None,
        *,
        connection: Optional[psycopg.Connection] = None,
        table: str = "chunks",
        embedding_col: str = "embedding",
        metric: Metric = "cosine",
        openai_api_key: Optional[str] = None,
        embedding_model: str = "text-embedding-3-small",
        embedder: Optional[Embedder] = None,
        register_pgvector_adapter: bool = True,
        server_side_cursor_name: str = "pgvector_stream",
        batch_size: int = 100,
    ):
        """
        Initialize the connector.

        Args:
            schema: Schema defining data extraction (REQUIRED)
            dsn: Database connection string
            connection: Existing psycopg connection
            table: Table name
            embedding_col: Embedding column name
            metric: Distance metric to use
            openai_api_key: OpenAI API key for embeddings
            embedding_model: OpenAI model to use
            embedder: Custom embedder function
            register_pgvector_adapter: Whether to register pgvector adapters
            server_side_cursor_name: Cursor name for streaming
            batch_size: Batch size for operations
        """
        super().__init__(schema)

        if connection is None and dsn is None:
            raise ValueError("Provide either a psycopg connection or a DSN.")
        self.conn = connection or psycopg.connect(dsn, row_factory=dict_row)  # type: ignore[arg-type]
        self.table = table
        self.embedding_col = embedding_col
        self.metric = metric
        self.batch_size = batch_size
        self.cursor_name = server_side_cursor_name

        # Optionally register pgvector adapters so lists/arrays bind cleanly
        if register_pgvector_adapter and _register_vector is not None:
            try:
                _register_vector(self.conn)
            except Exception:
                pass  # fall back to string literal formatting

        # Embedder resolution
        self._embedder: Optional[Embedder] = embedder
        self._openai_client = None
        if self._embedder is None and openai_api_key:
            try:
                from openai import OpenAI

                self._openai_client = OpenAI(api_key=openai_api_key)
                self._embedder = self._openai_embed  # use internal wrapper
                self._embedding_model = embedding_model
            except Exception as e:  # pragma: no cover
                raise ImportError(
                    "openai package is required for built-in embedding. "
                    "Install with `pip install openai`, or pass a custom `embedder`."
                ) from e

    def get_all_chunks(self) -> List[ChunkData]:
        """
        Stream all rows from the table.

        Uses a server-side cursor to avoid loading everything into memory at once.
        """
        sql = f"SELECT * FROM {self._q(self.table)}"
        out: List[ChunkData] = []

        # server-side cursor
        with self.conn.cursor(name=self.cursor_name) as cur:
            cur.execute(sql)
            while True:
                rows = cur.fetchmany(self.batch_size)
                if not rows:
                    break
                for row in rows:
                    row_dict = cast(Dict[str, Any], row)
                    chunk_data = self._create_chunk_data_from_raw(row_dict)
                    out.append(chunk_data)
        return out

    def semantic_search(self, query_str: str, k: int = 10) -> List[ChunkData]:
        """
        Perform a vector similarity search.

        - If an embedder is provided, embed `query_str` then search.
        - If no embedder is available, try to parse `query_str` as a JSON array like "[...]" and search directly.

        Uses the appropriate pgvector distance operator for the configured `metric`.
        """
        # get embedding
        query_vec: Union[str, Sequence[float]]
        if self._embedder is not None:
            query_vec = self._embedder(query_str)
        else:
            # allow raw vector literal like "[1,2,3]" or "{1,2,3}"
            s = query_str.strip()
            if not (s.startswith("[") or s.startswith("{")):
                raise ValueError(
                    "No embedder configured. Pass a vector literal like '[1,2,3]' or configure an embedder."
                )
            # send as plain text literal; Postgres casts to vector
            query_vec = s

        op = self._op_for_metric(self.metric)
        sql = (
            f"SELECT * "
            f"FROM {self._q(self.table)} "
            f"ORDER BY {self._q(self.embedding_col)} {op} %s "
            f"LIMIT %s"
        )

        # If we have pgvector adapters, we can pass a Python list/array; otherwise pass a string '[...]'
        params: Tuple[Any, Any] = (query_vec, k)

        rows: List[Dict[str, Any]]
        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cast(List[Dict[str, Any]], cur.fetchall())

        out: List[ChunkData] = []
        for row in rows:
            chunk_data = self._create_chunk_data_from_raw(row)
            out.append(chunk_data)
        return out

    def get_chunk_by_id(self, chunk_id: str) -> ChunkData:
        """Retrieve a specific chunk by ID using schema-defined accessor."""
        # We need to figure out the ID column from schema
        # This is a bit tricky since we need to reverse the accessor
        id_field = self._get_field_name_from_accessor(self.schema.id_accessor)

        sql = f"SELECT * FROM {self._q(self.table)} WHERE {self._q(id_field)} = %s"
        with self.conn.cursor() as cur:
            cur.execute(sql, (chunk_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"Chunk with ID '{chunk_id}' not found")

        row_dict = cast(Dict[str, Any], row)
        return self._create_chunk_data_from_raw(row_dict)

    def _get_field_name_from_accessor(self, accessor: str) -> str:
        """Extract field name from simple accessor (assumes direct field access for pgvector)."""
        # For pgvector, we assume simple field access like "id", "content", etc.
        # More complex accessors would need more sophisticated parsing
        if accessor.startswith(".") or "[" in accessor:
            raise ValueError(
                f"Complex accessor '{accessor}' not supported for SQL field identification"
            )
        return accessor

    def _q(self, ident: str) -> str:
        """Quote a SQL identifier simply and safely."""
        return '"' + ident.replace('"', '""') + '"'

    def _op_for_metric(self, metric: Metric) -> str:
        if metric == "cosine":
            return "<=>"
        if metric == "l2":
            return "<->"
        if metric == "ip":
            return "<#>"
        if metric == "l1":
            return "<+>"
        if metric == "hamming":
            return "<~>"
        if metric == "jaccard":
            return "<%>"
        raise ValueError(f"Unsupported metric: {metric}")

    # Built-in OpenAI embedder wrapper
    def _openai_embed(self, text: str) -> Sequence[float]:
        assert self._openai_client is not None
        resp = self._openai_client.embeddings.create(
            input=text.replace("\n", " "),
            model=getattr(self, "_embedding_model", "text-embedding-3-small"),
        )
        return cast(Sequence[float], resp.data[0].embedding)
