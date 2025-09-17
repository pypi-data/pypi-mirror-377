"""Helper functions for creating common database schemas."""

from vecta.core.schemas import VectorDBSchema


class SchemaTemplates:
    """Pre-built schema templates for common database configurations."""

    @staticmethod
    def chroma_default() -> VectorDBSchema:
        """Default schema for ChromaDB (local and cloud)."""
        return VectorDBSchema(
            id_accessor="id",
            content_accessor="document",
            metadata_accessor="metadata",
            source_path_accessor="metadata.source_path",
            page_nums_accessor="metadata.page_nums",
        )

    @staticmethod
    def pinecone_default() -> VectorDBSchema:
        """Default schema for Pinecone."""
        return VectorDBSchema(
            id_accessor=".id",
            content_accessor="metadata.content",
            metadata_accessor="metadata",
            source_path_accessor="metadata.source_path",
            page_nums_accessor="metadata.page_nums",
        )

    @staticmethod
    def pgvector_standard(
        id_col: str = "id", content_col: str = "content", metadata_col: str = "metadata"
    ) -> VectorDBSchema:
        """Standard schema for pgvector with separate columns."""
        return VectorDBSchema(
            id_accessor=id_col,
            content_accessor=content_col,
            metadata_accessor=metadata_col,
            source_path_accessor=f"{metadata_col}.source_path",
            page_nums_accessor=f"{metadata_col}.page_nums",
        )

    @staticmethod
    def pgvector_flat(
        id_col: str = "id",
        content_col: str = "content",
        source_path_col: str = "source_path",
        page_nums_col: str = "page_nums",
    ) -> VectorDBSchema:
        """Schema for pgvector with flat column structure."""
        return VectorDBSchema(
            id_accessor=id_col,
            content_accessor=content_col,
            source_path_accessor=source_path_col,
            page_nums_accessor=page_nums_col,
        )

    @staticmethod
    def databricks_indexed() -> VectorDBSchema:
        """Schema for Databricks with index-based access."""
        return VectorDBSchema(
            id_accessor="[0]",
            content_accessor="[1]",
            metadata_accessor="[2]",
            source_path_accessor="[2].source_path",
            page_nums_accessor="[2].page_nums",
        )

    @staticmethod
    def weaviate_default() -> VectorDBSchema:
        """Default schema for Weaviate."""
        return VectorDBSchema(
            id_accessor=".uuid",
            content_accessor="properties.content",
            metadata_accessor="properties.metadata",
            source_path_accessor="properties.metadata.source_path",
            page_nums_accessor="properties.metadata.page_nums",
        )
