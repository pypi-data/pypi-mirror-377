# vecta_backend/vecta/core/dataset_importer.py
"""Dataset importer for converting HuggingFace datasets to Vecta format."""

from typing import List, Optional, Dict, Any, Tuple, Union
from datasets import load_dataset, Dataset  # type: ignore[import-untyped]
import json
import uuid
import os
import pandas as pd
from vecta.core.schemas import (
    ChunkData,
    BenchmarkEntry,
    VectorDBSchema,
    DatasetSchema,
    DataAccessor,
)


class BenchmarkDatasetImporter:
    """Imports HuggingFace datasets and converts them to Vecta format."""

    def import_msmarco(
        self, split: str = "test", max_items: int = 7
    ) -> Tuple[List[ChunkData], List[BenchmarkEntry]]:
        """
        Import MSMarco dataset for retrieval + generation evaluation.

        Args:
            split: Dataset split to load
            max_items: Maximum number of items to process

        Returns:
            Tuple of (chunks, benchmark_entries)
        """
        dataset = load_dataset("microsoft/ms_marco", "v1.1", split=split)

        # Limit dataset size
        dataset = dataset.select(range(min(max_items, len(dataset))))

        # Define schema for MSMarco fields
        msmarco_schema = DatasetSchema(
            question_accessor="query",
            answer_accessor="answers",  # This is a list, we'll take the first
            id_accessor="query_id",
            additional_accessors={
                "passages": "passages",
            },
        )

        chunks = []
        benchmark_entries = []

        # Define schema for MSMarco chunk format - url is the source path
        chunk_schema = VectorDBSchema(
            id_accessor="id",
            content_accessor="content",
            metadata_accessor="metadata",
            source_path_accessor="metadata.url",
            page_nums_accessor="metadata.page_nums",
        )

        for i, item in enumerate(dataset):
            # Use schema to extract fields
            fields = msmarco_schema.extract_dataset_fields(item)
            query = fields["question"]

            # Handle query_id more carefully
            raw_query_id = fields["id"]

            if raw_query_id is not None:
                query_id = str(raw_query_id)
            else:
                query_id = str(uuid.uuid4())

            answers = fields["answer"] or []
            passages = fields["passages"] or {}

            # Extract passage information
            passage_texts = passages.get("passage_text", [])
            is_selected = passages.get("is_selected", [])
            urls = passages.get("url", [])

            # Create chunks for all passages
            relevant_chunk_ids = []
            all_source_paths = []

            for j, (passage_text, selected, url) in enumerate(
                zip(passage_texts, is_selected, urls)
            ):
                chunk_id = f"{query_id}_passage_{j}"

                # Create metadata - handle missing/empty URLs
                source_path = url if url else f"passage_{j}"
                metadata = {
                    "url": url,
                    "source": "msmarco",
                    "is_selected": bool(selected),
                    "query_id": query_id,
                    "page_nums": None,  # MSMarco has no page number concept
                }

                # Create raw result for schema processing
                raw_result = {
                    "id": chunk_id,
                    "content": passage_text,
                    "metadata": metadata,
                }

                chunk_data = ChunkData.from_schema_extraction(chunk_schema, raw_result)
                chunks.append(chunk_data)

                # If this passage is selected as relevant
                if selected:
                    relevant_chunk_ids.append(chunk_id)
                    all_source_paths.append(source_path)

            # Create benchmark entry if we have answers and relevant chunks
            if answers and relevant_chunk_ids:
                # Take first answer if it's a list
                answer = answers[0] if isinstance(answers, list) else str(answers)
                entry = BenchmarkEntry(
                    id=query_id,
                    question=query,
                    answer=answer,
                    chunk_ids=relevant_chunk_ids,
                    page_nums=None,  # No page numbers available in MSMarco
                    source_paths=list(set(all_source_paths)),
                )
                benchmark_entries.append(entry)

        return chunks, benchmark_entries

    def import_gpqa_diamond(
        self, split: str = "train", max_items: int = 7
    ) -> Tuple[List[ChunkData], List[BenchmarkEntry]]:
        """
        Import GPQA Diamond dataset for generation-only evaluation.

        Note: GPQA Diamond is a pure generation task, so no chunks are created.
        Only benchmark entries are returned for generation evaluation.

        Args:
            split: Dataset split to load
            max_items: Maximum number of items to process

        Returns:
            Tuple of (empty chunks list, benchmark_entries)
        """
        dataset = load_dataset("Idavidrein/gpqa", "gpqa_diamond", split=split)

        # Limit dataset size
        dataset = dataset.select(range(min(max_items, len(dataset))))

        # Define schema for GPQA Diamond fields
        gpqa_schema = DatasetSchema(
            question_accessor="Question",
            answer_accessor="Correct Answer",
            id_accessor="Record ID",
            additional_accessors={
                "incorrect_answer_1": "Incorrect Answer 1",
                "incorrect_answer_2": "Incorrect Answer 2",
                "incorrect_answer_3": "Incorrect Answer 3",
                "explanation": "Explanation",
                "subdomain": "Subdomain",
                "high_level_domain": "High-level domain",
            },
        )

        # No chunks for generation-only evaluation
        chunks: List[ChunkData] = []
        benchmark_entries: List[BenchmarkEntry] = []

        for item in dataset:
            # Use schema to extract fields
            fields = gpqa_schema.extract_dataset_fields(item)
            question = fields["question"]
            answer = fields["answer"]
            record_id = str(fields["id"] or uuid.uuid4())
            explanation = fields["explanation"]
            subdomain = fields["subdomain"]
            high_level_domain = fields["high_level_domain"]

            # Create benchmark entry for generation-only evaluation
            # No chunk_ids since this is pure generation
            entry = BenchmarkEntry(
                id=record_id,
                question=question,
                answer=answer,
                chunk_ids=None,  # No chunks for generation-only tasks
                page_nums=None,  # No page numbers available in GPQA
                source_paths=[subdomain] if subdomain else ["unknown"],
            )
            benchmark_entries.append(entry)

        return chunks, benchmark_entries
