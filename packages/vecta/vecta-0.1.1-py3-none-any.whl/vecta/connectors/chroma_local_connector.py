"""ChromaDB Local connector implementation."""

from typing import List, Dict, Any, cast

from vecta.connectors.base import BaseVectorDBConnector
from vecta.core.schemas import ChunkData, VectorDBSchema

# Custom connector helpers (always Type hint your connectors!)
from chromadb.api import ClientAPI
from chromadb.api.types import GetResult


class ChromaLocalConnector(BaseVectorDBConnector):
    """Connector for local ChromaDB vector database."""

    def __init__(
        self,
        client: ClientAPI,
        collection_name: str,
        schema: VectorDBSchema,
    ):
        """Initialize ChromaDB Local connector."""
        super().__init__(schema)
        self.client = client
        self.collection_name = collection_name

        try:
            self.collection = self.client.get_collection(name=collection_name)
        except Exception as e:
            raise ValueError(f"Could not access collection '{collection_name}': {e}")

    def get_all_chunks(self) -> List[ChunkData]:
        """
        Retrieve all chunks and metadata from the ChromaDB collection.

        Returns:
            List of ChunkData objects with all chunks from the collection.
        """
        # Get total count first
        total_count = self.collection.count()

        if total_count == 0:
            return []

        # Retrieve all data in batches to handle large collections
        batch_size = 100
        all_chunks: List[ChunkData] = []

        for offset in range(0, total_count, batch_size):
            print(f"Retrieving chunks {offset} to {offset + batch_size}")
            limit = min(batch_size, total_count - offset)

            result: GetResult = self.collection.get(
                include=[
                    "documents",  # type: ignore
                    "metadatas",  # type: ignore
                ],
                limit=limit,
                offset=offset,
            )

            # Process the batch
            batch_chunks = self._process_get_result(result)
            all_chunks.extend(batch_chunks)

        return all_chunks

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
            result = self.collection.query(
                query_texts=[query_str],
                n_results=k,
                include=[
                    "documents",  # type: ignore
                    "metadatas",  # type: ignore
                    "distances",  # type: ignore
                ],
            )

            chunks: List[ChunkData] = []
            # result["ids"] is List[IDs]; we check the first query group
            ids_group = result.get("ids")
            if ids_group and len(ids_group) > 0 and len(ids_group[0]) > 0:
                docs_group = result.get("documents") or []
                metas_group = result.get("metadatas") or []

                ids0: List[str] = cast(List[str], ids_group[0])
                docs0: List[str] = cast(List[str], docs_group[0]) if docs_group else []
                metas0: List[Dict[str, Any]] = (
                    cast(List[Dict[str, Any]], metas_group[0]) if metas_group else []
                )

                for i in range(len(ids0)):
                    document = docs0[i] if i < len(docs0) else ""
                    metadata = metas0[i] if i < len(metas0) else {}

                    # Create raw result in Chroma format
                    raw_result = {
                        "id": ids0[i],
                        "document": document,
                        "metadata": metadata,
                    }

                    chunk_data = self._create_chunk_data_from_raw(raw_result)
                    chunks.append(chunk_data)

            return chunks

        except Exception as e:
            raise RuntimeError(f"Similarity search failed: {e}")

    def get_chunk_by_id(self, chunk_id: str) -> ChunkData:
        """
        Retrieve a specific chunk by ID.

        Args:
            chunk_id: The chunk identifier

        Returns:
            ChunkData object for the specified chunk
        """
        try:
            result: GetResult = self.collection.get(
                ids=[chunk_id],
                include=[
                    "documents",  # type: ignore
                    "metadatas",  # type: ignore
                ],
            )

            if not result["ids"] or len(result["ids"]) == 0:
                raise ValueError(f"Chunk with ID '{chunk_id}' not found")

            chunks = self._process_get_result(result)
            return chunks[0]

        except Exception as e:
            raise RuntimeError(f"Failed to retrieve chunk '{chunk_id}': {e}")

    def _process_get_result(self, result: GetResult) -> List[ChunkData]:
        """
        Process ChromaDB GetResult into list of ChunkData objects.

        Args:
            result: GetResult from ChromaDB query

        Returns:
            List of ChunkData objects
        """
        chunks: List[ChunkData] = []

        if not result["ids"]:
            return chunks

        ids: List[str] = cast(List[str], result["ids"])
        documents: List[str] = cast(List[str], result.get("documents", []) or [])
        metadatas: List[Dict[str, Any]] = cast(
            List[Dict[str, Any]], result.get("metadatas", []) or []
        )

        for i, chunk_id in enumerate(ids):
            document = documents[i] if i < len(documents) else ""
            metadata = metadatas[i] if i < len(metadatas) else {}

            # Create raw result in Chroma format
            raw_result = {
                "id": chunk_id,
                "document": document,
                "metadata": metadata or {},
            }

            chunk_data = self._create_chunk_data_from_raw(raw_result)
            chunks.append(chunk_data)

        return chunks
