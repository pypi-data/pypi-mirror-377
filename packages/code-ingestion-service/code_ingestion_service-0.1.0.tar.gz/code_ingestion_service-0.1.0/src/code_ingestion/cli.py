#!/usr/bin/env python3
"""
Code Ingestion CLI

Simple CLI for ingesting code repositories into RAG pipelines.
Supports both local and remote repositories with basic file filtering.

Usage:
    code-ingestion /path/to/local/repo
    code-ingestion https://github.com/org/repo
    code-ingestion https://github.com/spring-projects/spring-boot --include "**/*.java"
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import List, Tuple, Optional

import click
from git import Repo
from git.exc import GitError

# Import new orchestrator
from .orchestration import create_ingestion_orchestrator
from . import __version__


# Default file patterns
DEFAULT_INCLUDE_PATTERNS = [
    "**/*.java",
    "**/*.py", 
    "**/*.js",
    "**/*.ts",
    "**/*.go",
    "**/*.rs",
    "**/*.cpp",
    "**/*.c",
    "**/*.h"
]

DEFAULT_EXCLUDE_PATTERNS = [
    "**/test/**",
    "**/tests/**", 
    "**/node_modules/**",
    "**/vendor/**",
    "**/build/**",
    "**/dist/**",
    "**/target/**",
    "**/.git/**",
    "**/*.min.js",
    "**/*.min.css"
]


def is_git_url(source: str) -> bool:
    """Check if source is a git URL."""
    return source.startswith(('http://', 'https://', 'git@', 'ssh://'))


def clone_repo(repo_url: str, target_dir: Path) -> None:
    """Clone repository with shallow clone for efficiency."""
    try:
        click.echo(f"🔄 Cloning {repo_url}...")
        Repo.clone_from(
            repo_url, 
            target_dir, 
            depth=1,  # Shallow clone - only latest commit
            single_branch=True
        )
        click.echo(f"✅ Successfully cloned to {target_dir}")
    except GitError as e:
        click.echo(f"❌ Failed to clone repository: {e}", err=True)
        sys.exit(1)


def find_matching_files(repo_path: Path, include_patterns: List[str], exclude_patterns: List[str]) -> List[Path]:
    """Find files matching include patterns and not matching exclude patterns."""
    import fnmatch
    
    matching_files = []
    
    for file_path in repo_path.rglob('*'):
        if not file_path.is_file():
            continue
            
        relative_path = file_path.relative_to(repo_path)
        relative_str = str(relative_path)
        
        # Check exclude patterns first (more efficient)
        excluded = any(fnmatch.fnmatch(relative_str, pattern) for pattern in exclude_patterns)
        if excluded:
            continue
            
        # Check include patterns
        included = any(fnmatch.fnmatch(relative_str, pattern) for pattern in include_patterns)
        if included:
            matching_files.append(file_path)
    
    return matching_files


def process_repository(repo_path: Path, include_patterns: List[str], exclude_patterns: List[str], 
                      max_files: Optional[int], embedding_provider: str, vector_store: str, verbose: bool) -> None:
    """Process repository files and ingest into RAG pipeline."""
    
    # Find matching files
    click.echo("🔍 Finding matching files...")
    matching_files = find_matching_files(repo_path, include_patterns, exclude_patterns)
    
    if not matching_files:
        click.echo("⚠️ No matching files found with current patterns", err=True)
        return
    
    # Apply max_files limit if specified
    if max_files and len(matching_files) > max_files:
        matching_files = matching_files[:max_files]
        click.echo(f"📊 Limited to {max_files} files")
    
    click.echo(f"📁 Found {len(matching_files)} files to process")
    
    # Prepare file content for orchestrator
    source_files = []
    for file_path in matching_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                relative_path = str(file_path.relative_to(repo_path))
                source_files.append((relative_path, content))
        except Exception as e:
            click.echo(f"❌ Could not read {file_path}: {str(e)}", err=True)
            continue
    
    if not source_files:
        click.echo("❌ No files could be read", err=True)
        return
    
    try:
        # Create and execute orchestrator
        orchestrator = create_ingestion_orchestrator(
            embedding_provider=embedding_provider,
            vector_store=vector_store,
            verbose=verbose
        )
        
        result = orchestrator.execute(source_files)
        
        if result.success:
            click.echo(f"🎉 Ingestion complete! {result.chunks_processed} chunks processed from {len(source_files)} files")
        else:
            click.echo("❌ Ingestion failed", err=True)
            
    except Exception as e:
        click.echo(f"❌ Ingestion failed: {str(e)}", err=True)
        return


@click.command()
@click.argument('source')
@click.option('--include', 'include_patterns', multiple=True, 
              help='File patterns to include (e.g., "**/*.java")')
@click.option('--exclude', 'exclude_patterns', multiple=True,
              help='File patterns to exclude (e.g., "**/test/**")')  
@click.option('--max-files', type=int, 
              help='Maximum number of files to process')
@click.option('--embedding-provider', default='nomic',
              help='Embedding provider to use (default: nomic)')
@click.option('--vector-store', default='pinecone',
              help='Vector store to use (default: pinecone)')
@click.option('--verbose', is_flag=True,
              help='Enable detailed logging and progress reports')
@click.option('--cleanup/--no-cleanup', default=True,
              help='Clean up temporary files after processing')
@click.version_option(version=__version__, prog_name="code-ingestion")
def cli(source: str, include_patterns: Tuple[str], exclude_patterns: Tuple[str], 
        max_files: Optional[int], embedding_provider: str, vector_store: str, 
        verbose: bool, cleanup: bool):
    """
    Ingest code repository for RAG pipeline.
    
    SOURCE can be either a local path or a git repository URL.
    
    Examples:
        code-ingestion /path/to/repo
        code-ingestion https://github.com/spring-projects/spring-boot
        code-ingestion https://github.com/org/repo --include "**/*.py" --max-files 100
    """
    
    # Use defaults if no patterns specified
    final_include = list(include_patterns) if include_patterns else DEFAULT_INCLUDE_PATTERNS
    final_exclude = list(exclude_patterns) if exclude_patterns else DEFAULT_EXCLUDE_PATTERNS
    
    click.echo("🚀 Starting code ingestion...")
    click.echo(f"📍 Source: {source}")
    click.echo(f"📄 Include patterns: {final_include}")
    click.echo(f"🚫 Exclude patterns: {final_exclude}")
    
    temp_dir = None
    
    try:
        if is_git_url(source):
            # Remote repository - clone to temp directory
            temp_dir = Path(tempfile.mkdtemp(prefix="code-ingest-"))
            clone_repo(source, temp_dir)
            repo_path = temp_dir
        else:
            # Local repository
            repo_path = Path(source)
            if not repo_path.exists():
                click.echo(f"❌ Path does not exist: {source}", err=True)
                sys.exit(1)
            click.echo(f"📁 Processing local repository: {repo_path}")
        
        # Process the repository
        process_repository(repo_path, final_include, final_exclude, max_files, 
                          embedding_provider, vector_store, verbose)
        
    finally:
        # Cleanup temporary directory
        if temp_dir and temp_dir.exists() and cleanup:
            click.echo("🧹 Cleaning up temporary files...")
            shutil.rmtree(temp_dir)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()