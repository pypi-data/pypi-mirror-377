from ..chunking_strategies.base_strategy import BaseStrategy
from ..data_models.class_info import ClassInfo


class SizeBasedStrategy(BaseStrategy):
    """Size-based chunking strategy."""

    def __init__(self, max_class_size: int = 2000):
        self.max_class_size = max_class_size

    def should_split_class(self, class_info: ClassInfo, source_code: str) -> bool:
        """Split class if it exceeds size threshold."""
        class_text = source_code[class_info.node.start_byte:class_info.node.end_byte]
        return len(class_text) > self.max_class_size