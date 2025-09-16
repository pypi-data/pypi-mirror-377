# Code Ingestion Service

A production-ready Python service for intelligently chunking source code and ingesting it into RAG (Retrieval-Augmented Generation) pipelines. Features optimized performance, Pinecone vector database integration, and a powerful CLI for both public and private repositories.

**Author:** Sandeep G  
**Copyright:** © 2025 Sandeep G  
**License:** Apache License 2.0 - see [LICENSE](LICENSE) file for details

## 🚀 Features

### Core Capabilities
- **Smart Code Chunking**: Single-pass CST analysis.
- **Pluggable Architecture**: Swap embedding providers (Nomic, OpenAI) and vector stores (Pinecone, Weaviate)
- **High Performance**: Optimized batching for ultra-fast embedding generation
- **Production-Ready CLI**: Unified interface with provider selection and verbose logging

### Language & Platform Support  
- **Java**: Full CST parsing with REST API detection and method extraction
- **Git Integration**: Shallow clone support for public/private repositories
- **Multiple Providers**: Nomic (default), OpenAI, HuggingFace embedding support
- **Vector Stores**: Pinecone (default), with extensible architecture

### Performance & Reliability
- **Optimized Processing**: Single-pass CST traversal, method-level context caching
- **Smart Filtering**: Include/exclude patterns for selective ingestion
- **Error Handling**: Robust processing with cleanup and validation
- **Test Coverage**: Comprehensive test suite for all components

## 🛠️ Core Components

### CodeChunker
The main orchestrator for code chunking operations, responsible for:
- Parsing source code
- Analyzing Concrete Syntax Trees (CST)
- Applying chunking strategies
- Generating structured code chunks with metadata

### Key Features
- **Package & Import Handling**: Preserves context by maintaining package and import statements
- **Class-Level Chunking**: Creates complete class chunks when appropriate
- **Method-Level Chunking**: Breaks down classes into method-level chunks when needed
- **Intelligent ID Generation**: Creates unique identifiers for each code chunk
- **Metadata Management**: Tracks comprehensive metadata for each chunk

## 🏗️ Architecture

The service follows a pluggable architecture with these main components:

1. **Orchestration**: Coordinates the complete ingestion pipeline
2. **Chunkers**: Handle intelligent code splitting with CST analysis
3. **Embedding Providers**: Generate embeddings (Nomic, OpenAI, HuggingFace)
4. **Vector Stores**: Store embeddings (Pinecone, Weaviate, Qdrant)
5. **Data Models**: Define structured representations for chunks and metadata

## 💻 Usage

### CLI Usage (Recommended)

The CLI provides a simple interface for ingesting repositories into your RAG pipeline:

#### Basic Usage
```bash
# Ingest a local repository
code-ingestion /path/to/your/repo

# Ingest a public GitHub repository
code-ingestion https://github.com/spring-projects/spring-boot

# Ingest with file filtering
code-ingestion https://github.com/kdn251/interviews \
  --include "**/*.java" \
  --exclude "**/test/**" \
  --max-files 50
```

#### Advanced Filtering
```bash
# Include specific folders and file types
code-ingestion https://github.com/kdn251/interviews \
  --include "company/**/*.java" \
  --include "leetcode/**/*.java" \
  --include "cracking-the-coding-interview/**/*.java" \
  --max-files 30

# Exclude unwanted directories
code-ingestion https://github.com/spring-projects/spring-boot \
  --include "**/*.java" \
  --exclude "**/test/**" \
  --exclude "**/build/**" \
  --exclude "**/target/**"
```

#### Provider Selection
```bash
# Use different embedding providers
code-ingestion /path/to/repo --embedding-provider nomic     # Default
code-ingestion /path/to/repo --embedding-provider openai
code-ingestion /path/to/repo --embedding-provider huggingface

# Use different vector stores  
code-ingestion /path/to/repo --vector-store pinecone        # Default
code-ingestion /path/to/repo --vector-store weaviate

# Enable detailed logging and progress
code-ingestion /path/to/repo --verbose
```

#### CLI Options
- `--embedding-provider`: Choose embedding provider (nomic, openai, huggingface)
- `--vector-store`: Choose vector store (pinecone, weaviate, qdrant)
- `--verbose`: Enable detailed logging and progress reports
- `--include`: File patterns to include (supports glob patterns like `**/*.java`)
- `--exclude`: File patterns to exclude (default excludes test, build, node_modules, etc.)
- `--max-files`: Limit number of files processed (useful for large repos)
- `--cleanup/--no-cleanup`: Control temporary file cleanup (default: cleanup enabled)

### GitHub Actions Integration (Recommended)

Create automated ingestion workflows for your repositories:

```yaml
# .github/workflows/ingest-code.yml
name: Ingest Codebase to RAG
on:
  workflow_dispatch:  # Manual trigger
  push:
    branches: [ main ]  # Auto-trigger on main branch updates
  
jobs:
  ingest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Code Ingestion Service
        run: |
          pip install git+https://github.com/sandeepgovi/code-ingestion-service.git@main
      
      - name: Ingest Current Repository
        run: |
          code-ingestion ./ \
            --include "**/*.java" \
            --include "**/*.py" \
            --exclude "**/test/**" \
            --verbose
        env:
          PINECONE_API_KEY: ${{ secrets.PINECONE_API_KEY }}
          PINECONE_INDEX_NAME: ${{ secrets.PINECONE_INDEX_NAME }}

  # Optional: Ingest external repositories
  ingest-external:
    runs-on: ubuntu-latest
    steps:
      - name: Install Code Ingestion Service
        run: |
          pip install git+https://github.com/sandeepgovi/code-ingestion-service.git@main
          
      - name: Ingest Spring Boot (example)
        run: |
          code-ingestion https://github.com/spring-projects/spring-boot \
            --include "**/*.java" \
            --max-files 200 \
            --verbose
        env:
          PINECONE_API_KEY: ${{ secrets.PINECONE_API_KEY }}
          PINECONE_INDEX_NAME: ${{ secrets.PINECONE_INDEX_NAME }}
```

#### Multi-Repository Workflow

```yaml
# Ingest multiple repositories in one workflow
name: Build Knowledge Base
on:
  workflow_dispatch:
  schedule:
    - cron: '0 2 * * 0'  # Weekly on Sunday at 2 AM

jobs:
  ingest-repositories:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        repo: 
          - 'https://github.com/spring-projects/spring-boot'
          - 'https://github.com/apache/kafka' 
          - 'your-org/internal-repo'
    steps:
      - name: Install Code Ingestion Service
        run: |
          pip install git+https://github.com/sandeepgovi/code-ingestion-service.git@main
          
      - name: Ingest Repository
        run: |
          code-ingestion ${{ matrix.repo }} \
            --include "**/*.java" \
            --exclude "**/test/**" \
            --max-files 500 \
            --verbose
        env:
          PINECONE_API_KEY: ${{ secrets.PINECONE_API_KEY }}
          PINECONE_INDEX_NAME: ${{ secrets.PINECONE_INDEX_NAME }}
```

### Local Development & Testing

You can test the service locally before setting up CI/CD:

```bash
# Test with a local repository
code-ingestion /path/to/your/local/repo --verbose

# Test with a public repository
code-ingestion https://github.com/spring-projects/spring-boot \
  --include "**/*.java" \
  --max-files 50 \
  --verbose

# Test different providers
code-ingestion /path/to/repo \
  --embedding-provider openai \
  --vector-store pinecone \
  --verbose
```

## ⚙️ Setup

### Prerequisites
- Python 3.13+
- Pinecone account and API key
- Git (for repository cloning)

### Installation

#### Option 1: Direct Installation (Recommended)
```bash
# Install directly from GitHub
pip install git+https://github.com/sandeepgovi/code-ingestion-service.git@main

# Test the installation
code-ingestion --help
```

#### Option 2: Development Installation
```bash
# Clone and install in development mode
git clone https://github.com/sandeepgovi/code-ingestion-service
cd code-ingestion-service
pip install -e .

# Test the installation  
code-ingestion --help
```

#### Setup Environment Variables
```bash
# Set up required environment variables
export PINECONE_API_KEY=your_api_key_here
export PINECONE_INDEX_NAME=your_index_name

# Or create .env file
echo "PINECONE_API_KEY=your_api_key_here" > .env
echo "PINECONE_INDEX_NAME=your_index_name" >> .env
```

## 🔒 Security

### Environment Variables
- **Never commit** `.env` files or hardcoded secrets to version control
- Use the provided `.env.example` as a template
- Store API keys and sensitive configuration in environment variables only

### Recommended Security Practices
- **Review Dependencies**: Regularly audit dependencies for vulnerabilities
- **Access Control**: Limit repository access when processing private repositories
- **API Keys**: Use read-only API keys when possible, rotate keys regularly
- **Local Processing**: Sensitive code processing happens locally before embedding

### Supported Environment Variables
```bash
# Pinecone (default vector store)
PINECONE_API_KEY=your_pinecone_api_key        # Required for Pinecone integration
PINECONE_INDEX_NAME=your_index_name           # Required for Pinecone integration
PINECONE_BATCH_SIZE=100                       # Optional: batch size for uploads

# Embedding providers
EMBEDDING_MODEL=nomic-ai/nomic-embed-text-v1.5  # Default model
OPENAI_API_KEY=your_openai_key                # Required for OpenAI embeddings

# Other providers (as you add them)
WEAVIATE_URL=http://localhost:8080            # For Weaviate vector store
QDRANT_URL=http://localhost:6333              # For Qdrant vector store
```

### Security Audit
Run dependency vulnerability checks:
```bash
# Install security audit tool
pip install pip-audit

# Check for vulnerabilities
pip-audit

# Or using pipenv
pipenv check
```

## 🤝 Contributing

Contributions are welcome! Feel free to submit pull requests or open issues for:
- Bug fixes
- New features
- Documentation improvements
- Additional language support

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

### Attribution Requirements
When using this software, you must:
- Include the copyright notice and license in any copy or substantial portion of the software
- State any significant changes made to the original code
- Include attribution to the original author (Sandeep G) in derivative works
