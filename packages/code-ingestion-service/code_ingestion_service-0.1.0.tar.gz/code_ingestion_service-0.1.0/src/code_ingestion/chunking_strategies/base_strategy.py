from abc import ABC, abstractmethod

from ..data_models.class_info import ClassInfo


class BaseStrategy(ABC):
    """Abstract base class for chunking strategies."""

    @abstractmethod
    def should_split_class(self, class_info: ClassInfo, source_code: str) -> bool:
        """Determine if a class should be split into smaller chunks."""
        pass