import os
from pathlib import Path

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
VARIANTS_DIR = DATA_DIR / "variants"
ACCEPTED_DIR = DATA_DIR / "accepted"
FEATURES_DIR = DATA_DIR / "features"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/verilence")

# Lab settings
NUM_VARIANTS_PER_CLAUSE = 5
BATCH_SIZE = 10
THINKING_BUDGET_TOKENS = 8000
MAX_OUTPUT_TOKENS = 2000

print(f"Config loaded. Data dir: {DATA_DIR}")
