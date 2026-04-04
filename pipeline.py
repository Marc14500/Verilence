#!/usr/bin/env python3
import sys
from layer1_ingestion import IngestionEngine
from layer2_embedding import EmbeddingEngine

def main():
    print("\n" + "="*70)
    print("VERILENCE - WEEK 1: INGESTION + CHUNKING + EMBEDDING")
    print("="*70)
    
    user_input = input("\n[INPUT] Enter document paths (comma-separated):\n> ").strip()
    
    if not user_input:
        print("✗ No input provided")
        return
    
    paths = [p.strip() for p in user_input.split(',')]
    
    # Step 1: Ingest
    ingester = IngestionEngine(chunk_size=512, chunk_overlap=64)
    documents = ingester.ingest_documents(paths)
    
    if not documents:
        print("✗ No documents loaded")
        return
    
    # Step 2: Chunk
    chunks = ingester.chunk_documents()
    ingester.save_state("output")
    
    if not chunks:
        print("✗ No chunks created")
        return
    
    # Step 3: Embed
    embedder = EmbeddingEngine()
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
    print("\nNext: RAG Retrieval Layer (Week 2)")

if __name__ == '__main__':
    main()
