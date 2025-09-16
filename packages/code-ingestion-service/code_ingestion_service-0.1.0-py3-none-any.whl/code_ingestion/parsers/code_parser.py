from abc import ABC, abstractmethod
from typing import Tuple

from tree_sitter import Parser, Tree, Node

from ..enums.programming_language import ProgrammingLanguage


class CodeParser(ABC):
    """Abstract base class for language-specific code parsers."""

    def __init__(self, language: ProgrammingLanguage):
        self.language = language
        self.parser = self._create_parser()

    @abstractmethod
    def _create_parser(self) -> Parser:
        """Create language-specific parser."""
        pass

    def parse(self, source_code: str) -> Tree:
        """Parse source code into CST."""
        return self.parser.parse(source_code.encode('utf-8'))

    def extract_text(self, node: Node, source_code: str) -> str:
        """Extract text content from a node."""
        return node.text.decode('utf-8')

    def get_line_numbers(self, node: Node) -> Tuple[int, int]:
        """Get start and end line numbers for a node."""
        return node.start_point[0] + 1, node.end_point[0] + 1
