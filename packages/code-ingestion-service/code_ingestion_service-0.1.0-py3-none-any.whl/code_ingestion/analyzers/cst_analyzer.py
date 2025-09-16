from abc import ABC, abstractmethod
from typing import List, Tuple

from tree_sitter import Tree

from ..data_models.class_info import ClassInfo
from ..parsers.code_parser import CodeParser


class CSTAnalyzer(ABC):
    """Abstract base class for CST analysis."""

    def __init__(self, parser: CodeParser):
        self.parser = parser

        # Shared REST API indicators across all languages

    REST_INDICATORS = [
        # Java Spring Boot
        "@RestController", "@Controller", "@RequestMapping",
        "@GetMapping", "@PostMapping", "@PutMapping", "@DeleteMapping",

        # Java JAX-RS
        "@Path", "@GET", "@POST", "@PUT", "@DELETE",

        # Python Flask
        "@app.route", "@blueprint.route",

        # Python FastAPI
        "@app.get", "@app.post", "@app.put", "@app.delete",

        # TypeScript/JavaScript (NestJS, Express decorators)
        "@Controller", "@Get", "@Post", "@Put", "@Delete",

        # Future frameworks can be added here without changing child classes
    ]

    # HTTP Method mapping
    METHOD_MAPPINGS = {
        "@GetMapping": "GET", "@PostMapping": "POST",
        "@PutMapping": "PUT", "@DeleteMapping": "DELETE",
        "@GET": "GET", "@POST": "POST", "@PUT": "PUT", "@DELETE": "DELETE"
    }

    def is_rest_api(self, annotations: List[str]) -> bool:
        """Check if annotations indicate REST API - shared across all languages"""
        for annotation in annotations:
            for indicator in self.REST_INDICATORS:
                if indicator in annotation:
                    return True
        return False

    @abstractmethod
    def extract_classes(self, tree: Tree, source_code: str) -> List[ClassInfo]:
        """Extract class information from CST."""
        pass

    @abstractmethod
    def extract_package_and_imports(self, tree: Tree, source_code: str) -> Tuple[str, List[str]]:
        """Extract package declaration and imports."""
        pass