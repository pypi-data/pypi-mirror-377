from ..analyzers.java_analyzer import JavaCSTAnalyzer
from .code_chunker import CodeChunker
from ..chunking_strategies.size_based_strategy import SizeBasedStrategy
from ..parsers.java_parser import JavaParser


def create_java_chunker(max_class_size: int = 2000) -> CodeChunker:
    """Factory function to create a Java code chunker."""
    parser = JavaParser()
    analyzer = JavaCSTAnalyzer(parser)
    strategy = SizeBasedStrategy(max_class_size)
    return CodeChunker(parser, analyzer, strategy)