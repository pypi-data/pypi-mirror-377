from typing import List, Optional

from pydantic import BaseModel, Field
from tree_sitter import Node

from ..data_models.method_info import MethodInfo


class ClassInfo(BaseModel):
    class Config:
        exclude_none = True
        exclude_unset = True
        arbitrary_types_allowed = True  # Allow tree-sitter Node
        
    name: str
    modifiers: List[str]
    methods: List[MethodInfo]
    fields: List[str]
    constructors: List[MethodInfo]
    start_line: int
    end_line: int
    node: Node = Field(exclude=True)  # Required field, excluded from serialization

    # Framework detection fields for openapi and doc generation
    annotations: List[str] = Field(default_factory=list)  # @RestController, @Service, etc.
    framework_type: Optional[str] = None  # spring-boot, jax-rs