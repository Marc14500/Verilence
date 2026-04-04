#!/usr/bin/env python3
"""Layer 1: Ingestion Engine - Fixed PDF Extraction"""

import pdfplumber
import re
from pathlib import Path
import json

class IngestionEngine:
    def __init__(self):
        print("\n[L1] INGESTION ENGINE INITIALIZED")
        self.documents = []
    
    def load_documents(self, upload_dir="uploads"):
        """Load and extract text from PDFs and TXT files"""
        print(f"[L1-INGEST] Loading {len(list(Path(upload_dir).glob('*')))} documents...")
        
        self.documents = []
        
        for file_path in sorted(Path(upload_dir).glob("*")):
            if file_path.is_file():
                text = None
                
                if file_path.suffix.lower() == ".pdf":
                    text = self._extract_pdf_text(file_path)
                elif file_path.suffix.lower() == ".txt":
                    with open(file_path, encoding='utf-8', errors='ignore') as f:
                        text = f.read()
                
                if text and len(text.strip()) > 100:  # Only keep if meaningful content
                    self.documents.append({
                        'filename': file_path.name,
                        'content': text,
                        'length': len(text)
                    })
                    print(f"  ✓ {file_path.name}: {len(text)} chars extracted")
        
        print(f"[L1-INGEST] ✓ Loaded {len(self.documents)} documents")
        return self.documents
    
    def _extract_pdf_text(self, pdf_path):
        """Extract text from PDF using pdfplumber"""
        try:
            text_pages = []
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        text = page.extract_text()
                        if text and len(text.strip()) > 50:
                            text_pages.append(text)
                    except:
                        pass
            
            if text_pages:
                full_text = "\n".join(text_pages)
                return full_text
            else:
                print(f"[L1-WARN] No text extracted from {pdf_path.name}")
                return None
        except Exception as e:
            print(f"[L1-ERROR] Failed to extract {pdf_path.name}: {e}")
            return None
    
    def chunk_documents(self, chunk_size=1200, overlap=150):
        """Chunk documents smartly by sections"""
        print(f"[L1-CHUNK] Chunking {len(self.documents)} documents...")
        
        chunks = []
        chunk_id = 0
        
        for doc in self.documents:
            content = doc['content']
            doc_chunks = 0
            
            # Split on ARTICLE or Section headers for legal docs
            sections = re.split(r'(?=ARTICLE\s+[IVX]+|Section\s+\d+\.)', content)
            
            current_chunk = ""
            for section in sections:
                if len(section.strip()) < 20:
                    continue
                
                # If adding this section exceeds chunk_size, save current chunk
                if len(current_chunk) + len(section) > chunk_size and current_chunk.strip():
                    chunks.append({
                        'chunk_id': f"chunk_{chunk_id}",
                        'document_name': doc['filename'],
                        'content': current_chunk.strip(),
                        'chunk_index': doc_chunks,
                        'keywords': self._extract_keywords(current_chunk)
                    })
                    chunk_id += 1
                    doc_chunks += 1
                    
                    # Overlap: keep last part of previous chunk
                    current_chunk = current_chunk[-overlap:] if len(current_chunk) > overlap else ""
                
                current_chunk += section
            
            # Save final chunk
            if current_chunk.strip() and len(current_chunk) > 50:
                chunks.append({
                    'chunk_id': f"chunk_{chunk_id}",
                    'document_name': doc['filename'],
                    'content': current_chunk.strip(),
                    'chunk_index': doc_chunks,
                    'keywords': self._extract_keywords(current_chunk)
                })
                chunk_id += 1
                doc_chunks += 1
            
            print(f"  ✓ {doc['filename']}: {doc_chunks} chunks")
        
        print(f"[L1-CHUNK] ✓ Created {len(chunks)} total chunks")
        return chunks
    
    def _extract_keywords(self, text):
        """Extract legal keywords present in text"""
        legal_keywords = [
            'sole risk', 'cost recovery', 'working interest', 'operator',
            'assignment', 'rofr', 'preferential right', 'consent',
            'afe', 'expenditure', 'override', 'royalty',
            'cash call', 'default', 'breach', 'amendment',
            'contradiction', 'inconsistency', 'conflict', 'ambiguity',
            'foreclosure', 'withdrawal', 'abandon', 'drilling'
        ]
        
        text_lower = text.lower()
        found = [kw for kw in legal_keywords if kw in text_lower]
        return list(dict.fromkeys(found))[:15]  # Remove duplicates, return top 15
    
    def save_chunks(self, chunks, output_path="output/chunks.json"):
        """Save chunks to JSON"""
        Path("output").mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(chunks, f, indent=2)
        
        print(f"[L1-SAVE] ✓ Saved {len(chunks)} chunks to {output_path}")
        return chunks

