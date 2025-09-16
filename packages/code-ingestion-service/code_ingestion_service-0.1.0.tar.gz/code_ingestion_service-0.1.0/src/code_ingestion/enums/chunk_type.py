from enum import Enum

class ChunkType(Enum):

    COMPLETE_CLASS = "complete_class"
    METHOD = "method"
    CONSTRUCTOR = "constructor"
    FIELDS = "fields"
    CLASS_HEADER = "class_header"
    INTERFACE = "interface"
    ENUM = "enum"