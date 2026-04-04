import json
import numpy as np
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class Citation:
    chunk_id: str
    document_name: str
    content_excerpt: str
    char_offset_start: int
    char_offset_end: int
    relevance_score: float

@dataclass
class RetrievedResult:
    query: str
    matching_chunks: List[Dict]
    citations: List[Dict]
    retrieval_score: float
    timestamp: str

class RAGEngine:
    def __init__(self, embeddings_path: str = "output/embeddings.json"):
        print("\n[L3] RAG ENGINE INITIALIZED")
        self.embeddings_data = self._load_embeddings(embeddings_path)
        self.chunks_data = self._load_chunks("output/chunks.json")
        print(f"[L3] Loaded {len(self.embeddings_data)} embeddings")
    
    def _load_embeddings(self, path: str):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[L3] ✗ Failed to load embeddings: {e}")
            return {}
    
    def _load_chunks(self, path: str):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[L3] ✗ Failed to load chunks: {e}")
            return []
    
    def retrieve(self, query: str, top_k: int = 5) -> RetrievedResult:
        """Retrieve most relevant chunks for query"""
        print(f"\n[L3-RETRIEVE] Query: '{query}'")
        
        # Mock: score all chunks by keyword match
        scores = []
        query_words = set(query.lower().split())
        
        for chunk_id, chunk_data in self.embeddings_data.items():
            content = chunk_data.get('content', '').lower()
            chunk_words = set(content.split())
            
            # Jaccard similarity
            if len(chunk_words) > 0:
                overlap = len(query_words & chunk_words)
                union = len(query_words | chunk_words)
                score = overlap / union if union > 0 else 0
            else:
                score = 0
            
            scores.append({
                'chunk_id': chunk_id,
                'document_name': chunk_data.get('document_name'),
                'content': chunk_data.get('content'),
                'classification': chunk_data.get('doc_classification'),
                'score': score
            })
        
        # Sort by score
        scores.sort(key=lambda x: x['score'], reverse=True)
        top_results = scores[:top_k]
        
        # Filter out zero scores
        top_results = [r for r in top_results if r['score'] > 0]
        
        if not top_results:
            print("[L3-RETRIEVE] ✗ No relevant chunks found")
            return RetrievedResult(
                query=query,
                matching_chunks=[],
                citations=[],
                retrieval_score=0.0,
                timestamp=datetime.now().isoformat()
            )
        
        # Create citations
        citations = []
        for result in top_results:
            citation = Citation(
                chunk_id=result['chunk_id'],
                document_name=result['document_name'],
                content_excerpt=result['content'][:200],
                char_offset_start=0,
                char_offset_end=len(result['content']),
                relevance_score=result['score']
            )
            citations.append(asdict(citation))
        
        avg_score = np.mean([r['score'] for r in top_results])
        
        print(f"[L3-RETRIEVE] ✓ Found {len(top_results)} relevant chunks (avg score: {avg_score:.2f})")
        
        return RetrievedResult(
            query=query,
            matching_chunks=top_results,
            citations=citations,
            retrieval_score=float(avg_score),
            timestamp=datetime.now().isoformat()
        )
    
    def save_retrieval(self, result: RetrievedResult, output_dir: str = "output"):
        Path(output_dir).mkdir(exist_ok=True)
        
        output_data = {
            'query': result.query,
            'retrieval_score': result.retrieval_score,
            'num_results': len(result.matching_chunks),
            'citations': result.citations,
            'timestamp': result.timestamp
        }
        
        # Save with timestamp
        filename = f"{output_dir}/retrieval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"[L3-SAVE] ✓ Saved to {filename}")
