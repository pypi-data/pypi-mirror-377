# vecta_backend/vecta/core/question_generator.py
"""LLM-based synthetic question generation with structured outputs."""

import concurrent.futures
from typing import List, Tuple, Optional
from openai import OpenAI

from vecta.core.schemas import (
    ChunkData,
    SyntheticQuestion,
    QuestionEvaluation,
    UsageInfo,
)


class QuestionGenerator:
    """Generates synthetic questions using LLM with structured outputs."""

    def __init__(
        self,
        openai_api_key: str,
        openai_base_url: str = "https://openrouter.ai/api/v1",
        model: str = "google/gemini-2.5-flash-lite",
        usage_service=None,
    ):
        """
        Initialize the question generator.

        Args:
            openai_api_key: OpenAI API key
            openai_base_url: OpenAI base URL
            model: OpenAI model to use for generation
            usage_service: TokenUsageService instance for tracking usage (backend only)
        """
        self.client = OpenAI(base_url=openai_base_url, api_key=openai_api_key)
        self.model = model
        self.usage_service = usage_service
        self.total_usage = UsageInfo()

    def generate_question_for_chunk(self, chunk: ChunkData) -> SyntheticQuestion:
        """
        Generate a synthetic question that can be answered by the specific chunk.

        Args:
            chunk: The chunk to generate a question for

        Returns:
            SyntheticQuestion with question, answer, and reasoning
        """
        system_prompt = """You are an expert at creating technical questions based on document content.
        
Your task is to generate a specific, technical question that can ONLY be answered using the information 
provided in the given text chunk. The question should:
1. Be specific and detailed
2. Require the exact information in this chunk to answer
3. Not be answerable from general knowledge alone
4. Focus on facts, procedures, or specific details mentioned in the text

Generate a question that someone would need this specific chunk to answer correctly."""

        user_prompt = f"""Based on this text chunk, generate a technical question:

Text chunk:
{chunk.content}

Additional context - Source: {chunk.source_path}, Pages: {chunk.page_nums}

Create a question that requires the specific information in this chunk to answer."""

        # Check usage limit if service is available
        if self.usage_service:
            estimated_tokens = self.usage_service.estimate_tokens(
                system_prompt + user_prompt
            )
            self.usage_service.check_usage_limit(estimated_tokens)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "synthetic_question",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "question": {
                                    "type": "string",
                                    "description": "The technical question generated from the chunk",
                                },
                                "answer": {
                                    "type": "string",
                                    "description": "The answer that can be derived from the chunk",
                                },
                                "reasoning": {
                                    "type": "string",
                                    "description": "Explanation of how the chunk answers the question",
                                },
                            },
                            "required": ["question", "answer", "reasoning"],
                            "additionalProperties": False,
                        },
                    },
                },
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
                raise ValueError("No content returned from OpenAI")

            import json

            result_data = json.loads(content)
            return SyntheticQuestion(**result_data)

        except Exception as e:
            raise RuntimeError(f"Failed to generate question for chunk {chunk.id}: {e}")

    def generate_questions_batch(
        self, chunks: List[ChunkData]
    ) -> List[Tuple[ChunkData, SyntheticQuestion]]:
        """
        Generate questions for multiple chunks in parallel batches.

        Args:
            chunks: List of chunks to generate questions for

        Returns:
            List of tuples containing (chunk, synthetic_question)
        """
        results = []
        batch_size = 16

        def generate_single(chunk: ChunkData) -> Tuple[ChunkData, SyntheticQuestion]:
            question = self.generate_question_for_chunk(chunk)
            return (chunk, question)

        # Process chunks in batches of 16
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]

            with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
                # Submit all tasks in the current batch
                future_to_chunk = {
                    executor.submit(generate_single, chunk): chunk for chunk in batch
                }

                # Collect results as they complete
                for future in concurrent.futures.as_completed(future_to_chunk):
                    chunk = future_to_chunk[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        print(
                            f"Warning: Failed to generate question for chunk {chunk.id}: {e}"
                        )
                        continue

        return results

    def evaluate_chunk_for_question(
        self, question: str, chunk: ChunkData
    ) -> QuestionEvaluation:
        """
        Evaluate whether a chunk can answer a specific question.

        Args:
            question: The question to evaluate
            chunk: The chunk to check

        Returns:
            QuestionEvaluation with assessment
        """
        system_prompt = """You are an expert evaluator determining if a text chunk can directly answer a specific question.

Your task is to determine if the given text chunk contains sufficient information to directly answer the question. 

Consider:
1. Does the chunk contain the specific facts/information needed?
2. Can the query be answered completely using only this chunk?
3. Are there any critical details missing that would prevent a complete answer?

Be strict in your evaluation - only return true if the chunk truly contains enough information for a complete, accurate answer."""

        user_prompt = f"""<Query>{question}</Query>
<Chunk source_path="{chunk.source_path}" page_nums="{chunk.page_nums}">
{chunk.content}
</Chunk>

Can this chunk directly and completely answer the query?"""

        # Check usage limit if service is available
        if self.usage_service:
            estimated_tokens = self.usage_service.estimate_tokens(
                system_prompt + user_prompt
            )
            self.usage_service.check_usage_limit(estimated_tokens)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "question_evaluation",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "can_answer": {
                                    "type": "boolean",
                                    "description": "Whether this chunk can directly answer the question",
                                },
                                "confidence": {
                                    "type": "number",
                                    "description": "Confidence score between 0-1",
                                    "minimum": 0,
                                    "maximum": 1,
                                },
                                "reasoning": {
                                    "type": "string",
                                    "description": "Explanation for the evaluation decision",
                                },
                            },
                            "required": ["can_answer", "confidence", "reasoning"],
                            "additionalProperties": False,
                        },
                    },
                },
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
                raise ValueError("No content returned from OpenAI")

            import json

            result_data = json.loads(content)
            return QuestionEvaluation(**result_data)

        except Exception as e:
            raise RuntimeError(f"Failed to evaluate chunk {chunk.id} for question: {e}")

    def evaluate_chunks_batch(
        self, evaluation_tasks: List[Tuple[str, ChunkData]]
    ) -> List[Tuple[str, ChunkData, QuestionEvaluation]]:
        """
        Evaluate multiple chunks for questions in parallel batches.

        Args:
            evaluation_tasks: List of (question, chunk) tuples to evaluate

        Returns:
            List of tuples containing (question, chunk, evaluation_result)
        """
        results = []
        batch_size = 16

        def evaluate_single(
            task: Tuple[str, ChunkData],
        ) -> Tuple[str, ChunkData, QuestionEvaluation]:
            question, chunk = task
            evaluation = self.evaluate_chunk_for_question(question, chunk)
            return (question, chunk, evaluation)

        # Process evaluation tasks in batches of 16
        for i in range(0, len(evaluation_tasks), batch_size):
            batch = evaluation_tasks[i : i + batch_size]

            with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
                # Submit all tasks in the current batch
                future_to_task = {
                    executor.submit(evaluate_single, task): task for task in batch
                }

                # Collect results as they complete
                for future in concurrent.futures.as_completed(future_to_task):
                    task = future_to_task[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        question, chunk = task
                        print(
                            f"Warning: Failed to evaluate chunk {chunk.id} for question: {e}"
                        )
                        continue

        return results
