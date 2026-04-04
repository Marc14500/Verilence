#!/usr/bin/env python3
import sys
from layer1_ingestion import IngestionEngine
from layer2_embedding import EmbeddingEngine
from layer3_rag import RAGEngine

def main():
    print("\n" + "="*70)
    print("VERILENCE - WEEK 2: RAG RETRIEVAL + CITATIONS")
    print("="*70)
    
    # Check if we have embeddings from Week 1
    import os
    if not os.path.exists("output/embeddings.json"):
        print("✗ No embeddings found. Run Week 1 first:")
        print("  python3 pipeline.py")
        return
    
    # Initialize RAG engine
    rag = RAGEngine("output/embeddings.json")
    
    # Interactive query loop
    print("\n[READY] RAG engine ready for queries")
    print("Type 'quit' to exit\n")
    
    while True:
        query = input("[QUERY] > ").strip()
        
        if query.lower() == 'quit':
            print("✗ Exiting")
            break
        
        if not query:
            continue
        
        # Retrieve
        result = rag.retrieve(query, top_k=5)
        
        # Display results
        if result.citations:
            print(f"\n[RESULTS] {len(result.citations)} relevant passages found")
            print(f"[SCORE] Retrieval score: {result.retrieval_score:.2f}\n")
            
            for i, citation in enumerate(result.citations, 1):
                print(f"--- Citation {i} ---")
                print(f"Document: {citation['document_name']}")
                print(f"Relevance: {citation['relevance_score']:.2f}")
                print(f"Excerpt: {citation['content_excerpt'][:150]}...")
                print()
        else:
            print("[RESULTS] ✗ No relevant passages found\n")
        
        # Save retrieval
        rag.save_retrieval(result, "output")

if __name__ == '__main__':
    main()
