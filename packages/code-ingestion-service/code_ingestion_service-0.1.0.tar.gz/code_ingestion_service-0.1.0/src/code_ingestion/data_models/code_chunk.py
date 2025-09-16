from pydantic import BaseModel

from .chunk_metadata import ChunkMetadata


class CodeChunk(BaseModel):
    class Config:
        exclude_none = True
        exclude_unset = True
        
    id: str
    content: str
    metadata: ChunkMetadata