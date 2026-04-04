"""
Verilence Configuration
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories
for d in [DATA_DIR, OUTPUT_DIR, LOGS_DIR]:
    d.mkdir(exist_ok=True)

# API Keys
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Model configuration
EMBEDDING_MODEL = "text-embedding-3-small"
LEGAL_BERT_MODEL = "nlpaueb/legal-bert-base-uncased"

# Chunking configuration
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64

# Ingestion configuration
MAX_DOCUMENT_SIZE = 50_000_000  # 50MB
SUPPORTED_FORMATS = ['.pdf', '.txt', '.docx', '.xlsx', '.csv', '.json']

# Database
VECTOR_DB_PATH = DATA_DIR / "vector_store"

print("✓ Config loaded")
