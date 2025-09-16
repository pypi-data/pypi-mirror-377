"""
Code Ingestion Service

A production-ready Python service for intelligently chunking source code and 
ingesting it into RAG (Retrieval-Augmented Generation) pipelines.

Features:
- Smart Code Chunking with CST analysis
- Pluggable Architecture for embedding providers and vector stores
- High Performance with intelligent batching
- Production-Ready CLI for both local and remote repositories

Author: Sandeep G
License: Apache License 2.0
"""

__version__ = "0.1.0"
__author__ = "Sandeep G"
__email__ = "sandeepg2890@gmail.com"
__license__ = "Apache-2.0"

# Main orchestrator for programmatic usage
from .orchestration import create_ingestion_orchestrator, IngestionOrchestrator

# Core data models
from .data_models import CodeChunk, ChunkMetadata, ClassInfo, MethodInfo

# Factory functions for easy setup
from .embeddings.factory import create_nomic_embedding_provider
from .vector_stores.factory import create_vector_store
from .chunkers.factory import create_java_chunker

__all__ = [
    # Version info
    "__version__", "__author__", "__email__", "__license__",
    
    # Main orchestrator
    "create_ingestion_orchestrator", "IngestionOrchestrator",
    
    # Data models
    "CodeChunk", "ChunkMetadata", "ClassInfo", "MethodInfo",
    
    # Factory functions
    "create_nomic_embedding_provider", "create_vector_store", "create_java_chunker",
]