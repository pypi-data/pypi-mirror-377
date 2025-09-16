from .base_store import BaseVectorStore
from .pinecone_store import PineconeVectorStore


def create_vector_store(store_type: str = 'pinecone') -> BaseVectorStore:
    """Factory for vector stores - keep it simple."""
    if store_type == 'pinecone':
        return PineconeVectorStore()
    else:
        raise ValueError(f"Unsupported vector store: {store_type}")