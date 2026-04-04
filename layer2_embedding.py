#!/usr/bin/env python3
"""Layer 2: Embedding Layer - Legal-BERT encoding"""

from transformers import AutoTokenizer, AutoModel
import torch
import json
import numpy as np

class EmbeddingLayer:
    def __init__(self):
        print("\n[L2] EMBEDDING LAYER")
        self.model_name = "nlpaueb/legal-bert-base-uncased"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)
        self.embeddings = []
    
    def embed_chunks(self, chunks):
        """Generate embeddings for chunks"""
        print(f"[L2-EMBED] Embedding {len(chunks)} chunks...")
        
        self.embeddings = []
        
        for chunk in chunks:
            # Handle both dict and object formats
            if isinstance(chunk, dict):
                text = chunk.get('content', '')
                chunk_id = chunk.get('chunk_id', '')
            else:
                text = getattr(chunk, 'content', '')
                chunk_id = getattr(chunk, 'chunk_id', '')
            
            # Truncate and clean
            text = str(text)[:512]
            
            try:
                # Tokenize
                inputs = self.tokenizer(
                    text,
                    return_tensors="pt",
                    truncation=True,
                    padding=True,
                    max_length=512
                )
                
                # Get embeddings
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    # Use [CLS] token embedding
                    embedding = outputs.last_hidden_state[:, 0, :].squeeze().numpy()
                
                # Normalize
                embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
                
                self.embeddings.append({
                    'vector': embedding.tolist(),
                    'chunk_id': str(chunk_id)
                })
            except Exception as e:
                print(f"[L2-EMBED] Warning: Could not embed chunk: {e}")
                # Use zero vector as fallback
                self.embeddings.append({
                    'vector': [0.0] * 768,
                    'chunk_id': str(chunk_id)
                })
        
        print(f"[L2-EMBED] ✓ Embedded {len(self.embeddings)} chunks")
    
    def save_embeddings(self, path):
        """Save embeddings to JSON"""
        output = {
            'embeddings': self.embeddings,
            'model': 'nlpaueb/legal-bert-base-uncased',
            'dimension': 768,
            'count': len(self.embeddings)
        }
        
        with open(path, 'w') as f:
            json.dump(output, f)
        
        print(f"[L2-SAVE] ✓ Saved {len(self.embeddings)} embeddings to {path}")

