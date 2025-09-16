# Code Ingestion Service - Complete Documentation

A production-ready Python service for intelligently chunking source code and ingesting it into RAG (Retrieval-Augmented Generation) pipelines with pluggable embedding providers and vector stores.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Pluggable Components](#pluggable-components)
- [CLI Usage](#cli-usage)
- [GitHub Workflows](#github-workflows)
- [Performance Features](#performance-features)
- [Adding New Providers](#adding-new-providers)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

## Overview

### What It Does
- **Intelligently chunks** source code into meaningful segments
- **Generates embeddings** using configurable embedding models
- **Stores in vector databases** for RAG pipeline integration
- **Supports multiple providers** for embeddings and storage
- **Optimized for performance** with intelligent batching

### Key Features
- 🔌 **Pluggable Architecture** - Swap embedding providers and vector stores
- ⚡ **High Performance** - Optimized batching for ultra-fast embedding generation
- 🎯 **Smart Chunking** - Context-aware code splitting (class/method level)
- 📊 **Production Ready** - Error handling, logging, and monitoring
- 🛠️ **Simple CLI** - Easy to use command-line interface
- 🔧 **Programmatic API** - Full programmatic control

## Architecture

### Core Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Code Files   │───▶│  Chunking       │───▶│  Embeddings     │
│   (.java, .py) │    │  (Smart Split)  │    │  (Batched)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Vector Storage  │◀───│  Orchestration  │◀───│  Generated      │
│ (Pinecone, etc) │    │  (Coordinates)  │    │  Embeddings     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Directory Structure

```
src/code_ingestion/
├── analyzers/          # Code analysis (CST parsing)
├── chunkers/           # Code chunking strategies  
├── embeddings/         # Embedding providers (pluggable)
├── vector_stores/      # Vector storage (pluggable)
├── orchestration/      # Pipeline coordination
├── data_models/        # Data structures
├── enums/             # Constants and enums
└── parsers/           # Language parsers
```

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/your-username/code-ingestion-service.git
cd code-ingestion-service

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env file
PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX_NAME=your-index-name
EMBEDDING_MODEL=nomic-ai/nomic-embed-text-v1.5
```

### Basic Usage

```bash
# Default: Nomic embeddings + Pinecone storage
python cli.py /path/to/your/repo

# With custom providers
python cli.py /path/to/repo --embedding-provider openai --vector-store weaviate

# With detailed logging
python cli.py /path/to/repo --verbose

# Remote repository
python cli.py https://github.com/user/repo --include "**/*.java"
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PINECONE_API_KEY` | Pinecone API key | - | Yes (for Pinecone) |
| `PINECONE_INDEX_NAME` | Pinecone index name | - | Yes (for Pinecone) |
| `PINECONE_BATCH_SIZE` | Batch size for uploads | 100 | No |
| `EMBEDDING_MODEL` | Default embedding model | nomic-ai/nomic-embed-text-v1.5 | No |

### File Filtering

Default patterns (customizable via CLI):

**Included:**
```
**/*.java, **/*.py, **/*.js, **/*.ts, **/*.go, **/*.rs, **/*.cpp
```

**Excluded:**  
```
**/test/**, **/tests/**, **/node_modules/**, **/build/**, **/dist/**
```

## Pluggable Components

### Available Embedding Providers

| Provider | Model | Dimensions | Performance |
|----------|-------|------------|-------------|
| **nomic** (default) | nomic-embed-text-v1.5 | 768 | Fast, local |
| **openai** | text-embedding-ada-002 | 1536 | High quality |
| **huggingface** | Custom models | Variable | Flexible |

### Available Vector Stores

| Store | Type | Features |
|-------|------|----------|
| **pinecone** (default) | Cloud | Managed, scalable |
| **weaviate** | Self-hosted | Open source |
| **qdrant** | Self-hosted | High performance |
| **chroma** | Local | Development friendly |

### Supported Languages

| Language | Parser | Features |
|----------|--------|----------|
| **Java** | Tree-sitter | Classes, methods, annotations, REST APIs |
| **Python** | Tree-sitter | Functions, classes (coming soon) |
| **JavaScript/TypeScript** | Tree-sitter | (coming soon) |

## CLI Usage

### Basic Commands

```bash
# Local repository
python cli.py /path/to/repo

# Remote repository  
python cli.py https://github.com/user/repo

# With file filtering
python cli.py /path/to/repo --include "**/*.java" --exclude "**/test/**"

# Limit files processed
python cli.py /path/to/repo --max-files 100
```

### Provider Selection

```bash
# Different embedding providers
python cli.py /path/to/repo --embedding-provider nomic     # Default
python cli.py /path/to/repo --embedding-provider openai
python cli.py /path/to/repo --embedding-provider huggingface

# Different vector stores  
python cli.py /path/to/repo --vector-store pinecone        # Default
python cli.py /path/to/repo --vector-store weaviate
python cli.py /path/to/repo --vector-store qdrant
```

### Debugging & Monitoring

```bash
# Verbose logging (shows progress, timing, metrics)
python cli.py /path/to/repo --verbose

# Quiet processing (default - no logging overhead)
python cli.py /path/to/repo
```

### CLI Options Reference

| Option | Type | Description | Example |
|--------|------|-------------|---------|
| `--embedding-provider` | string | Embedding provider to use | `--embedding-provider openai` |
| `--vector-store` | string | Vector store to use | `--vector-store weaviate` |
| `--verbose` | flag | Enable detailed logging | `--verbose` |
| `--include` | patterns | File patterns to include | `--include "**/*.py" "**/*.java"` |
| `--exclude` | patterns | File patterns to exclude | `--exclude "**/test/**"` |
| `--max-files` | integer | Maximum files to process | `--max-files 500` |
| `--cleanup/--no-cleanup` | flag | Clean up temp files | `--no-cleanup` |

## Programmatic Usage

### Basic Example

```python
from src.code_ingestion.orchestration import create_ingestion_orchestrator

# Create orchestrator with default providers
orchestrator = create_ingestion_orchestrator(
    embedding_provider='nomic',
    vector_store='pinecone',
    verbose=True
)

# Prepare source files (file_path, content) tuples
source_files = [
    ('src/main/Example.java', java_code_content),
    ('src/utils/Helper.java', helper_code_content)
]

# Execute ingestion
result = orchestrator.execute(source_files)
print(f"Processed {result.chunks_processed} chunks")
```

### Advanced Usage

```python
from src.code_ingestion.chunkers.factory import create_java_chunker
from src.code_ingestion.embeddings.factory import create_nomic_embedding_provider  
from src.code_ingestion.vector_stores.factory import create_vector_store
from src.code_ingestion.orchestration import IngestionOrchestrator

# Create components individually for fine control
chunker = create_java_chunker(max_class_size=2000)
embedding_provider = create_nomic_embedding_provider()
vector_store = create_vector_store('pinecone')

# Custom orchestrator
orchestrator = IngestionOrchestrator(
    chunker=chunker,
    embedding_provider=embedding_provider,
    vector_store=vector_store,
    verbose=False
)

# Process files
result = orchestrator.execute(source_files)
```

### Working with Individual Components

```python
# Just chunking
chunker = create_java_chunker()
chunks = chunker.chunk_code(source_code, file_path="Example.java")

# Just embeddings (with optimized batching)
embedding_provider = create_nomic_embedding_provider()
embeddings = embedding_provider.embed_chunks(
    texts=[chunk.content for chunk in chunks],
    verbose=True  # Show progress
)

# Just storage
vector_store = create_vector_store('pinecone')
stored_ids = vector_store.store_chunks(chunks, embeddings)
```

## Performance Features

### Intelligent Batching

- **Automatic**: Enabled by default for embedding generation
- **Smart**: Uses optimal batch sizes based on model architecture
- **Efficient**: Processes multiple texts in single model calls
- **Performance**: Optimized batching for maximum throughput

### Intelligent Filtering

Built-in filtering skips non-essential files:
- Test files (`/test/`, `/tests/`)
- Build artifacts (`/build/`, `/dist/`, `/target/`)
- Dependencies (`/node_modules/`, `/vendor/`)
- Generated files

### Optimized Chunking

- **Context-aware**: Maintains package/import context
- **Size-adaptive**: Complete classes vs method-level chunks
- **Single-pass**: Optimized CST traversal
- **Memory efficient**: Streaming processing

### Logging Control

```python
# Production: Quiet by default (no performance overhead)
orchestrator = create_ingestion_orchestrator(verbose=False)

# Development: Detailed logging
orchestrator = create_ingestion_orchestrator(verbose=True)
# Shows: progress bars, timing metrics, batch counts, processing info
```

## Adding New Providers

### Adding an Embedding Provider

1. **Create provider class**:

```python
# src/code_ingestion/embeddings/openai_provider.py
from .base_provider import BaseEmbeddingProvider

class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, api_key: str, model: str = "text-embedding-ada-002"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self._dimension = 1536
    
    def embed_chunks(self, texts: List[str], verbose: bool = False) -> List[List[float]]:
        # Implementation with intelligent batching
        pass
    
    def get_embedding_dimension(self) -> int:
        return self._dimension
```

2. **Update factory**:

```python
# src/code_ingestion/embeddings/factory.py
def create_embedding_provider(provider_type: str = 'nomic') -> BaseEmbeddingProvider:
    if provider_type == 'nomic':
        return NomicEmbeddingProvider(model_name="nomic-ai/nomic-embed-text-v1.5")
    elif provider_type == 'openai':
        return OpenAIEmbeddingProvider(api_key=os.getenv("OPENAI_API_KEY"))
    else:
        raise ValueError(f"Unsupported embedding provider: {provider_type}")
```

3. **Usage**:

```bash
python cli.py /path/to/repo --embedding-provider openai
```

### Adding a Vector Store

1. **Create store class**:

```python
# src/code_ingestion/vector_stores/weaviate_store.py
from .base_store import BaseVectorStore

class WeaviateVectorStore(BaseVectorStore):
    def __init__(self):
        # Initialize Weaviate client
        pass
    
    def store_chunks(self, chunks: List[CodeChunk], embeddings: List[List[float]]) -> List[str]:
        # Weaviate-specific storage implementation
        pass
```

2. **Update factory**:

```python
# src/code_ingestion/vector_stores/factory.py  
def create_vector_store(store_type: str = 'pinecone') -> BaseVectorStore:
    if store_type == 'pinecone':
        return PineconeVectorStore()
    elif store_type == 'weaviate':
        return WeaviateVectorStore()
    else:
        raise ValueError(f"Unsupported vector store: {store_type}")
```

### Adding Language Support

1. **Create analyzer**:

```python
# src/code_ingestion/analyzers/python_analyzer.py
from .cst_analyzer import CSTAnalyzer

class PythonCSTAnalyzer(CSTAnalyzer):
    def extract_classes(self, tree: Tree, source_code: str) -> List[ClassInfo]:
        # Python-specific CST analysis
        pass
```

2. **Update chunker factory**:

```python
# src/code_ingestion/chunkers/factory.py
def create_chunker(language: str = 'java'):
    if language == 'java':
        return create_java_chunker()
    elif language == 'python':
        return create_python_chunker()
```

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/main.py

# Run with verbose output
python tests/main.py --verbose
```

### Code Quality

```bash
# Linting
ruff check src/

# Type checking  
mypy src/

# Format code
black src/
```

### Project Structure

```
├── cli.py                 # Command-line interface
├── src/code_ingestion/    # Main package
│   ├── analyzers/         # Code analysis (CST)
│   ├── chunkers/          # Chunking strategies
│   ├── embeddings/        # Embedding providers
│   ├── vector_stores/     # Vector storage
│   ├── orchestration/     # Pipeline coordination
│   └── data_models/       # Data structures
├── tests/                 # Test suite
├── .env.example          # Environment template
└── requirements.txt      # Dependencies
```

## Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=.
python cli.py /path/to/repo
```

**2. Pinecone Connection Issues**
```bash
# Check environment variables
echo $PINECONE_API_KEY
echo $PINECONE_INDEX_NAME

# Verify API key validity
curl -H "Api-Key: $PINECONE_API_KEY" https://api.pinecone.io/indexes
```

**3. Memory Issues with Large Repos**
```bash
# Limit files processed
python cli.py /path/to/repo --max-files 1000

# Use more specific patterns
python cli.py /path/to/repo --include "src/**/*.java" --exclude "**/test/**"
```

**4. Performance Issues**
```bash
# Check if batching is working optimally
python cli.py /path/to/repo --verbose
# Should show: "Processing X chunks with intelligent batching"

# Reduce batch size for memory-constrained systems
export PINECONE_BATCH_SIZE=50
```

### Debug Mode

Enable verbose logging to see detailed processing information:

```bash
python cli.py /path/to/repo --verbose
```

This shows:
- File discovery progress
- Chunking statistics  
- Embedding generation progress with batch processing
- Storage batch operations
- Performance metrics

### Getting Help

1. **Check logs**: Use `--verbose` flag for detailed output
2. **Validate config**: Ensure all environment variables are set
3. **Test components**: Use programmatic API to isolate issues
4. **File issues**: Report bugs on GitHub with verbose logs

---

## 🎯 Summary

This service provides a **simple, pluggable, and high-performance** solution for ingesting code into RAG pipelines:

- **Simple**: `python cli.py /path/to/repo` just works
- **Pluggable**: Swap providers with `--embedding-provider` and `--vector-store`  
- **Fast**: Ultra-fast processing with intelligent batching
- **Production-ready**: Error handling, logging, and monitoring built-in

**Default stack**: Nomic embeddings + Pinecone storage + Java support
**Extensible**: Easy to add new providers, stores, and languages