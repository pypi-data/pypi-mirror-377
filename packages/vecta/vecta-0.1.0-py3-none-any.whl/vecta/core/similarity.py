"""Utilities for similarity search and deduplication using OpenAI embeddings."""

import os
from typing import List, Tuple, Dict, Optional, cast
import numpy as np
from openai import OpenAI

from vecta.core.schemas import ChunkData
from vecta.connectors.base import BaseVectorDBConnector


class EmbeddingSimilaritySearcher:
    """Utility class for finding similar chunks using OpenAI vector embeddings."""

    def __init__(
        self,
        connector: BaseVectorDBConnector,
        base_url: str = "https://api.openai.com/v1",
        api_key: Optional[str] = os.getenv("OPENAI_API_KEY"),
        embedding_model: str = "text-embedding-3-small",
    ):
        """
        Initialize with a vector database connector and OpenAI client for embedding-based similarity search.

        Args:
            connector: Vector database connector for similarity search
            base_url: OpenAI API base URL
            api_key: OpenAI API key
            embedding_model: OpenAI embedding model to use
        """
        self.connector = connector
        self.openai_client = OpenAI(base_url=base_url, api_key=api_key)
        self.embedding_model = embedding_model
        self._embedding_cache: Dict[str, np.ndarray] = {}

    def get_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding vector for text using OpenAI API with caching.

        Args:
            text: Text to get embedding for

        Returns:
            Numpy array containing the embedding vector
        """
        # Check cache first
        if text in self._embedding_cache:
            return self._embedding_cache[text]

        # Clean text (remove newlines as recommended by OpenAI)
        cleaned_text = text.replace("\n", " ").strip()

        # Ensure text is not empty
        if not cleaned_text:
            cleaned_text = "empty"

        # Get embedding from OpenAI - pass as single string
        response = self.openai_client.embeddings.create(
            input=cleaned_text, model=self.embedding_model  # Pass as string, not list
        )

        embedding = np.array(response.data[0].embedding)

        # Cache the embedding
        self._embedding_cache[text] = embedding

        return embedding

    def find_similar_chunks(
        self,
        target_chunk: ChunkData,
        all_chunks: List[ChunkData],
        k: int = 10,
        similarity_threshold: float = 0.7,
    ) -> List[Tuple[ChunkData, float]]:
        """
        Find chunks similar to the target chunk using OpenAI embedding similarity.

        Args:
            target_chunk: The chunk to find similarities for
            all_chunks: List of all chunks to search through
            k: Maximum number of similar chunks to return
            similarity_threshold: Minimum similarity score to include

        Returns:
            List of tuples containing (similar_chunk, similarity_score)
        """
        # Get embedding for target chunk
        target_embedding = self.get_embedding(target_chunk.content)

        similar_chunks = []

        for chunk in all_chunks:
            # Skip the target chunk itself
            if chunk.id == target_chunk.id:
                continue

            # Get embedding for current chunk
            chunk_embedding = self.get_embedding(chunk.content)

            # Calculate cosine similarity using embeddings
            similarity = self._calculate_cosine_similarity(
                target_embedding, chunk_embedding
            )

            if similarity >= similarity_threshold:
                similar_chunks.append((chunk, similarity))

        # Sort by similarity score descending and take top k
        similar_chunks.sort(key=lambda x: x[1], reverse=True)
        return similar_chunks[:k]

    @staticmethod
    def _calculate_cosine_similarity(
        embedding1: np.ndarray, embedding2: np.ndarray
    ) -> float:
        """
        Calculate cosine similarity between two embedding vectors.

        Since OpenAI embeddings are normalized to length 1, we can use dot product
        for faster computation (cosine similarity = dot product for unit vectors).

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score between 0 and 1 (higher is more similar)
        """
        # For normalized vectors, cosine similarity = dot product
        return float(np.dot(embedding1, embedding2))

    def compute_similarity_matrix(self, chunks: List[ChunkData]) -> np.ndarray:
        """
        Compute pairwise similarity matrix for all chunks using OpenAI embeddings.

        Args:
            chunks: List of chunks

        Returns:
            Similarity matrix as numpy array (n x n where n = len(chunks))
        """
        # Get all embeddings efficiently using batch processing
        texts = [chunk.content for chunk in chunks]
        embeddings = self.batch_get_embeddings(texts)

        # Convert to numpy array for efficient computation
        embeddings_matrix = np.array(embeddings)

        # Compute cosine similarity matrix using matrix multiplication
        # Since OpenAI embeddings are normalized, cosine similarity = dot product
        similarity_matrix = np.dot(embeddings_matrix, embeddings_matrix.T)

        return similarity_matrix

    def batch_get_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """
        Get embeddings for multiple texts efficiently using batch API calls.

        Args:
            texts: List of texts to get embeddings for

        Returns:
            List of embedding vectors corresponding to input texts
        """
        embeddings: List[Optional[np.ndarray]] = []
        uncached_texts = []
        uncached_indices = []

        # Check cache and collect uncached texts
        for i, text in enumerate(texts):
            if text in self._embedding_cache:
                embeddings.append(self._embedding_cache[text])
            else:
                embeddings.append(None)  # Placeholder
                cleaned_text = text.replace("\n", " ").strip()
                # Ensure text is not empty
                if not cleaned_text:
                    cleaned_text = "empty"
                uncached_texts.append(cleaned_text)
                uncached_indices.append(i)

        # Get embeddings for uncached texts in batch
        if uncached_texts:
            # Process in smaller batches to avoid API limits
            batch_size = 100
            for batch_start in range(0, len(uncached_texts), batch_size):
                batch_end = min(batch_start + batch_size, len(uncached_texts))
                batch_texts = uncached_texts[batch_start:batch_end]
                batch_indices = uncached_indices[batch_start:batch_end]

                response = self.openai_client.embeddings.create(
                    input=batch_texts,  # Pass as list for batch processing
                    model=self.embedding_model,
                )

                # Cache and assign embeddings
                for i, embedding_data in enumerate(response.data):
                    embedding = np.array(embedding_data.embedding)
                    original_index = batch_indices[i]
                    original_text = texts[original_index]

                    # Cache the embedding
                    self._embedding_cache[original_text] = embedding

                    # Assign to result
                    embeddings[original_index] = embedding

        return cast(List[np.ndarray], embeddings)

    def find_most_similar_chunk(
        self, target_chunk: ChunkData, candidate_chunks: List[ChunkData]
    ) -> Tuple[ChunkData, float]:
        """
        Find the single most similar chunk to the target.

        Args:
            target_chunk: The chunk to find similarities for
            candidate_chunks: List of chunks to compare against

        Returns:
            Tuple of (most_similar_chunk, similarity_score)
        """
        if not candidate_chunks:
            raise ValueError("No candidate chunks provided")

        similar_chunks = self.find_similar_chunks(
            target_chunk, candidate_chunks, k=1, similarity_threshold=0.0
        )

        if not similar_chunks:
            # Return the first chunk with 0 similarity if none meet threshold
            target_embedding = self.get_embedding(target_chunk.content)
            first_chunk = candidate_chunks[0]
            first_embedding = self.get_embedding(first_chunk.content)
            similarity = self._calculate_cosine_similarity(
                target_embedding, first_embedding
            )
            return (first_chunk, similarity)

        return similar_chunks[0]

    def clear_embedding_cache(self):
        """Clear the embedding cache to free memory."""
        self._embedding_cache.clear()

    @property
    def cache_size(self) -> int:
        """Get the current size of the embedding cache."""
        return len(self._embedding_cache)

    def precompute_embeddings(self, chunks: List[ChunkData]) -> Dict[str, np.ndarray]:
        """
        Precompute embeddings for a list of chunks for faster similarity computation.

        Args:
            chunks: List of chunks to precompute embeddings for

        Returns:
            Dictionary mapping chunk IDs to their embeddings
        """
        texts = [chunk.content for chunk in chunks]
        embeddings = self.batch_get_embeddings(texts)

        return {chunk.id: embedding for chunk, embedding in zip(chunks, embeddings)}
