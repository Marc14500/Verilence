#!/usr/bin/env python3
"""
VERILENCE - Main Pipeline
Week 1: Ingestion + Chunking + Embedding
"""

import sys
from pathlib import Path

from layer1_ingestion import IngestionEngine
from layer2_embedding import EmbeddingEngine


def main():
    print("\n" + "="*70)
    print("VERILENCE - WEEK 1: INGESTION + CHUNKING + EMBEDDING")
    print("="*70)
    
    # Get document paths from user
    print("\n[INPUT] Enter document paths (comma-separated):")
    print("  Examples: data/doc1.pdf, data/doc2.txt, /path/to/folder")
    
    user_input = input("\n> ").strip()
    
    if not user_input:
        print("✗ No input provided")
        return
    
    # Parse input
    paths = [p.strip() for p in user_input.split(',')]
    
    # Step 1: Ingest documents
    print("\n" + "-"*70)
    print("STEP 1: DOCUMENT INGESTION")
    print("-"*70)
    
    ingester = IngestionEngine(chunk_size=512, chunk_overlap=64)
    documents = ingester.ingest_documents(paths)
    
    if not documents:
        print("✗ No documents loaded")
        return
    
    # Step 2: Chunk documents
    print("\n" + "-"*70)
    print("STEP 2: DOCUMENT CHUNKING")
    print("-"*70)
    
    chunks = ingester.chunk_documents()
    ingester.save_state("output")
    
    if not chunks:
        print("✗ No chunks created")
        return
    
    # Step 3: Embed chunks
    print("\n" + "-"*70)
    print("STEP 3: CHUNK EMBEDDING & CLASSIFICATION")
    print("-"*70)
    
    try:
        import os
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            print("⚠ OPENAI_API_KEY not set - using mock embeddings")
            print("  Set it with: export OPENAI_API_KEY='sk-...'")
    except:
        openai_key = None
    
    embedder = EmbeddingEngine(api_key=openai_key)
    embedded_chunks = embedder.embed_chunks(chunks)
    embedder.save_embeddings(embedded_chunks, "output")
    
    # Summary
    print("\n" + "="*70)
    print("WEEK 1 COMPLETE")
    print("="*70)
    
    print(f"\n✓ Documents: {len(documents)}")
    print(f"✓ Chunks: {len(chunks)}")
    print(f"✓ Embedded: {len(embedded_chunks)}")
    print(f"✓ Output: output/")
    
    print("\nFiles created:")
    print("  - documents.json (metadata)")
    print("  - chunks.json (chunked content)")
    print("  - embeddings.json (vectors)")
    print("  - embeddings_index.json (index metadata)")
    
    print("\nNext: RAG Retrieval Layer (Week 2)")
    print("="*70)


if __name__ == '__main__':
    main()
