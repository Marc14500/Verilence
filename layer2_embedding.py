import os
import json
import google.generativeai as genai

class EmbeddingLayer:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        self.embedded_chunks = []
    
    def embed_text(self, text):
        """Embed text using Gemini embedding-2-preview"""
        if not text or not text.strip():
            return None
        
        try:
            result = genai.embed_content(
                model="models/gemini-embedding-2-preview",
                content=text[:2000],
                task_type="retrieval_document"
            )
            if 'embedding' in result:
                return result['embedding']
            return None
        except Exception as e:
            print(f"[L2-EMBEDDING] Embed error: {e}")
            return None
    
    def embed_chunks(self, chunks):
        """Embed chunks with real vectors"""
        self.embedded_chunks = []
        
        for i, chunk in enumerate(chunks):
            text = chunk.get('content', '')
            
            if not text or not text.strip():
                continue
            
            embedding = self.embed_text(text)
            if embedding:
                self.embedded_chunks.append({
                    'id': chunk.get('chunk_id', f'chunk_{i}'),
                    'text': text,
                    'source': chunk.get('document_name', ''),
                    'chunk_index': i,
                    'embedding': embedding,
                    'metadata': {
                        'chunk_index': i,
                        'document': chunk.get('document_name', ''),
                        'section': chunk.get('section', 'Unknown'),
                        'keywords': chunk.get('keywords', [])
                    }
                })
        
        print(f"[L2-EMBEDDING] ✓ Embedded {len(self.embedded_chunks)} chunks")
        return self.embedded_chunks
    
    def save_embeddings(self, filepath):
        """Save embeddings to file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        save_data = [
            {k: v for k, v in chunk.items() if k != 'embedding'}
            for chunk in self.embedded_chunks
        ]
        
        with open(filepath, 'w') as f:
            json.dump(save_data, f, indent=2)
        print(f"[L2-EMBEDDING] ✓ Saved {len(save_data)} chunk metadata to {filepath}")
