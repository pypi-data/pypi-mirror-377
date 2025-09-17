# vecta_backend/vecta/connectors/langchain_connector.py

from __future__ import annotations
from typing import List, Dict, Any, Tuple, cast

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore as LCVectorStore  # interface
from langchain_core.retrievers import BaseRetriever as LCRetriever

from vecta.connectors.base import BaseVectorDBConnector
from vecta.core.schemas import ChunkData, VectorDBSchema


class LangChainVectorStoreConnector(BaseVectorDBConnector):
    """
    Adapter that lets Vecta read/search a LangChain VectorStore or Retriever.

    Supports:
      - semantic_search via vectorstore.similarity_search(_with_score) or retriever.invoke
      - get_all_chunks via store-specific strategies:
          * Chroma: use `.get(limit, offset)` paging
          * FAISS: iterate `index_to_docstore_id` and fetch from `docstore`
    """

    def __init__(
        self,
        schema: VectorDBSchema,
        vectorstore: LCVectorStore | None = None,
        retriever: LCRetriever | None = None,
    ):
        super().__init__(schema)

        if vectorstore is None and retriever is None:
            raise ValueError("Provide either a LangChain VectorStore or a Retriever.")
        self.vs = vectorstore
        self.ret = retriever

    def semantic_search(self, query_str: str, k: int = 10) -> List[ChunkData]:
        if self.ret is not None:
            docs = self.ret.invoke(query_str)
            return [self._doc_to_chunk(d) for d in docs[:k]]

        assert self.vs is not None
        chunks: List[ChunkData] = []
        docs_and_scores: List[Tuple[Document, float]] | None = None

        # Prefer scores when available
        if hasattr(self.vs, "similarity_search_with_score"):
            try:
                docs_and_scores = cast(
                    List[Tuple[Document, float]],
                    self.vs.similarity_search_with_score(query_str, k=k),
                )
            except Exception:
                docs_and_scores = None

        if docs_and_scores is not None:
            for doc, score in docs_and_scores:
                chunk = self._doc_to_chunk(doc)
                chunk.metadata.setdefault("score", float(score))
                chunks.append(chunk)
            return chunks

        # Fallback: plain docs
        docs = self.vs.similarity_search(query_str, k=k)  # type: ignore[attr-defined]
        return [self._doc_to_chunk(d) for d in docs]

    def get_all_chunks(self) -> List[ChunkData]:
        if self.ret is not None:
            raise NotImplementedError("Bulk export from a Retriever is not supported.")

        assert self.vs is not None
        # Try store-specific bulk paths:
        # 1) Chroma wrapper exposes .get with paging
        if hasattr(self.vs, "get"):
            try:
                return self._export_via_get(self.vs)  # type: ignore[arg-type]
            except Exception:
                pass

        # 2) FAISS exposes docstore + index_to_docstore_id
        if hasattr(self.vs, "docstore") and hasattr(self.vs, "index_to_docstore_id"):
            return self._export_via_faiss(self.vs)

        # 3) No universal "get all" exists
        raise NotImplementedError(
            f"Bulk export is not supported for this vector store: {self._vs_name()}"
        )

    def get_chunk_by_id(self, chunk_id: str) -> ChunkData:
        """
        Retrieve a specific chunk by node ID via the docstore.
        """
        if self.vs and hasattr(self.vs, "get_by_ids"):
            docs = self.vs.get_by_ids([chunk_id])  # type: ignore[attr-defined]
            if not docs:
                raise ValueError(f"Chunk with ID '{chunk_id}' not found")
            return self._doc_to_chunk(docs[0])

        # Chroma path
        if self.vs is not None and hasattr(self.vs, "get"):
            raw = self.vs.get(ids=[chunk_id])  # type: ignore[attr-defined]
            ids = raw.get("ids") or []
            if not ids:
                raise ValueError(f"Chunk with ID '{chunk_id}' not found")
            doc = self._row_to_doc(raw, 0)
            return self._doc_to_chunk(doc)

        # FAISS path (docstore IDs are usually NOT equal to vector ids; best-effort)
        if hasattr(self.vs, "docstore"):
            store = getattr(self.vs, "docstore")
            doc = store.search(chunk_id)
            if doc is None:
                raise ValueError(f"Chunk with ID '{chunk_id}' not found")
            return self._doc_to_chunk(doc)

        raise NotImplementedError("This vector store does not support fetching by ID.")

    def _doc_to_chunk(self, doc: Document) -> ChunkData:
        md: Dict[str, Any] = dict(doc.metadata or {})

        # Create raw result in LangChain format
        raw_result = {
            "id": str(getattr(doc, "id", md.get("id", "")) or ""),
            "page_content": doc.page_content or "",
            "metadata": md,
        }

        return self._create_chunk_data_from_raw(raw_result)

    def _vs_name(self) -> str:
        if self.ret is not None:
            return self.ret.__class__.__name__
        return self.vs.__class__.__name__ if self.vs is not None else "Unknown"

    def _export_via_get(self, vs) -> List[ChunkData]:
        # Chroma-style paging API: get(limit, offset, include=['documents','metadatas'])
        batch = 100
        out: List[ChunkData] = []
        # Try to figure out total via a first call
        first = vs.get(limit=batch, offset=0, include=["documents", "metadatas"])
        total = len(first.get("ids") or [])
        if total == 0:
            return []
        out.extend(self._rows_to_chunks(first))
        offset = total
        while True:
            chunk = vs.get(
                limit=batch, offset=offset, include=["documents", "metadatas"]
            )
            ids = chunk.get("ids") or []
            if not ids:
                break
            out.extend(self._rows_to_chunks(chunk))
            offset += len(ids)
        return out

    def _export_via_faiss(self, vs) -> List[ChunkData]:
        # FAISS keeps a mapping + docstore. Iterate all.
        out: List[ChunkData] = []
        mapping = getattr(vs, "index_to_docstore_id")
        store = getattr(vs, "docstore")
        for _, doc_id in mapping.items():
            doc = store.search(doc_id)
            if doc is None:
                continue
            out.append(self._doc_to_chunk(doc))
        return out

    def _rows_to_chunks(self, raw) -> List[ChunkData]:
        docs = []
        ids = raw.get("ids") or []
        for i in range(len(ids)):
            docs.append(self._row_to_doc(raw, i))
        return [self._doc_to_chunk(d) for d in docs]

    def _row_to_doc(self, raw, i: int) -> Document:
        doc_texts = raw.get("documents") or []
        metas = raw.get("metadatas") or []
        ids = raw.get("ids") or []
        content = doc_texts[i] if i < len(doc_texts) else ""
        md = metas[i] if i < len(metas) else {}
        return Document(page_content=content, metadata=md, id=str(ids[i]))
