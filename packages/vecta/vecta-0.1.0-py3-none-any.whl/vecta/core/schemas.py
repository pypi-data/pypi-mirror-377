# vecta_backend/vecta/core/schemas.py
"""Pydantic schemas for Vecta."""

import json
from typing import List, Optional, Dict, Any, Callable, Tuple, Union
from pydantic import BaseModel, Field
from enum import Enum
import uuid
from jsonpath_ng import parse as jsonpath_parse  # type: ignore[import-untyped]
from jsonpath_ng.ext import parse as jsonpath_ext_parse  # type: ignore[import-untyped]


class VectorDBType(str, Enum):
    """Supported vector database types."""

    CHROMA_LOCAL = "chroma_local"
    CHROMA_CLOUD = "chroma_cloud"
    PINECONE = "pinecone"
    PGVECTOR = "pgvector"
    AZURE = "azure"
    AZURE_COSMOS = "azure_cosmos"
    DATABRICKS = "databricks"
    LANGCHAIN = "langchain"
    LLAMA_INDEX = "llama_index"
    WEAVIATE = "weaviate"


class EvaluationType(str, Enum):
    """Supported evaluation types."""

    RETRIEVAL_ONLY = "retrieval_only"
    RETRIEVAL_AND_GENERATION = "retrieval_and_generation"
    GENERATION_ONLY = "generation_only"


class DataAccessor:
    """Utility class for extracting data from various data structures using path-like syntax."""

    @staticmethod
    def extract(data: Any, accessor_path: str) -> Any:
        """
        Extract data using accessor path syntax with JSON parsing support.

        Supported syntax:
        - "field_name" - direct field access
        - ".property_name" - property access
        - "[0]" - index access
        - "field.subfield" - nested field access
        - "[0].property" - mixed access
        - "metadata.source.filename" - deep nesting
        - "json(field_path).subfield" - parse field as JSON then access subfield
        - "json(json(field_path).subfield).final_field" - nested JSON parsing

        Args:
            data: The data structure to extract from
            accessor_path: Path string defining how to access the data

        Returns:
            Extracted value or None if path doesn't exist
        """
        if not accessor_path:
            return None

        try:
            # Handle JSON parsing syntax: json(field_path).remaining_path
            if "json(" in accessor_path:
                return DataAccessor._extract_with_json_parsing(data, accessor_path)

            # Regular path parsing
            current = data
            path_parts = DataAccessor._parse_accessor_path(accessor_path)

            for i, part in enumerate(path_parts):
                if part.startswith("[") and part.endswith("]"):
                    # Index access
                    index = int(part[1:-1])
                    if isinstance(current, (list, tuple)):
                        if index < len(current):
                            current = current[index]
                        else:
                            return None
                    else:
                        return None
                elif part.startswith("."):
                    # Property access - try dict access first, then property access
                    prop_name = part[1:]

                    # For dictionaries, try dict key access first
                    if isinstance(current, dict):
                        if prop_name in current:
                            current = current[prop_name]
                        else:
                            return None
                    # For objects, try property access
                    elif hasattr(current, prop_name):
                        current = getattr(current, prop_name)
                    else:
                        return None
                else:
                    # Field access
                    if isinstance(current, dict):
                        if part in current:
                            current = current.get(part)
                        else:
                            return None
                    elif hasattr(current, part):
                        current = getattr(current, part)
                    else:
                        return None

                if current is None:
                    return None

            return current

        except (KeyError, IndexError, AttributeError, ValueError, TypeError):
            return None

    @staticmethod
    def _extract_with_json_parsing(data: Any, accessor_path: str) -> Any:
        """Handle nested JSON parsing in accessor paths."""
        try:
            current = data
            remaining_path = accessor_path

            # Process nested json() calls
            while "json(" in remaining_path:
                # Find the first json() pattern
                json_start = remaining_path.find("json(")
                if json_start == -1:
                    break

                # Find the matching closing parenthesis
                paren_count = 0
                json_end = -1
                for i in range(json_start + 5, len(remaining_path)):
                    if remaining_path[i] == "(":
                        paren_count += 1
                    elif remaining_path[i] == ")":
                        if paren_count == 0:
                            json_end = i
                            break
                        paren_count -= 1

                if json_end == -1:
                    return None

                # Extract the path inside json()
                json_field_path = remaining_path[json_start + 5 : json_end]

                # Get the JSON field value
                json_value = DataAccessor.extract(current, json_field_path)

                if json_value is None:
                    return None

                # Parse as JSON if it's a string
                if isinstance(json_value, str):
                    try:
                        parsed_json = json.loads(json_value)
                    except json.JSONDecodeError:
                        return None
                else:
                    # Already parsed or not a string
                    parsed_json = json_value

                # Update current to the parsed JSON
                current = parsed_json

                # Update remaining path - remove the json() part
                before_json = remaining_path[:json_start]
                after_json = remaining_path[json_end + 1 :]

                # If there's a dot after the json(), remove it
                if after_json.startswith("."):
                    after_json = after_json[1:]

                remaining_path = before_json + after_json

                # If we've processed all json() calls and have remaining path
                if "json(" not in remaining_path and remaining_path:
                    return DataAccessor.extract(current, remaining_path)

            # If no more json() calls and no remaining path, return current
            if not remaining_path:
                return current
            else:
                return DataAccessor.extract(current, remaining_path)

        except (ValueError, TypeError, json.JSONDecodeError):
            return None

    @staticmethod
    def _parse_accessor_path(accessor_path: str) -> List[str]:
        """Parse accessor path into individual components."""
        parts = []
        current_part = ""
        i = 0

        while i < len(accessor_path):
            char = accessor_path[i]

            if char == ".":
                if current_part:
                    parts.append(current_part)
                    current_part = ""
                # Start property access
                if i + 1 < len(accessor_path) and accessor_path[i + 1] != "[":
                    current_part = "."
                i += 1
            elif char == "[":
                if current_part:
                    parts.append(current_part)
                    current_part = ""
                # Find closing bracket
                bracket_end = accessor_path.find("]", i)
                if bracket_end != -1:
                    parts.append(accessor_path[i : bracket_end + 1])
                    i = bracket_end + 1
                else:
                    current_part += char
                    i += 1
            else:
                current_part += char
                i += 1

        if current_part:
            parts.append(current_part)

        return parts


class VectorDBSchema(BaseModel):
    """Defines how to extract data from vector database results."""

    # Core field accessors - these define how to get basic chunk data
    id_accessor: str  # e.g., "id", ".id", "[0]", "metadata.chunk_id"
    content_accessor: str  # e.g., "content", ".content", "[1]", "text", "metadata.text"

    # Optional metadata accessor if metadata exists as a separate field
    metadata_accessor: Optional[str] = None  # e.g., "metadata", ".metadata", "[2]"

    # Source information accessors - support JSON parsing
    source_path_accessor: str  # e.g., "metadata.source_path", "json(metadata).source_path", "filename", "[3]"
    page_nums_accessor: Optional[str] = (
        None  # e.g., "metadata.page_nums", "json(metadata).page_nums", "pages", "[4]"
    )

    # Default values when extraction fails
    source_path_default: str = "unknown"
    page_nums_default: Optional[List[int]] = None

    # Additional field accessors for custom fields the user might need
    additional_accessors: Dict[str, str] = Field(default_factory=dict)

    def extract_chunk_data(self, raw_result: Any) -> Dict[str, Any]:
        """
        Extract chunk data from a raw database result using the schema.

        Args:
            raw_result: Raw result from database query (could be dict, object, list, etc.)

        Returns:
            Dictionary with extracted data that can be used to create ChunkData
        """
        # Extract core fields
        chunk_id = DataAccessor.extract(raw_result, self.id_accessor)
        content = DataAccessor.extract(raw_result, self.content_accessor)

        # Extract metadata if specified
        metadata = {}
        if self.metadata_accessor:
            extracted_metadata = DataAccessor.extract(
                raw_result, self.metadata_accessor
            )
            if isinstance(extracted_metadata, dict):
                metadata = extracted_metadata
            elif isinstance(extracted_metadata, str):
                # Try to parse as JSON
                try:
                    metadata = json.loads(extracted_metadata)
                except json.JSONDecodeError:
                    metadata = {"raw_metadata": extracted_metadata}
            elif extracted_metadata is not None:
                # Convert non-dict metadata to dict
                metadata = {"raw_metadata": extracted_metadata}

        # Extract source information
        source_path = DataAccessor.extract(raw_result, self.source_path_accessor)
        if source_path is None:
            source_path = self.source_path_default

        page_nums = None
        if self.page_nums_accessor:
            page_nums = DataAccessor.extract(raw_result, self.page_nums_accessor)
            page_nums = self._normalize_page_nums(page_nums)
        if page_nums is None:
            page_nums = self.page_nums_default

        # Create accessible data structure for any additional processing
        accessible_data = {
            "id": chunk_id,
            "content": content,
            "metadata": metadata,
            "source_path": source_path,
            "page_nums": page_nums,
            "raw_result": raw_result,
        }

        # Add additional accessible fields
        for field_name, accessor in self.additional_accessors.items():
            accessible_data[field_name] = DataAccessor.extract(raw_result, accessor)

        return {
            "id": str(chunk_id) if chunk_id is not None else "",
            "content": str(content) if content is not None else "",
            "metadata": metadata,
            "source_path": str(source_path),
            "page_nums": page_nums,
            "accessible_data": accessible_data,
        }

    def _normalize_page_nums(self, value: Any) -> Optional[List[int]]:
        """Normalize various page number formats to List[int]."""
        if value is None:
            return None

        if isinstance(value, list):
            try:
                return [int(x) for x in value if x is not None]
            except (ValueError, TypeError):
                return None
        elif isinstance(value, (int, str)):
            try:
                return [int(value)]
            except (ValueError, TypeError):
                return None

        return None


class UsageInfo(BaseModel):
    """Token usage information for LLM calls."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: Optional[float] = None


class ChunkData(BaseModel):
    """Represents a chunk of data from a vector database."""

    id: str
    content: str
    metadata: Dict[str, Any]
    source_path: str = "unknown"
    page_nums: Optional[List[int]] = None

    @classmethod
    def from_schema_extraction(
        cls, schema: VectorDBSchema, raw_result: Any
    ) -> "ChunkData":
        """Create ChunkData from raw database result using schema."""
        extracted = schema.extract_chunk_data(raw_result)

        return cls(
            id=extracted["id"],
            content=extracted["content"],
            metadata=extracted["metadata"],
            source_path=extracted["source_path"],
            page_nums=extracted["page_nums"],
        )

    @property
    def source_data(self) -> Dict[str, Any]:
        """Get the full source data."""
        return {"source_path": self.source_path, "page_nums": self.page_nums}


class SyntheticQuestion(BaseModel):
    """Generated synthetic question from LLM."""

    question: str = Field(description="The technical question generated from the chunk")
    answer: str = Field(description="The answer that can be derived from the chunk")
    reasoning: str = Field(
        description="Explanation of how the chunk answers the question"
    )


class QuestionEvaluation(BaseModel):
    """Evaluation of whether a chunk can answer a question."""

    can_answer: bool = Field(
        description="Whether this chunk can directly answer the question"
    )
    confidence: float = Field(description="Confidence score between 0-1", ge=0, le=1)
    reasoning: str = Field(description="Explanation for the evaluation decision")


class BenchmarkEntry(BaseModel):
    """A single entry in the benchmark dataset."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    answer: str
    chunk_ids: Optional[List[str]] = None
    page_nums: Optional[List[int]] = None
    source_paths: Optional[List[str]] = None


class EvaluationMetrics(BaseModel):
    """Evaluation metrics for retrieval performance."""

    precision: Optional[float] = Field(default=None, ge=0, le=1)
    recall: Optional[float] = Field(default=None, ge=0, le=1)
    f1_score: Optional[float] = Field(default=None, ge=0, le=1)


class GenerationMetrics(BaseModel):
    """Evaluation metrics for generation quality."""

    accuracy: float = Field(ge=0, le=1)
    factuality: float = Field(ge=0, le=1)


class BenchmarkResults(BaseModel):
    """Complete evaluation results for retrieval-only evaluation."""

    chunk_level: EvaluationMetrics
    page_level: Optional[EvaluationMetrics]
    document_level: EvaluationMetrics
    total_questions: int
    duration_seconds: Optional[int] = None
    retrieval_evaluation_name: Optional[str] = None
    usage_info: Optional[UsageInfo] = None


class RetrievalAndGenerationResults(BaseModel):
    """Complete evaluation results for retrieval + generation evaluation."""

    chunk_level: EvaluationMetrics
    page_level: Optional[EvaluationMetrics]
    document_level: EvaluationMetrics
    generation_metrics: GenerationMetrics
    total_questions: int
    duration_seconds: Optional[int] = None
    retrieval_evaluation_name: Optional[str] = None
    usage_info: Optional[UsageInfo] = None


class GenerationOnlyResults(BaseModel):
    """Complete evaluation results for generation-only evaluation."""

    generation_metrics: GenerationMetrics
    total_questions: int
    duration_seconds: Optional[int] = None
    retrieval_evaluation_name: Optional[str] = None
    usage_info: Optional[UsageInfo] = None


class RetrievalFunction(BaseModel):
    """Wrapper for retrieval function."""

    name: str
    function: Callable[[str], List[str]]

    class Config:
        arbitrary_types_allowed = True


class RetrievalAndGenerationFunction(BaseModel):
    """Wrapper for retrieval + generation function."""

    name: str
    function: Callable[[str], Tuple[List[str], str]]

    class Config:
        arbitrary_types_allowed = True


class GenerationOnlyFunction(BaseModel):
    """Wrapper for generation-only function."""

    name: str
    function: Callable[[str], str]

    class Config:
        arbitrary_types_allowed = True


class RenameRequest(BaseModel):
    """Payload for renaming a resource."""

    name: str


# Dataset-specific schemas for field mapping
class DatasetSchema(BaseModel):
    """Schema for mapping dataset fields to standard Vecta format."""

    question_accessor: str  # How to access the question field
    answer_accessor: str  # How to access the answer field
    context_accessor: Optional[str] = None  # How to access context/passages
    id_accessor: Optional[str] = None  # How to access unique ID
    supporting_facts_accessor: Optional[str] = None  # How to access supporting facts

    # Additional field accessors for dataset-specific fields
    additional_accessors: Dict[str, str] = Field(default_factory=dict)

    def extract_dataset_fields(self, raw_item: Any) -> Dict[str, Any]:
        """Extract standardized fields from a dataset item."""
        return {
            "question": DataAccessor.extract(raw_item, self.question_accessor),
            "answer": DataAccessor.extract(raw_item, self.answer_accessor),
            "context": (
                DataAccessor.extract(raw_item, self.context_accessor)
                if self.context_accessor
                else None
            ),
            "id": (
                DataAccessor.extract(raw_item, self.id_accessor)
                if self.id_accessor
                else None
            ),
            "supporting_facts": (
                DataAccessor.extract(raw_item, self.supporting_facts_accessor)
                if self.supporting_facts_accessor
                else None
            ),
            **{
                field_name: DataAccessor.extract(raw_item, accessor)
                for field_name, accessor in self.additional_accessors.items()
            },
        }
