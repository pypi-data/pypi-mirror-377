from abc import ABC, abstractmethod
from typing import List

from ..data_models.code_chunk import CodeChunk


class BaseVectorStore(ABC):
    """Abstract base class for vector stores - keep it simple."""

    @abstractmethod
    def store_chunks(self, chunks: List[CodeChunk], embeddings: List[List[float]]) -> List[str]:
        """Store code chunks with their embeddings. Return stored IDs."""
        pass