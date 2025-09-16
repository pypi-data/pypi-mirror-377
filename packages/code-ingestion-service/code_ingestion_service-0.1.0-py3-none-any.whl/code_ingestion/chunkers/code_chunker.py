from typing import List

from ..analyzers.cst_analyzer import CSTAnalyzer
from ..chunking_strategies.base_strategy import BaseStrategy
from ..data_models.chunk_metadata import ChunkMetadata
from ..data_models.class_info import ClassInfo
from ..data_models.code_chunk import CodeChunk
from ..data_models.method_info import MethodInfo
from ..enums.chunk_type import ChunkType
from ..parsers.code_parser import CodeParser


class CodeChunker:
    """Main orchestrator for code chunking."""

    def __init__(self,
                 parser: CodeParser,
                 analyzer: CSTAnalyzer,
                 strategy: BaseStrategy):
        self.parser = parser
        self.analyzer = analyzer
        self.strategy = strategy

    def chunk_code(self,
                   source_code: str,
                   file_path: str = "",
                   repo_url: str = "") -> List[CodeChunk]:
        """Main method to chunk code based on the strategy."""
        tree = self.parser.parse(source_code)
        chunks = []

        # Single-pass CST extraction for optimal performance
        package, imports, classes = self.analyzer.extract_all_info(tree, source_code)
        file_name = file_path.split("/")[-1] if file_path else ""

        for class_info in classes:
            chunks.extend(self._process_class(
                class_info, source_code, package, imports,
                file_path, file_name, repo_url
            ))

        return chunks

    def _process_class(self,
                       class_info: ClassInfo,
                       source_code: str,
                       package: str,
                       imports: List[str],
                       file_path: str,
                       file_name: str,
                       repo_url: str) -> List[CodeChunk]:
        """Process a single class and decide chunking strategy."""
        chunks = []

        # Method-level context caching: build base context once per class
        base_context = self._build_context(package, imports)
        class_wrapper_start = f"public class {class_info.name} {{\n    // class header\n    \n"
        class_wrapper_end = "\n}"

        if not self.strategy.should_split_class(class_info, source_code):
            chunk = self._create_complete_class_chunk(
                class_info, source_code, base_context,
                file_path, file_name, repo_url
            )
            chunks.append(chunk)
        else:
            method_chunks = self._create_method_chunks(
                class_info, source_code, base_context, class_wrapper_start, class_wrapper_end,
                file_path, file_name, repo_url
            )
            chunks.extend(method_chunks)

        return chunks

    def _create_complete_class_chunk(self,
                                     class_info: ClassInfo,
                                     source_code: str,
                                     base_context: str,
                                     file_path: str,
                                     file_name: str,
                                     repo_url: str) -> CodeChunk:
        """Create a complete class chunk."""
        class_content = self.parser.extract_text(class_info.node, source_code)
        full_content = base_context + class_content

        metadata = ChunkMetadata(
            repo_url=repo_url,
            file_path=file_path,
            file_name=file_name,
            class_name=class_info.name,
            methods=[method.name for method in class_info.methods],
            fields=class_info.fields,
            chunk_type=ChunkType.COMPLETE_CLASS.value,
            chunk_size=len(full_content),
            start_line=class_info.start_line,
            end_line=class_info.end_line,
            language=self.parser.language.value,
            annotations=class_info.annotations,
            framework_type=class_info.framework_type,
            is_rest_controller=self.analyzer.is_rest_api(class_info.annotations),
            http_methods=[m.http_method for m in class_info.methods if m.http_method]
        )

        chunk_id = self._create_chunk_id(file_path, class_info.name)
        return CodeChunk(id=chunk_id, content=full_content, metadata=metadata)

    def _create_method_chunks(self,
                              class_info: ClassInfo,
                              source_code: str,
                              base_context: str,
                              class_wrapper_start: str,
                              class_wrapper_end: str,
                              file_path: str,
                              file_name: str,
                              repo_url: str) -> List[CodeChunk]:
        """Create method-level chunks."""
        chunks = []

        for method_info in class_info.methods:
            chunk = self._create_method_chunk(
                class_info, method_info, class_info.name, source_code, base_context, class_wrapper_start, class_wrapper_end,
                file_path, file_name, repo_url, ChunkType.METHOD
            )
            chunks.append(chunk)

        for constructor_info in class_info.constructors:
            chunk = self._create_method_chunk(class_info,
                constructor_info, class_info.name, source_code, base_context, class_wrapper_start, class_wrapper_end,
                file_path, file_name, repo_url, ChunkType.CONSTRUCTOR
            )
            chunks.append(chunk)

        return chunks

    def _create_method_chunk(self,
                             class_info: ClassInfo,
                             method_info: MethodInfo,
                             class_name: str,
                             source_code: str,
                             base_context: str,
                             class_wrapper_start: str,
                             class_wrapper_end: str,
                             file_path: str,
                             file_name: str,
                             repo_url: str,
                             chunk_type: ChunkType) -> CodeChunk:
        """Create a chunk for a single method."""
        method_content = self.parser.extract_text(method_info.node, source_code)

        # Use cached context parts to build method context efficiently
        indented_method = "    " + method_content.replace("\n", "\n    ")
        context = base_context + class_wrapper_start + indented_method + class_wrapper_end

        metadata = ChunkMetadata(
            repo_url=repo_url,
            file_path=file_path,
            file_name=file_name,
            class_name=class_name,
            method_name=method_info.name,
            signature=method_info.signature,
            return_type=method_info.return_type,
            chunk_type=chunk_type.value,
            chunk_size=len(context),
            start_line=method_info.start_line,
            end_line=method_info.end_line,
            language=self.parser.language.value,
            annotations=method_info.annotations,
            framework_type=class_info.framework_type,
            is_rest_controller=self.analyzer.is_rest_api(class_info.annotations),
            http_methods=[method_info.http_method] if method_info.http_method else [],
            api_path=method_info.api_path,
        )

        chunk_id = self._create_chunk_id(file_path, class_name, method_info.name)
        return CodeChunk(id=chunk_id, content=context, metadata=metadata)

    def _build_context(self, package: str, imports: List[str]) -> str:
        """Build package and import context."""
        context = ""
        if package:
            context += package + "\n"
        if imports:
            context += "\n".join(imports) + "\n\n"
        return context

    def _create_chunk_id(self, file_path: str, class_name: str, method_name: str = None) -> str:
        """Create a unique chunk ID."""
        parts = [file_path.replace("/", ":")]
        if class_name:
            parts.append(class_name)
        if method_name:
            parts.append(method_name)
        return ":".join(parts)
