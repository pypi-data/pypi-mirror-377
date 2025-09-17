"""LlamaIndex connector implementation."""

from __future__ import annotations
from typing import List, Dict, Any, cast

import json

from vecta.connectors.base import BaseVectorDBConnector
from vecta.core.schemas import ChunkData, VectorDBSchema

# ---- LlamaIndex imports (version-tolerant) ----
# VectorStoreIndex
try:
    from llama_index.core import VectorStoreIndex  # type: ignore[import-untyped]
    from llama_index.core.schema import Document  # type: ignore[import-untyped]
except Exception:  # pragma: no cover
    try:
        from llama_index.core.indices.vector_store import (
            VectorStoreIndex,
        )  # type: ignore[import-untyped]
        from llama_index.core.schema import Document  # type: ignore[import-untyped]
    except Exception:
        try:
            from llama_index.legacy import VectorStoreIndex  # type: ignore[import-untyped, no-redef]
            from llama_index.legacy.schema import Document  # type: ignore[import-untyped, no-redef]
        except Exception as e:  # pragma: no cover
            raise ImportError(
                "Could not import VectorStoreIndex from LlamaIndex. "
                "Please install/update `llama-index`."
            ) from e

# BaseRetriever + schema types
try:
    from llama_index.core.retrievers import BaseRetriever  # type: ignore[import-untyped]
    from llama_index.core.schema import (  # type: ignore[import-untyped]
        BaseNode,
        NodeWithScore,
    )
except Exception:  # pragma: no cover
    try:
        from llama_index.legacy.retrievers import (  # type: ignore[import-untyped, no-redef]
            BaseRetriever,
        )
        from llama_index.legacy.schema import (  # type: ignore[import-untyped, no-redef]
            BaseNode,
            NodeWithScore,
        )
    except Exception as e:
        raise ImportError(
            "Could not import LlamaIndex BaseRetriever/BaseNode/NodeWithScore."
        ) from e


class LlamaIndexConnector(BaseVectorDBConnector):
    """
    Adapter that lets Vecta read/search a LlamaIndex VectorStoreIndex or Retriever.

    Args:
        schema: Schema for data extraction (REQUIRED)
        index: LlamaIndex VectorStoreIndex instance
        retriever: LlamaIndex BaseRetriever instance

    You must provide at least one of (index, retriever).
    For get_all_chunks/get_chunk_by_id, an Index with a populated docstore is required.
    """

    def __init__(
        self,
        schema: VectorDBSchema,
        index: VectorStoreIndex | None = None,
        retriever: BaseRetriever | None = None,
    ):
        super().__init__(schema)

        if index is None and retriever is None:
            raise ValueError(
                "Provide either a LlamaIndex VectorStoreIndex or a Retriever."
            )
        self.index = index
        self.ret = retriever

    def semantic_search(self, query_str: str, k: int = 10) -> List[ChunkData]:
        """
        Perform similarity search using LlamaIndex retrieval.

        If a custom retriever was supplied, we call retriever.retrieve(query).
        Otherwise, we create a retriever from the Index:
            index.as_retriever(similarity_top_k=k).retrieve(query)
        """
        try:
            if self.ret is not None:
                nodes_with_scores: List[NodeWithScore] = self.ret.retrieve(query_str)
            else:
                assert self.index is not None
                retriever = self.index.as_retriever(similarity_top_k=k)
                nodes_with_scores = retriever.retrieve(query_str)

            out: List[ChunkData] = []
            for nws in nodes_with_scores[:k]:
                node: BaseNode = nws.node  # NodeWithScore -> BaseNode
                chunk = self._node_to_chunk(node, score=getattr(nws, "score", None))
                out.append(chunk)
            return out
        except Exception as e:
            raise RuntimeError(f"Similarity search failed: {e}")

    def get_all_chunks(self) -> List[ChunkData]:
        """
        Export all chunks by enumerating the LlamaIndex docstore.

        Implementation strategy:
          1) Access a docstore from the index (index.docstore or index.storage_context.docstore)
          2) Gather node IDs via docstore.get_all_ref_doc_info()
          3) Fetch nodes with docstore.get_nodes([...])
        """
        if self.index is None:
            raise NotImplementedError(
                "Bulk export requires a VectorStoreIndex with an accessible docstore."
            )

        # Try to locate the docstore in a version-tolerant way
        docstore = getattr(self.index, "docstore", None)
        if docstore is None:
            sc = getattr(self.index, "storage_context", None)
            docstore = getattr(sc, "docstore", None)
        if docstore is None:
            raise NotImplementedError(
                "Could not find a docstore on the provided index."
            )

        # Preferred path: use ref_doc -> node_ids mapping
        try:
            ref_map = docstore.get_all_ref_doc_info()  # type: ignore[attr-defined]
        except Exception:
            ref_map = None

        nodes: List[BaseNode] = []
        if ref_map:
            # Python RefDocInfo typically exposes node_ids (TS docs show nodeIds)
            all_ids: List[str] = []
            for _ref_id, ref_info in cast(dict, ref_map).items():
                node_ids = (
                    getattr(ref_info, "node_ids", None)
                    or getattr(ref_info, "nodeIds", None)
                    or []
                )
                all_ids.extend(list(node_ids))
            if all_ids:
                nodes.extend(docstore.get_nodes(all_ids))  # type: ignore[attr-defined]

        # Fallback: some docstores expose .docs (dict of node_id -> BaseNode)
        if not nodes and hasattr(docstore, "docs"):
            docs_dict = getattr(docstore, "docs")
            try:
                nodes = list(cast(dict, docs_dict).values())
            except Exception:
                pass

        if not nodes:
            # Vector stores that keep text internally may not mirror nodes in docstore
            raise NotImplementedError(
                "No nodes found in docstore. This vector store may not keep text in the docstore."
            )

        return [self._node_to_chunk(n) for n in nodes]

    def get_chunk_by_id(self, chunk_id: str) -> ChunkData:
        """
        Retrieve a specific chunk by node ID via the docstore.
        """
        if self.index is None:
            raise NotImplementedError(
                "Fetching by ID requires an Index with a docstore (retriever alone is insufficient)."
            )

        # Locate docstore
        docstore = getattr(self.index, "docstore", None)
        if docstore is None:
            sc = getattr(self.index, "storage_context", None)
            docstore = getattr(sc, "docstore", None)
        if docstore is None:
            raise NotImplementedError(
                "Could not find a docstore on the provided index."
            )

        try:
            node: BaseNode = docstore.get_node(chunk_id)  # type: ignore[attr-defined]
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve chunk '{chunk_id}': {e}")

        return self._node_to_chunk(node)

    def _node_to_chunk(self, node: BaseNode, score: float | None = None) -> ChunkData:
        """Convert a LlamaIndex node into Vecta ChunkData."""
        # Prefer get_content(); fall back to .text if present
        content = ""
        try:
            content = node.get_content()
        except Exception:
            content = getattr(node, "text", "")  # legacy

        md: Dict[str, Any] = dict(getattr(node, "metadata", {}) or {})
        if score is not None:
            # keep a numeric score if provided
            md.setdefault("score", float(score))

        # Node/Chunk id
        node_id = getattr(node, "id_", None) or getattr(node, "node_id", "") or ""

        # Create raw result in LlamaIndex format
        raw_result = {
            "node_id": str(node_id),
            "content": content or "",
            "metadata": md,
        }

        return self._create_chunk_data_from_raw(raw_result)

    def _vs_name(self) -> str:
        if self.ret is not None:
            return self.ret.__class__.__name__
        return self.index.__class__.__name__ if self.index is not None else "Unknown"

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
            # Convert doc to node format and then to chunk
            out.append(self._node_to_chunk(doc))
        return out

    def _rows_to_chunks(self, raw) -> List[ChunkData]:
        docs = []
        ids = raw.get("ids") or []
        for i in range(len(ids)):
            doc_data = self._row_to_dict(raw, i)
            docs.append(doc_data)
        return [self._create_chunk_data_from_raw(d) for d in docs]

    def _row_to_dict(self, raw, i: int) -> Dict[str, Any]:
        doc_texts = raw.get("documents") or []
        metas = raw.get("metadatas") or []
        ids = raw.get("ids") or []
        content = doc_texts[i] if i < len(doc_texts) else ""
        md = metas[i] if i < len(metas) else {}

        # Create raw result in the format expected by the schema
        return {
            "node_id": str(ids[i]) if i < len(ids) else "",
            "content": content,
            "metadata": md,
        }
