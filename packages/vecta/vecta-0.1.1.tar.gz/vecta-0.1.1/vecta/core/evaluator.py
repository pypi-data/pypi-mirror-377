# vecta_backend/vecta/core/evaluator.py
"""Evaluation logic for retrieval performance metrics and generation quality assessment."""

from __future__ import annotations
import time
from typing import List, Set, Dict, Callable, Tuple, Optional, Any
import concurrent.futures
import json

from openai import OpenAI

from vecta.core.schemas import (
    BenchmarkEntry,
    EvaluationMetrics,
    BenchmarkResults,
    RetrievalAndGenerationResults,
    GenerationOnlyResults,
    GenerationMetrics,
    UsageInfo,
)


class Evaluator:
    """Evaluates retrieval function performance against benchmark using KB metadata."""

    def __init__(
        self,
        benchmark_entries: List[BenchmarkEntry],
        meta_lookup: Optional[
            Dict[str, Tuple[Optional[List[int]], Optional[str]]]
        ] = None,
        openai_api_key: Optional[str] = None,
        openai_base_url: str = "https://openrouter.ai/api/v1",
        model: str = "gpt-4o-mini",
        usage_service=None,
    ):
        """
        Args:
            benchmark_entries: entries to evaluate
            meta_lookup: Optional {chunk_id: (page_nums, source_path)} - required for retrieval evaluation
            openai_api_key: Optional key; if omitted, generation metrics default to 0.0
            openai_base_url: Base URL for OpenAI-compatible API (defaults to OpenRouter)
            model: Model to use for structured grading
            usage_service: TokenUsageService instance for tracking usage (backend only)
        """
        self.benchmark_entries = benchmark_entries
        self.meta_lookup = meta_lookup or {}
        self.openai_api_key = openai_api_key
        self.openai_base_url = openai_base_url
        self.model = model
        self.usage_service = usage_service
        self.total_usage = UsageInfo()
        self._client: Optional[Any] = None

        if self.openai_api_key and OpenAI is not None:
            try:
                self._client = OpenAI(
                    base_url=self.openai_base_url, api_key=self.openai_api_key
                )
            except Exception:
                self._client = None

    def evaluate_retrieval(
        self,
        retrieval_function: Callable[[str], List[str]],
        evaluation_name: str,
    ) -> BenchmarkResults:
        """Evaluate retrieval-only function performance."""
        if not self.meta_lookup:
            raise ValueError(
                "meta_lookup is required for retrieval evaluation and must contain {chunk_id: (page_nums, source_path)}"
            )

        start_time = time.time()

        chunk_metrics = self._evaluate_retrieval_level(
            retrieval_function=retrieval_function,
            get_ground_truth=lambda e: set(e.chunk_ids) if e.chunk_ids else set(),
            get_retrieved=lambda ids: set(ids),
        )

        page_metrics = self._evaluate_page_level(retrieval_function)

        doc_metrics = self._evaluate_retrieval_level(
            retrieval_function=retrieval_function,
            get_ground_truth=lambda e: set(e.source_paths) if e.source_paths else set(),
            get_retrieved=lambda ids: self._map_chunks_to_docs(ids),
        )

        end_time = time.time()
        duration_seconds = int(end_time - start_time)

        return BenchmarkResults(
            chunk_level=chunk_metrics,
            page_level=page_metrics,
            document_level=doc_metrics,
            total_questions=len(self.benchmark_entries),
            duration_seconds=duration_seconds,
            retrieval_evaluation_name=evaluation_name,
            usage_info=self.total_usage if self.total_usage.total_tokens > 0 else None,
        )

    def evaluate_retrieval_and_generation(
        self,
        retrieval_generation_function: Callable[[str], Tuple[List[str], str]],
        evaluation_name: str,
    ) -> RetrievalAndGenerationResults:
        """Evaluate a function that returns both retrieved chunk_ids and generated text."""
        if not self.meta_lookup:
            raise ValueError(
                "meta_lookup is required for retrieval+generation evaluation and must contain {chunk_id: (page_nums, source_path)}"
            )

        start_time = time.time()

        # Collect all results first
        all_results = []
        for entry in self.benchmark_entries:
            chunk_ids, gen_text = retrieval_generation_function(entry.question)
            all_results.append((entry, chunk_ids, gen_text))

        end_time = time.time()
        duration_seconds = int(end_time - start_time)

        # Compute retrieval metrics
        chunk_metrics = self._compute_retrieval_metrics(
            all_results,
            lambda e: set(e.chunk_ids) if e.chunk_ids else set(),
            lambda ids: set(ids),
        )

        page_metrics = self._compute_page_level_metrics(all_results)

        doc_metrics = self._compute_retrieval_metrics(
            all_results,
            lambda e: set(e.source_paths) if e.source_paths else set(),
            lambda ids: self._map_chunks_to_docs(ids),
        )

        # Compute generation metrics
        questions = [entry.question for entry, _, _ in all_results]
        expected_answers = [entry.answer for entry, _, _ in all_results]
        generated_answers = [gen_text for _, _, gen_text in all_results]

        accuracy, factuality = self._evaluate_generation_batch(
            questions, expected_answers, generated_answers
        )

        gen_metrics = GenerationMetrics(accuracy=accuracy, factuality=factuality)

        return RetrievalAndGenerationResults(
            chunk_level=chunk_metrics,
            page_level=page_metrics,
            document_level=doc_metrics,
            generation_metrics=gen_metrics,
            total_questions=len(self.benchmark_entries),
            duration_seconds=duration_seconds,
            retrieval_evaluation_name=evaluation_name,
            usage_info=self.total_usage if self.total_usage.total_tokens > 0 else None,
        )

    def evaluate_generation_only(
        self,
        generation_function: Callable[[str], str],
        evaluation_name: str,
    ) -> GenerationOnlyResults:
        """Evaluate generation-only quality (accuracy and factuality) versus expected answers."""

        questions: List[str] = []
        expected_answers: List[str] = []
        generated_answers: List[str] = []

        start_time = time.time()

        for entry in self.benchmark_entries:
            questions.append(entry.question)
            expected_answers.append(entry.answer)
            generated_answers.append(generation_function(entry.question))

        end_time = time.time()
        duration_seconds = int(end_time - start_time)

        accuracy, factuality = self._evaluate_generation_batch(
            questions, expected_answers, generated_answers
        )

        gen_metrics = GenerationMetrics(accuracy=accuracy, factuality=factuality)

        return GenerationOnlyResults(
            generation_metrics=gen_metrics,
            total_questions=len(self.benchmark_entries),
            duration_seconds=duration_seconds,
            retrieval_evaluation_name=evaluation_name,
            usage_info=self.total_usage if self.total_usage.total_tokens > 0 else None,
        )

    def _evaluate_retrieval_level(
        self,
        retrieval_function: Callable[[str], List[str]],
        get_ground_truth: Callable[[BenchmarkEntry], Set[Any]],
        get_retrieved: Callable[[List[str]], Set[Any]],
    ) -> EvaluationMetrics:
        """Evaluate at a specific granularity level."""
        total_precision = 0.0
        total_recall = 0.0
        total_f1 = 0.0

        for entry in self.benchmark_entries:
            retrieved_chunk_ids = retrieval_function(entry.question)
            ground_truth = get_ground_truth(entry)
            retrieved = get_retrieved(retrieved_chunk_ids)

            precision, recall, f1 = self._calculate_metrics(ground_truth, retrieved)
            total_precision += precision
            total_recall += recall
            total_f1 += f1

        n = len(self.benchmark_entries) or 1
        return EvaluationMetrics(
            precision=total_precision / n,
            recall=total_recall / n,
            f1_score=total_f1 / n,
        )

    def _evaluate_page_level(
        self, retrieval_function: Callable[[str], List[str]]
    ) -> Optional[EvaluationMetrics]:
        """Evaluate page-level retrieval with overlap logic."""
        # Check if any benchmark entries have page information
        has_page_info = any(
            entry.page_nums and len(entry.page_nums) > 0
            for entry in self.benchmark_entries
        )

        if not has_page_info:
            return None

        total_precision = 0.0
        total_recall = 0.0
        total_f1 = 0.0
        valid_entries = 0

        for entry in self.benchmark_entries:
            # Skip entries without page information
            if not entry.page_nums or not entry.source_paths:
                continue

            valid_entries += 1
            retrieved_chunk_ids = retrieval_function(entry.question)

            # Ground truth: set of (source_path, page_num) for each expected page
            ground_truth_pages = set()
            for source_path in entry.source_paths:
                for page_num in entry.page_nums:
                    ground_truth_pages.add((source_path, page_num))

            # Retrieved: pages from retrieved chunks with overlap logic
            retrieved_pages = self._map_chunks_to_pages_with_overlap(
                retrieved_chunk_ids, entry
            )

            precision, recall, f1 = self._calculate_metrics(
                ground_truth_pages, retrieved_pages
            )
            total_precision += precision
            total_recall += recall
            total_f1 += f1

        if valid_entries == 0:
            return None

        n = valid_entries
        return EvaluationMetrics(
            precision=total_precision / n,
            recall=total_recall / n,
            f1_score=total_f1 / n,
        )

    def _compute_retrieval_metrics(
        self,
        all_results: List[Tuple[BenchmarkEntry, List[str], str]],
        get_ground_truth: Callable[[BenchmarkEntry], Set[Any]],
        get_retrieved: Callable[[List[str]], Set[Any]],
    ) -> EvaluationMetrics:
        """Compute retrieval metrics for a batch of results."""
        total_precision = 0.0
        total_recall = 0.0
        total_f1 = 0.0

        for entry, chunk_ids, _ in all_results:
            ground_truth = get_ground_truth(entry)
            retrieved = get_retrieved(chunk_ids)

            precision, recall, f1 = self._calculate_metrics(ground_truth, retrieved)
            total_precision += precision
            total_recall += recall
            total_f1 += f1

        n = len(all_results) or 1
        return EvaluationMetrics(
            precision=total_precision / n,
            recall=total_recall / n,
            f1_score=total_f1 / n,
        )

    def _compute_page_level_metrics(
        self, all_results: List[Tuple[BenchmarkEntry, List[str], str]]
    ) -> Optional[EvaluationMetrics]:
        """Compute page-level metrics with overlap logic for batch results."""
        # Check if any benchmark entries have page information
        has_page_info = any(
            entry.page_nums and len(entry.page_nums) > 0 for entry, _, _ in all_results
        )

        if not has_page_info:
            return None

        total_precision = 0.0
        total_recall = 0.0
        total_f1 = 0.0
        valid_entries = 0

        for entry, chunk_ids, _ in all_results:
            # Skip entries without page information
            if not entry.page_nums or not entry.source_paths:
                continue

            valid_entries += 1

            # Ground truth: set of (source_path, page_num) for each expected page
            ground_truth_pages = set()
            for source_path in entry.source_paths:
                for page_num in entry.page_nums:
                    ground_truth_pages.add((source_path, page_num))

            # Retrieved: pages from retrieved chunks with overlap logic
            retrieved_pages = self._map_chunks_to_pages_with_overlap(chunk_ids, entry)

            precision, recall, f1 = self._calculate_metrics(
                ground_truth_pages, retrieved_pages
            )
            total_precision += precision
            total_recall += recall
            total_f1 += f1

        if valid_entries == 0:
            return None

        n = valid_entries
        return EvaluationMetrics(
            precision=total_precision / n,
            recall=total_recall / n,
            f1_score=total_f1 / n,
        )

    def _evaluate_generation_batch(
        self,
        questions: List[str],
        expected_answers: List[str],
        generated_answers: List[str],
    ) -> Tuple[float, float]:
        """Evaluate generation quality using structured LLM outputs with batch processing."""
        if not self._client:
            return 0.0, 0.0

        all_accuracy: List[float] = []
        all_factuality: List[float] = []
        batch_size = 8

        # Process in batches of 8
        for i in range(0, len(questions), batch_size):
            batch_questions = questions[i : i + batch_size]
            batch_expected = expected_answers[i : i + batch_size]
            batch_generated = generated_answers[i : i + batch_size]

            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                futures = []
                for q, e, g in zip(batch_questions, batch_expected, batch_generated):
                    future = executor.submit(self._evaluate_generation_single, q, e, g)
                    futures.append(future)

                # Collect results
                for future in concurrent.futures.as_completed(futures, timeout=120):
                    try:
                        acc, fac = future.result(timeout=30)
                        all_accuracy.append(acc)
                        all_factuality.append(fac)
                    except Exception:
                        all_accuracy.append(0.0)
                        all_factuality.append(0.0)

        n = len(all_accuracy) or 1
        return sum(all_accuracy) / n, sum(all_factuality) / n

    def _evaluate_generation_single(
        self, question: str, expected_answer: str, generated_answer: str
    ) -> Tuple[float, float]:
        """Evaluate single generation with structured output."""
        if not self._client:
            return 0.0, 0.0

        system_prompt = (
            "You are an expert evaluator assessing AI-generated answers. "
            "Score ACCURACY (match to expected answer) and FACTUALITY "
            "(consistency, no invented facts). "
            'Return JSON: {"accuracy_score": 0.0-1.0, "factuality_score": 0.0-1.0}.'
        )

        user_prompt = (
            f"Question: {question[:200]}...\n\n"
            f"Expected: {expected_answer[:200]}...\n\n"
            f"Generated: {generated_answer[:200]}...\n\n"
            "Evaluate accuracy (vs expected) and factuality (self-consistent, no unsupported claims)."
        )

        # Check usage limit if service is available
        if self.usage_service:
            estimated_tokens = self.usage_service.estimate_tokens(
                system_prompt + user_prompt
            )
            self.usage_service.check_usage_limit(estimated_tokens)

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "generation_evaluation",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "accuracy_score": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1,
                                },
                                "factuality_score": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1,
                                },
                            },
                            "required": [
                                "accuracy_score",
                                "factuality_score",
                            ],
                            "additionalProperties": False,
                        },
                    },
                },
                timeout=20,
                max_tokens=500,
            )

            # Track usage
            if response.usage and self.usage_service:
                usage_info = UsageInfo(
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                )
                self.usage_service.log_usage(usage_info)

            content = response.choices[0].message.content
            if content is None:
                return 0.0, 0.0

            data = json.loads(content)
            acc = float(data.get("accuracy_score", 0.0))
            fac = float(data.get("factuality_score", 0.0))
            return acc, fac

        except Exception:
            return 0.0, 0.0

    @staticmethod
    def _calculate_metrics(
        ground_truth: Set[Any], retrieved: Set[Any]
    ) -> Tuple[float, float, float]:
        """Calculate precision, recall, and F1 score."""
        if not retrieved or not ground_truth:
            return 0.0, 0.0, 0.0
        inter = ground_truth & retrieved
        precision = len(inter) / len(retrieved)
        recall = len(inter) / len(ground_truth)
        f1 = (
            0.0
            if (precision + recall == 0)
            else 2 * precision * recall / (precision + recall)
        )
        return precision, recall, f1

    def _map_chunks_to_pages_with_overlap(
        self, chunk_ids: List[str], entry: BenchmarkEntry
    ) -> Set[Tuple[str, int]]:
        """Map retrieved chunk IDs to (source_path, page_num) tuples with overlap logic."""
        retrieved_pages = set()

        # Get expected pages for this entry
        expected_pages = set()
        if entry.source_paths and entry.page_nums:
            for expected_source_path in entry.source_paths:
                for page_num in entry.page_nums:
                    expected_pages.add((expected_source_path, page_num))

        for cid in chunk_ids:
            if cid not in self.meta_lookup:
                continue
            page_nums, source_path = self.meta_lookup[cid]
            if page_nums is None or source_path is None:
                continue

            # Check if any of this chunk's pages overlap with expected pages for the same document
            chunk_pages = {(source_path, p) for p in page_nums}
            expected_for_doc = {(d, p) for d, p in expected_pages if d == source_path}

            # If there's overlap, include the overlapping pages
            overlap = chunk_pages & expected_for_doc
            if overlap:
                retrieved_pages.update(overlap)

        return retrieved_pages

    def _map_chunks_to_docs(self, chunk_ids: List[str]) -> Set[str]:
        """Map retrieved chunk IDs to document names."""
        out: Set[str] = set()
        for cid in chunk_ids:
            if cid not in self.meta_lookup:
                continue
            _, source_path = self.meta_lookup[cid]
            if source_path is None:
                continue
            out.add(source_path)
        return out
