#Java CST node type definitions
class JavaNodeTypes:
    """Constants for Java CST node types from tree-sitter-java grammar."""

    # Type-related nodes
    RETURN_TYPES = [
        "type_identifier",
        "generic_type",
        "array_type",
        "void_type",
        "scoped_type_identifier",
        "integral_type",  # int, long, short, byte
        "floating_point_type",  # double, float
        "boolean_type",
        "primitive_type"
    ]

    PARAMETER_TYPES = [
        "type_identifier",
        "generic_type",
        "array_type",
        "scoped_type_identifier",
        "integral_type",
        "floating_point_type",
        "boolean_type",
        "primitive_type"
    ]

    # Modifier nodes
    ACCESS_MODIFIERS = ["public", "private", "protected"]
    OTHER_MODIFIERS = ["static", "final", "abstract", "synchronized", "native", "transient", "volatile"]
    ALL_MODIFIERS = ACCESS_MODIFIERS + OTHER_MODIFIERS

    # Declaration node constants
    CLASS_DECLARATION = "class_declaration"
    METHOD_DECLARATION = "method_declaration"
    CONSTRUCTOR_DECLARATION = "constructor_declaration"
    FIELD_DECLARATION = "field_declaration"
    INTERFACE_DECLARATION = "interface_declaration"
    ENUM_DECLARATION = "enum_declaration"
    PACKAGE_DECLARATION = "package_declaration"
    IMPORT_DECLARATION = "import_declaration"

    # Structural node constants
    IDENTIFIER = "identifier"
    CLASS_BODY = "class_body"
    MODIFIERS = "modifiers"
    FORMAL_PARAMETERS = "formal_parameters"
    FORMAL_PARAMETER = "formal_parameter"
    VARIABLE_DECLARATOR = "variable_declarator"

    ANNOTATION = "annotation"

    # Convenience accessors for common patterns
    @classmethod
    def is_type_node(cls, node_type: str) -> bool:
        return node_type in cls.RETURN_TYPES or node_type in cls.PARAMETER_TYPES