#!/usr/bin/env python3
import sys
import os
from layer3_rag_qdrant import RAGEngineQdrant

def main():
    print("\n" + "="*70)
    print("VERILENCE - WEEK 2: RAG RETRIEVAL + QDRANT")
    print("="*70)
    
    if not os.path.exists("output/embeddings.json"):
        print("Error: Run Week 1 first")
        return
    
    print("\nInitializing RAG engine...")
    rag = RAGEngineQdrant(qdrant_url="http://localhost:6333", collection_name="verilence")
    
    print("Indexing embeddings...")
    rag.load_and_index("output/embeddings.json", "output/chunks.json")
    
    print("\n[READY] Type queries or 'quit' to exit\n")
    
    while True:
        query = input("[QUERY] > ").strip()
        if query.lower() == 'quit':
            break
        if not query:
            continue
        
        result = rag.retrieve(query, top_k=5)
        
        if result.citations:
            print(f"\nFound {len(result.citations)} passages:\n")
            for i, citation in enumerate(result.citations, 1):
                doc = citation.get('document', 'Unknown')
                content = citation.get('content') or '(no content)'
                score = citation.get('score', 0)
                
                print(f"[{i}] {doc} (score: {score:.2f})")
                if content and content != '(no content)':
                    print(f"    {str(content)[:100]}...")
                print()
        else:
            print("No results\n")
        
        rag.save_retrieval(result, "output")

if __name__ == '__main__':
    main()

