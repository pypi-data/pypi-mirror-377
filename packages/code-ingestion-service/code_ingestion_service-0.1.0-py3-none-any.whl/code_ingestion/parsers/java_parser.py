import tree_sitter_java as tsjava
from tree_sitter import Parser, Language

from ..enums.programming_language import ProgrammingLanguage
from ..parsers.code_parser import CodeParser


class JavaParser(CodeParser):
    """Java-specific parser implementation."""

    def __init__(self):
        super().__init__(ProgrammingLanguage.JAVA)

    def _create_parser(self) -> Parser:
        java_language = Language(tsjava.language())
        return Parser(language=java_language)