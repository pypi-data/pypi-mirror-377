import os
from typing import List

from pinecone import Pinecone, ServerlessSpec

from .base_store import BaseVectorStore
from ..data_models.code_chunk import CodeChunk


class PineconeVectorStore(BaseVectorStore):
    """Pure Pinecone storage - no embedding creation."""
    
    def __init__(self):
        """Initialize Pinecone client and ensure index exists."""
        api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = os.getenv("PINECONE_INDEX_NAME")
        
        if not api_key or not self.index_name:
            raise ValueError("PINECONE_API_KEY and PINECONE_INDEX_NAME required")
        
        self.pc = Pinecone(api_key=api_key)
        self._ensure_index_exists()
    
    def store_chunks(self, chunks: List[CodeChunk], embeddings: List[List[float]]) -> List[str]:
        """Store chunks with pre-computed embeddings."""
        if len(chunks) != len(embeddings):
            raise ValueError("Chunks and embeddings must have same length")
        
        # Prepare vectors for Pinecone
        vectors = []
        for chunk, embedding in zip(chunks, embeddings):
            vectors.append({
                'id': chunk.id,
                'values': embedding,
                'metadata': chunk.metadata.model_dump(exclude_none=True, exclude_unset=True)
            })
        
        # Store in batches
        index = self.pc.Index(self.index_name)
        batch_size = int(os.getenv("PINECONE_BATCH_SIZE", "100"))
        
        stored_ids = []
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            index.upsert(vectors=batch)
            stored_ids.extend([v['id'] for v in batch])
        
        return stored_ids
    
    def _ensure_index_exists(self):
        """Create index if it doesn't exist - reuse existing logic."""
        dimension = 768  # nomic-embed-text-v1.5 dimension
        
        if self.index_name in self.pc.list_indexes().names():
            index_stats = self.pc.describe_index(name=self.index_name)
            if index_stats.dimension != dimension:
                print(f"Recreating index '{self.index_name}' with correct dimension")
                self.pc.delete_index(name=self.index_name)
                self._create_index(dimension)
        else:
            self._create_index(dimension)
    
    def _create_index(self, dimension: int):
        """Create new Pinecone index."""
        self.pc.create_index(
            name=self.index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )