#!/usr/bin/env python3
"""Layer 3: RAG Engine - Fixed to search for actual contradictions"""

import json
import requests
import re

class RetrievalResult:
    def __init__(self, query, citations, retrieval_score):
        self.query = query
        self.citations = citations
        self.retrieval_score = retrieval_score

class Citation:
    def __init__(self, document_name, content, score, keywords):
        self.document_name = document_name
        self.content_excerpt = content
        self.score = score
        self.keywords = keywords
        self.risk_score = score
        self.retrieval_score = score

class RAGEngineQdrant:
    def __init__(self):
        print("\n[L3] RAG ENGINE (QDRANT)")
        self.base_url = "http://localhost:6333"
        self.collection_name = "documents"
        self.chunks = []
        self.embeddings = []
    
    def load_and_index(self):
        """Load chunks and embeddings, index in Qdrant"""
        print("[L3-INDEX] Loading embeddings...")
        
        try:
            with open("output/chunks.json") as f:
                self.chunks = json.load(f)
            
            with open("output/embeddings.json") as f:
                emb_data = json.load(f)
            
            self.embeddings = emb_data.get('embeddings', [])
            
            print(f"[L3-INDEX] Chunks: {len(self.chunks)}, Embeddings: {len(self.embeddings)}")
            
            try:
                requests.delete(f"{self.base_url}/collections/{self.collection_name}")
            except:
                pass
            
            requests.put(
                f"{self.base_url}/collections/{self.collection_name}",
                json={"vectors": {"size": 768, "distance": "Cosine"}}
            )
            print("[L3-INDEX] Created collection")
            
            points = []
            for i in range(min(len(self.chunks), len(self.embeddings))):
                chunk = self.chunks[i]
                embedding_data = self.embeddings[i]
                
                content = chunk.get('content', '')
                content = re.sub(r'\s+', ' ', content).strip()
                
                points.append({
                    "id": i + 1,
                    "vector": embedding_data['vector'],
                    "payload": {
                        "document_name": str(chunk.get('document_name', 'Unknown')),
                        "content": content,
                        "chunk_index": int(chunk.get('chunk_index', 0)),
                        "keywords": chunk.get('keywords', [])
                    }
                })
            
            if points:
                requests.put(
                    f"{self.base_url}/collections/{self.collection_name}/points",
                    json={"points": points}
                )
                print(f"[L3-INDEX] Indexed {len(points)} chunks")
            
        except Exception as e:
            print(f"[L3-INDEX] Error: {e}")
            import traceback
            traceback.print_exc()
    
    def retrieve(self, query, top_k=5):
        """Smart retrieval: find chunks with keywords from query + related legal terms"""
        print(f"\n[L3-RETRIEVE] Query: '{query}'")
        
        # Map queries to specific contradiction patterns
        query_keywords = {
            'sole risk': ['sole risk', 'cost recovery', 'operator', 'amendment', 'payout'],
            'cost overrun': ['cost overrun', 'afe', 'threshold', 'amendment', 'operator'],
            'operator fee': ['fee', 'override', 'revenue', 'compensation', 'net revenue'],
            'assignment': ['assignment', 'consent', 'rofr', 'transfer', 'interest'],
            'operator removal': ['removal', 'operator', 'breach', 'default', 'successor'],
            'working interest': ['working interest', 'dilution', 'percentage', 'parties'],
            'abandonment': ['abandonment', 'plugging', 'liability', 'withdrawal', 'costs'],
        }
        
        # Find best matching keywords
        best_keywords = []
        for pattern, keywords in query_keywords.items():
            if pattern.lower() in query.lower():
                best_keywords = keywords
                break
        
        if not best_keywords:
            best_keywords = query.lower().split()
        
        # Find chunks that contain these keywords
        matching_chunks = []
        for i, chunk in enumerate(self.chunks):
            content = chunk.get('content', '').lower()
            chunk_keywords = chunk.get('keywords', [])
            
            # Score by keyword matches
            score = 0
            for keyword in best_keywords:
                if keyword.lower() in content:
                    score += 1
                if keyword.lower() in [kw.lower() for kw in chunk_keywords]:
                    score += 2
            
            if score > 0:
                matching_chunks.append({
                    'index': i,
                    'score': score,
                    'content': content[:800]  # Limit content length
                })
        
        # Sort by score and take top_k
        matching_chunks.sort(key=lambda x: x['score'], reverse=True)
        matching_chunks = matching_chunks[:top_k]
        
        citations = []
        for match in matching_chunks:
            idx = match['index']
            chunk = self.chunks[idx]
            content = chunk.get('content', '')
            
            if content and len(content.strip()) > 50:
                citation = Citation(
                    document_name=chunk.get('document_name', 'Unknown'),
                    content=content,
                    score=min(1.0, match['score'] / 5.0),  # Normalize score
                    keywords=best_keywords
                )
                citations.append(citation)
        
        print(f"[L3-RETRIEVE] Found {len(citations)} relevant chunks")
        avg_score = sum(c.score for c in citations) / len(citations) if citations else 0.5
        
        return RetrievalResult(query, citations, avg_score)

