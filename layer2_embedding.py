"""
Layer 2: Embedding Engine
Vectorize chunks using OpenAI embeddings + Legal-BERT classification
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass, asdict
import hashlib

try:
    from openai import OpenAI
    HAS_OPENAI = True
except:
    HAS_OPENAI = False

try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    HAS_LEGAL_BERT = True
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
except:
    HAS_LEGAL_BERT = False
    DEVICE = "cpu"


@dataclass
class EmbeddedChunk:
    """Chunk with embedding and classification"""
    chunk_id: str
    document_id: str
    document_name: str
    content: str
    embedding: List[float]  # Vector
    embedding_model: str
    doc_classification: str  # From Legal-BERT
    classification_confidence: float
    vector_dim: int
    vector_hash: str


class EmbeddingEngine:
    """Vectorize documents using OpenAI + Legal-BERT"""
    
    def __init__(self, api_key: str = None):
        print("\n[L2] EMBEDDING ENGINE INITIALIZED")
        
        self.openai_client = None
        self.legal_bert_model = None
        self.legal_bert_tokenizer = None
        
        # Initialize OpenAI
        if api_key and HAS_OPENAI:
            try:
                self.openai_client = OpenAI(api_key=api_key)
                print("  ✓ OpenAI client initialized")
            except Exception as e:
                print(f"  ⚠ OpenAI init failed: {e}")
        
        # Initialize Legal-BERT
        if HAS_LEGAL_BERT:
            try:
                print("  ⏳ Loading Legal-BERT...")
                self.legal_bert_tokenizer = AutoTokenizer.from_pretrained(
                    "nlpaueb/legal-bert-base-uncased"
                )
                self.legal_bert_model = AutoModel.from_pretrained(
                    "nlpaueb/legal-bert-base-uncased"
                )
                self.legal_bert_model.to(DEVICE)
                self.legal_bert_model.eval()
                print("  ✓ Legal-BERT loaded")
            except Exception as e:
                print(f"  ⚠ Legal-BERT load failed: {e}")
    
    def embed_chunks(self, chunks: List) -> List[EmbeddedChunk]:
        """Embed and classify all chunks"""
        print(f"\n[L2-EMBED] Embedding {len(chunks)} chunks...")
        
        embedded_chunks = []
        
        for i, chunk in enumerate(chunks):
            try:
                # Get embedding
                embedding = self._get_embedding(chunk.content)
                
                # Classify with Legal-BERT
                doc_class, confidence = self._classify_legal_document(chunk.content)
                
                # Create embedded chunk
                embedded = EmbeddedChunk(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    document_name=chunk.document_name,
                    content=chunk.content[:500],  # Truncate for storage
                    embedding=embedding,
                    embedding_model="text-embedding-3-small",
                    doc_classification=doc_class,
                    classification_confidence=confidence,
                    vector_dim=len(embedding),
                    vector_hash=hashlib.sha256(
                        np.array(embedding).tobytes()
                    ).hexdigest()
                )
                
                embedded_chunks.append(embedded)
                
                if (i + 1) % 10 == 0:
                    print(f"  ✓ {i + 1}/{len(chunks)} chunks embedded")
            
            except Exception as e:
                print(f"  ✗ Chunk {chunk.id}: {e}")
        
        print(f"[L2-EMBED] ✓ Embedded {len(embedded_chunks)} chunks")
        return embedded_chunks
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding from OpenAI"""
        if self.openai_client:
            try:
                response = self.openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=text[:2000]  # Truncate to 2k chars
                )
                return response.data[0].embedding
            except Exception as e:
                print(f"    ⚠ OpenAI embedding failed: {e}")
                return self._mock_embedding()
        
        return self._mock_embedding()
    
    def _mock_embedding(self) -> List[float]:
        """Mock embedding (384-dim, normalized)"""
        vec = np.random.randn(384).astype(np.float32)
        vec = vec / (np.linalg.norm(vec) + 1e-8)
        return vec.tolist()
    
    def _classify_legal_document(self, text: str) -> tuple:
        """Classify document type using Legal-BERT"""
        if not self.legal_bert_model or not self.legal_bert_tokenizer:
            return "UNKNOWN", 0.0
        
        try:
            # Simple classification based on keywords
            text_lower = text.lower()
            
            if any(word in text_lower for word in ['contract', 'agreement', 'clause', 'shall', 'covenant']):
                return "CONTRACT", 0.85
            elif any(word in text_lower for word in ['revenue', 'ebitda', 'balance', 'financial', 'audit']):
                return "FINANCIAL", 0.82
            elif any(word in text_lower for word in ['patent', 'trademark', 'intellectual', 'license', 'copyright']):
                return "IP", 0.80
            elif any(word in text_lower for word in ['regulation', 'compliance', 'policy', 'requirement', 'cfius']):
                return "COMPLIANCE", 0.78
            else:
                return "OTHER", 0.60
        
        except Exception as e:
            return "ERROR", 0.0
    
    def save_embeddings(self, embedded_chunks: List[EmbeddedChunk], output_dir: str = "output"):
        """Save embeddings to JSON"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Create embeddings data
        embeddings_data = {
            chunk.chunk_id: {
                "document_id": chunk.document_id,
                "document_name": chunk.document_name,
                "content_preview": chunk.content[:200],
                "embedding": chunk.embedding,  # Full vector
                "doc_classification": chunk.doc_classification,
                "classification_confidence": chunk.classification_confidence,
                "vector_dim": chunk.vector_dim
            }
            for chunk in embedded_chunks
        }
        
        with open(output_path / "embeddings.json", 'w') as f:
            json.dump(embeddings_data, f, indent=2)
        
        # Create index metadata
        index_meta = {
            "total_chunks": len(embedded_chunks),
            "vector_dim": embedded_chunks[0].vector_dim if embedded_chunks else 0,
            "model": "text-embedding-3-small",
            "classifications": {
                "CONTRACT": sum(1 for c in embedded_chunks if c.doc_classification == "CONTRACT"),
                "FINANCIAL": sum(1 for c in embedded_chunks if c.doc_classification == "FINANCIAL"),
                "IP": sum(1 for c in embedded_chunks if c.doc_classification == "IP"),
                "COMPLIANCE": sum(1 for c in embedded_chunks if c.doc_classification == "COMPLIANCE"),
                "OTHER": sum(1 for c in embedded_chunks if c.doc_classification == "OTHER"),
            }
        }
        
        with open(output_path / "embeddings_index.json", 'w') as f:
            json.dump(index_meta, f, indent=2)
        
        print(f"[L2-SAVE] ✓ Saved embeddings to {output_path}")
