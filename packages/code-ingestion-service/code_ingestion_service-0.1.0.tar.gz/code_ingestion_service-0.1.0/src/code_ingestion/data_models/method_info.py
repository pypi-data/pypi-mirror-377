from typing import Optional, List

from pydantic import BaseModel, Field
from tree_sitter import Node


class MethodInfo(BaseModel):
    class Config:
        exclude_none = True
        exclude_unset = True
        arbitrary_types_allowed = True  # Allow tree-sitter Node
        
    name: str
    signature: str
    return_type: Optional[str]
    node: Node = Field(exclude=True)  # Required field, excluded from serialization
    start_line: int
    end_line: int

    # Fields to support openapi and doc generation
    annotations: List[str] = Field(default_factory=list)  # @GetMapping, @RequestMapping, etc.
    http_method: Optional[str] = None  # GET, POST, PUT, DELETE
    api_path: Optional[str] = None  # /api/users/{id}