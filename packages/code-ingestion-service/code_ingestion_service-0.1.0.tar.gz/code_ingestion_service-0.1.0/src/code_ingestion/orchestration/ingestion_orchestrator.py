from dataclasses import dataclass
from typing import List

from ..chunkers.factory import create_java_chunker
from ..embeddings.factory import create_nomic_embedding_provider
from ..vector_stores.factory import create_vector_store


@dataclass
class IngestionResult:
    """Simple result object."""
    chunks_processed: int
    success: bool


class IngestionOrchestrator:
    """Simple orchestrator - coordinates chunking, embedding, and storage."""
    
    def __init__(self, chunker, embedding_provider, vector_store, verbose: bool = False):
        self.chunker = chunker
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.verbose = verbose
    
    def execute(self, source_code_files: List[tuple]) -> IngestionResult:
        """Execute the ingestion pipeline."""
        if self.verbose:
            print("🚀 Starting code ingestion pipeline...")
        
        # Step 1: Chunk all files
        all_chunks = []
        for file_path, content in source_code_files:
            chunks = self.chunker.chunk_code(content, file_path, "")
            all_chunks.extend(chunks)
        
        if self.verbose:
            print(f"📝 Generated {len(all_chunks)} code chunks")
        
        if not all_chunks:
            return IngestionResult(chunks_processed=0, success=True)
        
        # Step 2: Generate embeddings (parallel by default)
        embeddings = self.embedding_provider.embed_chunks(
            [chunk.content for chunk in all_chunks],
            verbose=self.verbose
        )
        
        # Step 3: Store in vector database
        stored_ids = self.vector_store.store_chunks(all_chunks, embeddings)
        
        if self.verbose:
            print(f"✅ Stored {len(stored_ids)} chunks successfully!")
        
        return IngestionResult(chunks_processed=len(all_chunks), success=True)


def create_ingestion_orchestrator(
    embedding_provider: str = 'nomic',
    vector_store: str = 'pinecone', 
    verbose: bool = False
) -> IngestionOrchestrator:
    """Factory for creating orchestrator - reuses existing factories."""
    return IngestionOrchestrator(
        chunker=create_java_chunker(),
        embedding_provider=create_nomic_embedding_provider(),
        vector_store=create_vector_store(vector_store),
        verbose=verbose
    )