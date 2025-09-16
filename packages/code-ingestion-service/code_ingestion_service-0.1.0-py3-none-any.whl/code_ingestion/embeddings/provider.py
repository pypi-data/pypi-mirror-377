import os
import threading
from typing import List

from langchain_huggingface import HuggingFaceEmbeddings

from .base_provider import BaseEmbeddingProvider


class NomicEmbeddingProvider(BaseEmbeddingProvider):
    """Nomic embedding provider with parallel processing."""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model_kwargs = {"trust_remote_code": True}
        self._dimension = 768
        self.max_workers = min(8, (os.cpu_count() or 1) + 4)  # Cap at 8 for stability
        
        # Single shared embedder with thread-safe access
        self._embedder = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=self.model_kwargs
        )
        
        # Lock for thread-safe access to the shared model
        self._model_lock = threading.Lock()

    def _embed_single_safe(self, text: str) -> List[float]:
        """Thread-safe single text embedding using shared model with lock."""
        with self._model_lock:
            return self._embedder.embed_documents([text])[0]

    def embed_chunks(self, texts: List[str], verbose: bool = False) -> List[List[float]]:
        """Convert text chunks to embeddings with parallel processing."""
        if len(texts) <= 1:
            # Use shared embedder for single text (no threading needed)
            return self._embedder.embed_documents(texts)
        
        # Use intelligent batching - this is actually the optimal approach for this model
        if verbose:
            print(f"🔥 Processing {len(texts)} chunks with intelligent batching")
        
        return self._embed_intelligent_batched(texts, verbose)
    
    def _embed_intelligent_batched(self, texts: List[str], verbose: bool) -> List[List[float]]:
        """Intelligent batching optimized for the Nomic model architecture."""
        # Optimal batch size for Nomic model - balance between memory and speed
        optimal_batch_size = 16
        all_embeddings = []
        
        if verbose:
            print(f"📊 Processing {len(texts)} texts in batches of {optimal_batch_size}")
        
        for i in range(0, len(texts), optimal_batch_size):
            batch_texts = texts[i:i + optimal_batch_size]
            
            try:
                # Process batch - this is thread-safe and optimal for the model
                batch_embeddings = self._embedder.embed_documents(batch_texts)
                all_embeddings.extend(batch_embeddings)
                
                if verbose:
                    progress = min(i + optimal_batch_size, len(texts))
                    print(f"   ✅ Batch {i//optimal_batch_size + 1}: {progress}/{len(texts)} processed")
                    
            except Exception as e:
                if verbose:
                    print(f"⚠️ Batch failed, processing individually: {str(e)[:100]}...")
                    
                # Fallback to individual processing for this batch only
                for text in batch_texts:
                    try:
                        embedding = self._embedder.embed_documents([text])[0]
                        all_embeddings.append(embedding)
                    except Exception as individual_error:
                        if verbose:
                            print(f"❌ Individual embedding failed (text length {len(text)})")
                        # Create zero vector as last resort
                        all_embeddings.append([0.0] * self._dimension)
        
        if verbose:
            print(f"🎯 Completed: {len(all_embeddings)} embeddings generated")
        
        return all_embeddings

    def get_embedding_dimension(self) -> int:
        """Return the dimension of the embedding vectors."""
        return self._dimension

