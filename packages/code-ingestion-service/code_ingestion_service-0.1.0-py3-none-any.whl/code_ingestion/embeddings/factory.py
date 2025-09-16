import os

from .provider import NomicEmbeddingProvider


def create_nomic_embedding_provider() -> NomicEmbeddingProvider:
    """Factory function using environment variables."""
    model_name = os.getenv("EMBEDDING_MODEL", "nomic-ai/nomic-embed-text-v1.5")
    return NomicEmbeddingProvider(model_name=model_name)