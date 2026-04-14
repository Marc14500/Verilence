#!/usr/bin/env python3
"""Layer 1: Document Ingestion with section preservation"""
import pdfplumber
import json
import os
import re

class IngestionEngine:
    def __init__(self):
        print("\n[L1] INGESTION ENGINE INITIALIZED")
        self.documents = []
        self.chunks = []

    def load_documents(self, folder_path):
        print(f"[L1-INGEST] Loading documents from {folder_path}...")
        for filename in os.listdir(folder_path):
            if filename.endswith(('.pdf', '.txt')):
                filepath = os.path.join(folder_path, filename)
                print(f"  ✓ Loading {filename}...")
                
                if filename.endswith('.pdf'):
                    with pdfplumber.open(filepath) as pdf:
                        text = ""
                        for page in pdf.pages:
                            text += page.extract_text() or ""
                else:
                    with open(filepath, 'r') as f:
                        text = f.read()
                
                self.documents.append({
                    'filename': filename,
                    'text': text,
                    'char_count': len(text)
                })
        
        print(f"[L1-INGEST] ✓ Loaded {len(self.documents)} documents")
        return self.documents

    def chunk_documents(self):
        """Chunk by articles/sections - no overlap"""
        print(f"[L1-CHUNK] Chunking {len(self.documents)} documents...")
        self.chunks = []
        
        for doc in self.documents:
            text = doc['text']
            
            # Split by article headers
            article_pattern = r'(ARTICLE\s+[A-Z0-9\.]+|Section\s+[0-9\.]+)'
            parts = re.split(article_pattern, text)
            
            chunk_index = 0
            current_section = "PREAMBLE"
            
            for i, part in enumerate(parts):
                part = part.strip()
                if not part:
                    continue
                
                # If this is a header, update section and get content
                if re.match(r'^(ARTICLE|Section)', part):
                    current_section = part[:80]
                    # Next part is the content
                    if i + 1 < len(parts):
                        content = parts[i + 1].strip()
                        if content:
                            self.chunks.append({
                                'chunk_id': f'chunk_{chunk_index}',
                                'document_name': doc['filename'],
                                'content': content,
                                'section': current_section,
                                'chunk_index': chunk_index
                            })
                            chunk_index += 1
            
            print(f"  ✓ {doc['filename']}: {len([c for c in self.chunks if c['document_name'] == doc['filename']])} chunks")
        
        print(f"[L1-CHUNK] ✓ Created {len(self.chunks)} total chunks")
        return self.chunks

    def save_chunks(self, chunks, output_path='output/chunks.json'):
        """Save chunks with section info"""
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(chunks, f, indent=2)
        print(f"[L1-SAVE] ✓ Saved {len(chunks)} chunks to {output_path}")
