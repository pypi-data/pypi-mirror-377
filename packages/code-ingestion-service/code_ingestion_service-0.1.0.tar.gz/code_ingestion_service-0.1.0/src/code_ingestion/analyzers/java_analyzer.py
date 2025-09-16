from typing import List, Tuple, Optional, Dict

from tree_sitter import Tree, Node

from ..analyzers.cst_analyzer import CSTAnalyzer
from ..analyzers.java_cst_types import JavaNodeTypes
from ..data_models.class_info import ClassInfo
from ..data_models.method_info import MethodInfo


class JavaCSTAnalyzer(CSTAnalyzer):
    """Java-specific CST analyzer."""

    def extract_classes(self, tree: Tree, source_code: str) -> List[ClassInfo]:
        """Extract Java class information from CST."""
        classes = []

        for node in tree.root_node.children:
            if node.type == JavaNodeTypes.CLASS_DECLARATION:
                class_info = self._analyze_class(node, source_code)
                if class_info:
                    classes.append(class_info)

        return classes

    def _analyze_class(self, class_node: Node, source_code: str) -> Optional[ClassInfo]:
        """Analyze a single class node."""
        class_name = None
        methods = []
        fields = []
        constructors = []
        annotations = []  # NEW

        # Extract class name and annotations (enhanced existing loop)
        for child in class_node.children:
            if child.type == JavaNodeTypes.IDENTIFIER:
                class_name = self.parser.extract_text(child, source_code)
            elif child.type == JavaNodeTypes.MODIFIERS:  # NEW
                annotations = self._extract_annotations_from_modifiers(child, source_code)

        if not class_name:
            return None

        # Extract class body (your existing logic - unchanged)
        for child in class_node.children:
            if child.type == JavaNodeTypes.CLASS_BODY:
                for member in child.children:
                    if member.type == JavaNodeTypes.METHOD_DECLARATION:
                        method_info = self._extract_method_info(member, source_code)
                        if method_info:
                            methods.append(method_info)
                    elif member.type == JavaNodeTypes.CONSTRUCTOR_DECLARATION:
                        constructor_info = self._extract_constructor_info(member, source_code, class_name)
                        if constructor_info:
                            constructors.append(constructor_info)
                    elif member.type == JavaNodeTypes.FIELD_DECLARATION:
                        field_names = self._extract_field_names(member, source_code)
                        fields.extend(field_names)

        start_line, end_line = self.parser.get_line_numbers(class_node)
        framework_type = self._detect_framework_type(annotations)  # NEW

        # NEW: Class-level path processing
        class_base_path = self._extract_class_base_path(annotations)
        if class_base_path:
            methods = self._enrich_methods_with_base_path(methods, class_base_path)

        return ClassInfo(
            name=class_name,
            modifiers=[],
            methods=methods,
            fields=fields,
            constructors=constructors,
            start_line=start_line,
            end_line=end_line,
            node=class_node,
            annotations=annotations,  # NEW
            framework_type=framework_type  # NEW
        )

    def _extract_modifiers(self, modifiers_node: Node, source_code: str) -> List[str]:
        """Extract modifiers from a modifiers node."""
        modifiers = []
        for child in modifiers_node.children:
            if child.type in JavaNodeTypes.ALL_MODIFIERS:
                modifiers.append(child.type)
        return modifiers

    def _extract_method_info(self, method_node: Node, source_code: str) -> Optional[MethodInfo]:
        """Extract method information."""
        name = None
        return_type = None
        annotations = []  # NEW

        # Extract components (enhanced existing loop)
        for child in method_node.children:
            if child.type == JavaNodeTypes.IDENTIFIER:
                name = self.parser.extract_text(child, source_code)
            elif child.type in JavaNodeTypes.RETURN_TYPES:
                return_type = self.parser.extract_text(child, source_code)
            elif child.type == JavaNodeTypes.MODIFIERS:  # NEW
                annotations = self._extract_annotations_from_modifiers(child, source_code)

        if not name:
            return None

        signature = self.parser.extract_text(method_node, source_code).split("{")[0].strip()
        start_line, end_line = self.parser.get_line_numbers(method_node)
        http_method, api_path = self._analyze_rest_annotations(annotations)  # NEW

        return MethodInfo(
            name=name,
            signature=signature,
            return_type=return_type,
            node=method_node,
            start_line=start_line,
            end_line=end_line,
            annotations=annotations,  # NEW
            http_method=http_method,  # NEW
            api_path=api_path  # NEW
        )

    def _extract_constructor_info(self, constructor_node: Node, source_code: str, class_name: str) -> Optional[
        MethodInfo]:
        """Extract constructor information."""
        signature = self.parser.extract_text(constructor_node, source_code).split("{")[0].strip()
        start_line, end_line = self.parser.get_line_numbers(constructor_node)

        return MethodInfo(
            name=class_name,
            signature=signature,
            return_type=None,
            node=constructor_node,
            start_line=start_line,
            end_line=end_line
        )

    def _extract_parameters(self, params_node: Node, source_code: str) -> List[Dict[str, str]]:
        """Extract parameter information."""
        parameters = []
        for child in params_node.children:
            if child.type == JavaNodeTypes.FORMAL_PARAMETER:
                param_info = {"type": None, "name": None}
                for param_child in child.children:
                    if param_child.type in JavaNodeTypes.PARAMETER_TYPES:  # ← Use your constant!
                        param_info["type"] = self.parser.extract_text(param_child, source_code)
                    elif param_child.type == JavaNodeTypes.IDENTIFIER:
                        param_info["name"] = self.parser.extract_text(param_child, source_code)
                parameters.append(param_info)
        return parameters

    def _extract_field_names(self, field_node: Node, source_code: str) -> List[str]:
        """Extract field names from a field declaration."""
        field_names = []
        for child in field_node.children:
            if child.type == JavaNodeTypes.VARIABLE_DECLARATOR:
                for var_child in child.children:
                    if var_child.type == JavaNodeTypes.IDENTIFIER:
                        field_names.append(self.parser.extract_text(var_child, source_code))
        return field_names

    def extract_package_and_imports(self, tree: Tree, source_code: str) -> Tuple[str, List[str]]:
        """Extract package declaration and imports."""
        package = None
        imports = []

        for node in tree.root_node.children:
            if node.type == JavaNodeTypes.PACKAGE_DECLARATION:
                package = self.parser.extract_text(node, source_code)
            elif node.type == JavaNodeTypes.IMPORT_DECLARATION:
                imports.append(self.parser.extract_text(node, source_code))

        return package, imports

    def extract_all_info(self, tree: Tree, source_code: str) -> Tuple[str, List[str], List[ClassInfo]]:
        """
        Single-pass CST extraction for optimal performance.
        Extracts package, imports, and classes in one traversal.
        """
        package = None
        imports = []
        classes = []

        # Single traversal of root level nodes
        for node in tree.root_node.children:
            if node.type == JavaNodeTypes.PACKAGE_DECLARATION:
                package = self.parser.extract_text(node, source_code)
            elif node.type == JavaNodeTypes.IMPORT_DECLARATION:
                imports.append(self.parser.extract_text(node, source_code))
            elif node.type == JavaNodeTypes.CLASS_DECLARATION:
                class_info = self._analyze_class(node, source_code)
                if class_info:
                    classes.append(class_info)

        return package, imports, classes

    def _extract_annotations_from_modifiers(self, modifiers_node: Node, source_code: str) -> List[str]:
        """Extract annotations from a modifiers node."""
        annotations = []
        for child in modifiers_node.children:
            if child.type == JavaNodeTypes.ANNOTATION:
                annotation_text = self.parser.extract_text(child, source_code)
                annotations.append(annotation_text.strip())
        return annotations

    def _detect_framework_type(self, annotations: List[str]) -> Optional[str]:
        """Detect framework type from class annotations"""
        for annotation in annotations:
            if "@RestController" in annotation or "@Controller" in annotation:
                return "spring-boot"
            elif "@Path" in annotation:
                return "jax-rs"
        return None

    def _analyze_rest_annotations(self, annotations: List[str]) -> Tuple[Optional[str], Optional[str]]:
        """Analyze REST annotations for HTTP method and path"""
        http_method = None
        api_path = None

        for annotation in annotations:
            # Check for direct method mappings
            for annotation_type, method in self.METHOD_MAPPINGS.items():
                if annotation_type in annotation:
                    http_method = method
                    api_path = self._extract_path_from_mapping(annotation)
                    break

            # Special handling for @RequestMapping
            if "@RequestMapping" in annotation:
                if "GET" in annotation or "RequestMethod.GET" in annotation:
                    http_method = "GET"
                elif "POST" in annotation or "RequestMethod.POST" in annotation:
                    http_method = "POST"
                api_path = self._extract_path_from_mapping(annotation)

            # Extract path from @Path (JAX-RS)
            elif "@Path" in annotation:
                api_path = self._extract_path_from_mapping(annotation)

        return http_method, api_path

    def _extract_class_base_path(self, class_annotations: List[str]) -> Optional[str]:
        """Extract base path from class-level @RequestMapping"""
        for annotation in class_annotations:
            if "@RequestMapping" in annotation:
                return self._extract_path_from_mapping(annotation)
        return None

    def _enrich_methods_with_base_path(self, methods: List[MethodInfo], class_base_path: str) -> List[MethodInfo]:
        """Combine class base path with method paths"""
        for method in methods:
            if method.api_path:
                method.api_path = self._combine_paths(class_base_path, method.api_path)
            elif method.http_method:
                method.api_path = class_base_path
        return methods

    def _combine_paths(self, base_path: str, method_path: str) -> str:
        """Combine base and method paths"""
        base = base_path.rstrip('/')
        method = method_path.lstrip('/') if method_path else ""
        return f"{base}/{method}" if method else base

    def _extract_path_from_mapping(self, annotation: str) -> Optional[str]:
        """Extract path from mapping annotation"""
        import re
        path_patterns = [
            r'["\']([^"\']*)["\']',  # Simple quoted path
            r'path\s*=\s*["\']([^"\']*)["\']',  # path = "/path"
            r'value\s*=\s*["\']([^"\']*)["\']'  # value = "/path"
        ]

        for pattern in path_patterns:
            match = re.search(pattern, annotation)
            if match:
                return match.group(1)
        return None