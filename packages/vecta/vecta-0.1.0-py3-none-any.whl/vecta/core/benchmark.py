# vecta_backend/vecta/core/benchmark.py
"""Main benchmarking class that orchestrates the entire process."""

import os
import random
from typing import List, Optional, Callable, Dict, Tuple, cast
import pandas as pd
from tqdm import tqdm

from vecta.connectors.base import BaseVectorDBConnector
from vecta.core.schemas import (
    ChunkData,
    BenchmarkEntry,
    BenchmarkResults,
    RetrievalAndGenerationResults,
    GenerationOnlyResults,
    UsageInfo,
)
from vecta.core.question_generator import QuestionGenerator
from vecta.core.evaluator import Evaluator
from vecta.core.similarity import EmbeddingSimilaritySearcher


class VectaClient:
    """Main class for creating and evaluating RAG retrieval benchmarks."""

    def __init__(
        self,
        vector_db_connector: Optional[BaseVectorDBConnector] = None,
        openai_api_key: Optional[str] = os.getenv("OPENROUTER_API_KEY"),
        openai_base_url: str = "https://openrouter.ai/api/v1",
        model: str = "google/gemini-2.5-flash-lite",
    ):
        """
        Initialize VectaClient.

        Args:
            vector_db_connector: Connector to the vector database (optional for API client usage)
            openai_api_key: OpenAI API key for question generation (not needed for API client)
            openai_base_url: OpenAI base URL
            model: OpenAI model to use
        """
        self.connector = vector_db_connector

        self.question_generator: Optional[QuestionGenerator]
        self.semantic_searcher: Optional[EmbeddingSimilaritySearcher]

        self.openai_base_url = openai_base_url

        # Only initialize AI components if API key is provided (server-side usage)
        if openai_api_key:
            self.question_generator = QuestionGenerator(
                openai_api_key=openai_api_key,
                openai_base_url=openai_base_url,
                model=model,
            )
            self.semantic_searcher = (
                EmbeddingSimilaritySearcher(vector_db_connector)
                if vector_db_connector
                else None
            )
        else:
            self.question_generator = None
            self.semantic_searcher = None

        self.all_chunks: List[ChunkData] = []
        self.meta_by_id: Dict[str, Tuple[Optional[List[int]], Optional[str]]] = {}
        self.benchmark_entries: List[BenchmarkEntry] = []
        self.openai_api_key = openai_api_key

    def load_knowledge_base(self) -> List[ChunkData]:
        """
        Load all chunks and metadata from the vector database.

        Returns:
            List of all ChunkData objects from the database
        """
        print("Loading knowledge base from vector database...")
        if not self.connector:
            raise ValueError("Vector database connector is not set")
        self.all_chunks = self.connector.get_all_chunks()
        print(f"Loaded {len(self.all_chunks)} chunks")

        self.meta_by_id = {c.id: (c.page_nums, c.source_path) for c in self.all_chunks}

        return self.all_chunks

    def generate_benchmark(
        self,
        n_questions: int,
        similarity_threshold: float = 0.7,
        similarity_top_k: int = 5,
        random_seed: Optional[int] = None,
    ) -> List[BenchmarkEntry]:
        """
        Generate synthetic benchmark questions using parallelized LLM calls.
        This method requires OpenAI API key and is typically used server-side.

        Args:
            n_questions: Number of questions to generate
            similarity_threshold: Minimum similarity score for considering chunks as duplicates
            similarity_top_k: Number of similar chunks to check for each question
            random_seed: Optional random seed for reproducibility

        Returns:
            Tuple of (List of BenchmarkEntry objects, UsageInfo)
        """
        if not self.question_generator:
            raise ValueError("OpenAI API key required for benchmark generation")

        if not self.all_chunks:
            raise ValueError(
                "Knowledge base not loaded. Call load_knowledge_base() first."
            )

        if not self.semantic_searcher:
            raise ValueError("Similarity searcher not initialized.")

        # All chunks can be used for similarity search since we no longer require embeddings
        if len(self.all_chunks) < n_questions:
            raise ValueError(
                f"Not enough chunks ({len(self.all_chunks)}) for {n_questions} questions"
            )

        if random_seed is not None:
            random.seed(random_seed)

        # Sample random chunks
        selected_chunks = random.sample(self.all_chunks, n_questions)

        print(f"Generating {n_questions} synthetic questions...")

        # Step 1: Batch generate questions for all selected chunks
        print("Generating questions in parallel batches...")
        chunk_question_pairs = self.question_generator.generate_questions_batch(
            selected_chunks
        )
        print(f"Generated {len(chunk_question_pairs)} questions")

        # Step 2: For each question, find similar chunks and collect evaluation tasks
        print("Finding similar chunks and preparing evaluations...")
        evaluation_tasks = []
        chunk_question_similar_map = {}

        for chunk, synthetic_q in tqdm(
            chunk_question_pairs, desc="Finding similar chunks"
        ):
            # Find similar chunks that might also answer this question
            similar_chunks = self.semantic_searcher.find_similar_chunks(
                target_chunk=chunk,
                all_chunks=self.all_chunks,
                k=similarity_top_k,
                similarity_threshold=similarity_threshold,
            )

            # Store the mapping for later use
            chunk_question_similar_map[(chunk.id, synthetic_q.question)] = {
                "chunk": chunk,
                "question": synthetic_q,
                "similar_chunks": similar_chunks,
            }

            # Add evaluation tasks for similar chunks
            for similar_chunk, similarity_score in similar_chunks:
                evaluation_tasks.append((synthetic_q.question, similar_chunk))

        # Step 3: Batch process all evaluation tasks
        print(
            f"Evaluating {len(evaluation_tasks)} chunk-question pairs in parallel batches..."
        )
        evaluation_results = self.question_generator.evaluate_chunks_batch(
            evaluation_tasks
        )

        # Step 4: Build evaluation results map for quick lookup
        evaluation_map = {}
        for question, chunk, evaluation in evaluation_results:
            evaluation_map[(question, chunk.id)] = evaluation

        # Step 5: Assemble benchmark entries
        print("Assembling benchmark entries...")
        benchmark_entries = []

        for chunk, synthetic_q in chunk_question_pairs:
            try:
                # Collect correct answers using an ordered mapping to keep alignment
                from collections import OrderedDict

                answers = OrderedDict()
                answers[chunk.id] = (chunk.page_nums, chunk.source_path)

                # Get similar chunks for this question
                key = (chunk.id, synthetic_q.question)
                if key in chunk_question_similar_map:
                    similar_chunks = cast(
                        List[Tuple[ChunkData, float]],
                        chunk_question_similar_map[key]["similar_chunks"],
                    )

                    # Check evaluations for similar chunks
                    for similar_chunk, similarity_score in similar_chunks:
                        eval_key = (synthetic_q.question, similar_chunk.id)
                        if eval_key in evaluation_map:
                            evaluation = evaluation_map[eval_key]
                            if evaluation.can_answer and evaluation.confidence >= 0.8:
                                answers.setdefault(
                                    similar_chunk.id,
                                    (
                                        similar_chunk.page_nums,
                                        similar_chunk.source_path,
                                    ),
                                )

                # Flatten all page_nums and collect unique values
                all_page_nums = []
                for page_nums, _ in answers.values():
                    if page_nums:
                        all_page_nums.extend(page_nums)
                unique_page_nums = (
                    sorted(list(set(all_page_nums))) if all_page_nums else None
                )

                # Collect all source_paths
                all_source_paths = []
                for _, source_path in answers.values():
                    if source_path:
                        all_source_paths.append(source_path)
                unique_source_paths = (
                    list(set(all_source_paths)) if all_source_paths else None
                )

                # Materialize aligned lists
                correct_chunk_ids = list(answers.keys())

                # Create benchmark entry
                entry = BenchmarkEntry(
                    question=synthetic_q.question,
                    answer=synthetic_q.answer,
                    chunk_ids=correct_chunk_ids if correct_chunk_ids else None,
                    page_nums=unique_page_nums,
                    source_paths=unique_source_paths,
                )

                benchmark_entries.append(entry)

            except Exception as e:
                print(
                    f"Warning: Failed to create benchmark entry for chunk {chunk.id}: {e}"
                )
                continue

        self.benchmark_entries = benchmark_entries
        print(f"Successfully generated {len(benchmark_entries)} benchmark questions")

        return benchmark_entries

    def save_benchmark(self, file_path: str) -> None:
        """
        Save benchmark to CSV file.

        Args:
            file_path: Path to save the CSV file
        """
        if not self.benchmark_entries:
            raise ValueError("No benchmark entries to save. Generate benchmark first.")

        # Convert to records for CSV
        records = []
        for entry in self.benchmark_entries:
            records.append(
                {
                    "id": entry.id,
                    "question": entry.question,
                    "answer": entry.answer,
                    "chunk_ids": "|".join(entry.chunk_ids) if entry.chunk_ids else "",
                    "page_nums": (
                        "|".join(map(str, entry.page_nums)) if entry.page_nums else ""
                    ),
                    "source_paths": (
                        "|".join(entry.source_paths) if entry.source_paths else ""
                    ),
                }
            )

        df = pd.DataFrame(records)
        df.to_csv(file_path, index=False)
        print(f"Benchmark saved to {file_path}")

    def load_benchmark(self, file_path: str) -> List[BenchmarkEntry]:
        """
        Load benchmark from CSV file.

        Args:
            file_path: Path to the CSV file

        Returns:
            List of BenchmarkEntry objects
        """
        print(f"DEBUG: VectaClient.load_benchmark called with {file_path}")
        df = pd.read_csv(file_path)
        print(f"DEBUG: Read {len(df)} rows from CSV")

        benchmark_entries = []
        for _, row in df.iterrows():
            # Handle NaN values by converting to empty string first
            chunk_ids_str: str | None = (
                str(row["chunk_ids"]) if pd.notna(row["chunk_ids"]) else None
            )
            page_nums_str: str | None = (
                str(row["page_nums"]) if pd.notna(row["page_nums"]) else None
            )
            source_paths_str: str | None = (
                str(row["source_paths"]) if pd.notna(row["source_paths"]) else None
            )

            print(
                f"DEBUG: Row {row.get('id', 'unknown')}: chunk_ids='{chunk_ids_str}', page_nums='{page_nums_str}', source_paths='{source_paths_str}'"
            )

            # Parse chunk_ids
            chunk_ids = None
            if chunk_ids_str and chunk_ids_str not in ("", "nan"):
                chunk_ids = chunk_ids_str.split("|")

            # Parse page_nums - None means no page information available
            page_nums = None
            if page_nums_str and page_nums_str not in ("", "nan"):
                try:
                    page_nums = [int(x) for x in page_nums_str.split("|") if x]
                except ValueError:
                    page_nums = None

            # Parse source_paths
            source_paths = None
            if source_paths_str and source_paths_str not in ("", "nan"):
                source_paths = source_paths_str.split("|")

            entry = BenchmarkEntry(
                id=str(row["id"]),
                question=str(row["question"]),
                answer=str(row["answer"]),
                chunk_ids=chunk_ids,
                page_nums=page_nums,
                source_paths=source_paths,
            )
            print(
                f"DEBUG: Created entry with chunk_ids={entry.chunk_ids}, page_nums={entry.page_nums}, source_paths={entry.source_paths}"
            )
            benchmark_entries.append(entry)

        self.benchmark_entries = benchmark_entries
        print(
            f"DEBUG: Loaded {len(benchmark_entries)} benchmark entries from {file_path}"
        )

        return benchmark_entries

    def evaluate_retrieval(
        self,
        retrieval_function: Callable[[str], List[str]],
        evaluation_name: Optional[str] = None,
    ) -> BenchmarkResults:
        """
        Evaluate a retrieval-only function against the benchmark.
        This method works without OpenAI API key and can be used client-side.

        Args:
            retrieval_function: Function that takes query string and returns list of chunk IDs
            evaluation_name: Name to use for this retrieval function when sent to the API

        Returns:
            BenchmarkResults with evaluation metrics
        """
        if not self.benchmark_entries:
            raise ValueError("No benchmark loaded. Generate or load benchmark first.")

        # For API client usage, meta_by_id might not be available
        if not self.meta_by_id and self.benchmark_entries:
            # Build meta_by_id from benchmark entries
            print("Building metadata lookup from benchmark entries...")
            self.meta_by_id = {}
            for entry in self.benchmark_entries:
                if entry.chunk_ids:
                    for i, chunk_id in enumerate(entry.chunk_ids):
                        # Use the entry's source_paths and page_nums
                        self.meta_by_id[chunk_id] = (
                            entry.page_nums,
                            entry.source_paths[0] if entry.source_paths else None,
                        )

        # default to function name if not provided
        if not evaluation_name:
            evaluation_name = retrieval_function.__name__

        evaluator = Evaluator(
            self.benchmark_entries,
            meta_lookup=self.meta_by_id,
            openai_base_url=self.openai_base_url,
            openai_api_key=self.openai_api_key,
        )
        results = evaluator.evaluate_retrieval(retrieval_function, evaluation_name)

        print(f"\nEvaluation Results for {evaluation_name}:")
        print(f"Total Questions: {results.total_questions}")
        print("\nChunk Level:")
        print(f"  Precision: {results.chunk_level.precision:.3f}")
        print(f"  Recall: {results.chunk_level.recall:.3f}")
        print(f"  F1 Score: {results.chunk_level.f1_score:.3f}")

        if results.page_level:
            print("\nPage Level:")
            print(f"  Precision: {results.page_level.precision:.3f}")
            print(f"  Recall: {results.page_level.recall:.3f}")
            print(f"  F1 Score: {results.page_level.f1_score:.3f}")
        else:
            print("\nPage Level: N/A (no page information available)")

        print("\nDocument Level:")
        print(f"  Precision: {results.document_level.precision:.3f}")
        print(f"  Recall: {results.document_level.recall:.3f}")
        print(f"  F1 Score: {results.document_level.f1_score:.3f}")

        return results

    def evaluate_retrieval_and_generation(
        self,
        retrieval_generation_function: Callable[[str], Tuple[List[str], str]],
        evaluation_name: Optional[str] = None,
    ) -> RetrievalAndGenerationResults:
        """
        Evaluate a retrieval + generation function against the benchmark.
        Generation evaluation requires OpenAI API key, but this still works without it
        (generation metrics will be 0.0).

        Args:
            retrieval_generation_function: Function that takes query string and returns tuple of (chunk_ids, generated_text)
            evaluation_name: Name to use for this function

        Returns:
            RetrievalAndGenerationResults with evaluation metrics
        """
        if not self.benchmark_entries:
            raise ValueError("No benchmark loaded. Generate or load benchmark first.")

        # Build meta_by_id if not available
        if not self.meta_by_id and self.benchmark_entries:
            print("Building metadata lookup from benchmark entries...")
            self.meta_by_id = {}
            for entry in self.benchmark_entries:
                if entry.chunk_ids:
                    for i, chunk_id in enumerate(entry.chunk_ids):
                        self.meta_by_id[chunk_id] = (
                            entry.page_nums,
                            entry.source_paths[0] if entry.source_paths else None,
                        )

        # default to function name if not provided
        if not evaluation_name:
            evaluation_name = retrieval_generation_function.__name__

        evaluator = Evaluator(
            self.benchmark_entries,
            meta_lookup=self.meta_by_id,
            openai_base_url=self.openai_base_url,
            openai_api_key=self.openai_api_key,
        )
        results = evaluator.evaluate_retrieval_and_generation(
            retrieval_generation_function, evaluation_name
        )

        print(f"\nEvaluation Results for {evaluation_name}:")
        print(f"Total Questions: {results.total_questions}")
        print("\nRetrieval Metrics:")
        print(
            f"  Chunk Level - P: {results.chunk_level.precision:.3f}, R: {results.chunk_level.recall:.3f}, F1: {results.chunk_level.f1_score:.3f}"
        )

        if results.page_level:
            print(
                f"  Page Level - P: {results.page_level.precision:.3f}, R: {results.page_level.recall:.3f}, F1: {results.page_level.f1_score:.3f}"
            )
        else:
            print("  Page Level - N/A (no page information available)")

        print(
            f"  Document Level - P: {results.document_level.precision:.3f}, R: {results.document_level.recall:.3f}, F1: {results.document_level.f1_score:.3f}"
        )
        print("\nGeneration Metrics:")
        print(f"  Accuracy: {results.generation_metrics.accuracy:.3f}")
        print(f"  Factuality: {results.generation_metrics.factuality:.3f}")

        return results

    def evaluate_generation_only(
        self,
        generation_function: Callable[[str], str],
        evaluation_name: Optional[str] = None,
    ) -> GenerationOnlyResults:
        """
        Evaluate a generation-only function against the benchmark.
        This requires OpenAI API key for generation evaluation.

        Args:
            generation_function: Function that takes query string and returns generated text
            evaluation_name: Name to use for this function

        Returns:
            GenerationOnlyResults with evaluation metrics
        """
        print(
            f"DEBUG: evaluate_generation_only called with {len(self.benchmark_entries)} entries"
        )

        if not self.benchmark_entries:
            raise ValueError("No benchmark loaded. Generate or load benchmark first.")

        # default to function name if not provided
        if not evaluation_name:
            evaluation_name = generation_function.__name__

        print(f"DEBUG: Creating Evaluator for generation-only evaluation")

        # For generation-only evaluation, meta_lookup is not needed
        evaluator = Evaluator(
            self.benchmark_entries,
            meta_lookup=None,  # Not needed for generation-only
            openai_base_url=self.openai_base_url,
            openai_api_key=self.openai_api_key,
        )

        print(f"DEBUG: Calling evaluator.evaluate_generation_only")
        results = evaluator.evaluate_generation_only(
            generation_function, evaluation_name
        )

        print(f"\nEvaluation Results for {evaluation_name}:")
        print(f"Total Questions: {results.total_questions}")
        print("\nGeneration Metrics:")
        print(f"  Accuracy: {results.generation_metrics.accuracy:.3f}")
        print(f"  Factuality: {results.generation_metrics.factuality:.3f}")

        return results
