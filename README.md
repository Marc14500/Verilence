# VERILENCE - Contradiction & Conflict Detection Engine

**Glass Box AI infrastructure for document analysis.**

## Quick Start
```bash
# 1. Start Qdrant (runs in Docker)
docker run -p 6333:6333 qdrant/qdrant &

# 2. Run analysis
python3 layer8_reporting.py

# 3. Check reports
open output/report_*.html
cat output/report_*.json
```

## Architecture

6-layer stack:
- **L1**: Ingestion (document loading + chunking)
- **L2**: Embedding (vectorization + classification)
- **L3**: RAG (Qdrant vector search + retrieval)
- **L4**: EBM (Explainable Boosting Machine for risk scoring)
- **L5**: LLM (Gemini synthesis + explanations)
- **L6**: Routing (Confidence-based human-in-the-loop)
- **L8**: Reporting (JSON + HTML generation)

## Key Features

- **Document-Agnostic**: Works with any document type
- **Interpretable**: EBM provides feature-level explanations
- **Confidence-Weighted**: Auto-routes findings based on certainty
- **Cited**: Every finding links to source passages
- **Scalable**: Qdrant handles millions of vectors

## Roadmap

- Week 7: Documentation ✓
- V1.1: API endpoints (FastAPI)
- V1.2: VDR integrations (Intralinks, Datasite)
- V1.3: Multi-tenant support
- V2.0: Neo4j knowledge graph

