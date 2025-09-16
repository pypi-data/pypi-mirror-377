from abc import ABC, abstractmethod
from typing import List


class BaseEmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    def embed_chunks(self, texts: List[str]) -> List[List[float]]:
        """Convert text chunks to embedding vectors."""
        pass

    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """Return the dimension of the embedding vectors."""
        pass