from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ChunkMetadata(BaseModel):
    class Config:
        exclude_none = True
        exclude_unset = True
    # MANDATORY FIELDS FIRST (no defaults)
    language: str  # Now mandatory!
    chunk_type: str  # Also mandatory
    repo_url:str

    # OPTIONAL FIELDS LCST (with defaults)
    # File context
    file_path: Optional[str] = None
    file_name: Optional[str] = None

    # Code structure
    class_name: Optional[str] = None
    method_name: Optional[str] = None
    signature: Optional[str] = None
    return_type: Optional[str] = None
    fields: List[str] = Field(default_factory=list)
    methods: List[str] = Field(default_factory=list)

    # Chunk info
    chunk_size: int = 0
    start_line: int = 0
    end_line: int = 0

    # Processing info
    processed_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    #fields to support openapi and readme generations
    annotations: List[str] = Field(default_factory=list)
    framework_type: Optional[str] = None
    is_rest_controller: bool = False
    http_methods: List[str] = Field(default_factory=list)  # For class-level: all methods in class
    api_path: Optional[str] = None