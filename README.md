# VERILENCE

Glass Box contradiction detection engine for legal documents (JOAs, contracts, agreements).

## Overview

Verilence uses Explainable Boosting Machine (EBM) + LLM synthesis to find contradictions in legal documents with full mathematical auditability and Glass Box transparency.

**Core Thesis:** Lawyers shouldn't trust AI they can't understand. Every finding includes complete audit trail showing exactly why we're confident.

## Quick Start
```bash
# Terminal 1: Start Qdrant vector database
docker run -p 6333:6333 qdrant/qdrant

# Terminal 2: Start web server
cd ~/verilence
export GOOGLE_API_KEY='your-google-api-key'
python3 app.py
```

Visit `http://localhost:5000`

## Upload a Document

1. Click upload zone (or drag & drop)
2. Submit PDF or TXT
3. Wait 30-60 seconds for analysis
4. View audit report with:
   - Contradiction findings
   - Confidence scores (0-100%)
   - Mathematical proof of each score
   - Routing decision (analyst review, partner escalation, etc.)
   - Export as PDF, CSV, or email

## Architecture

**9-Layer System:**

| Layer | Component | Purpose |
|-------|-----------|---------|
| L1 | Ingestion | PDF/text extraction, smart chunking |
| L2 | Embedding | Legal-BERT (768-dim vectors) |
| L3 | RAG | Qdrant vector search & retrieval |
| L4 | EBM | Glass Box risk scoring |
| L5 | LLM | Gemini 2.5 Pro contradiction synthesis |
| L6 | Routing | Confidence-based human-in-the-loop |
| L9 | Reporting | Audit-ready HTML/JSON reports |
| Web | UI | Upload, analyze, export, learn |

## Confidence Scoring

Every finding gets a **confidence score (0-100%)** from 3 independent signals:

1. **Text Clarity (35%)** - How obvious is the contradiction in the document?
2. **LLM Reliability (35%)** - Google Gemini 2.5 Pro production AI
3. **Retrieval Quality (30%)** - Did we pull the right document chunks?

**Formula:**
**Routing Rules:**
- Confidence > 85%: AUTO_APPROVE
- Confidence 60-85%: ANALYST_REVIEW
- Confidence < 60%: SENIOR_PARTNER_ESCALATION

## Key Features

✅ **Glass Box Framework** - Every number is auditable and transparent
✅ **Mathematical Proof** - Findings include complete calculation audit trail
✅ **Production AI** - Uses Google Gemini 2.5 Pro (not experimental)

✅ **Multiple Export Formats** - PDF reports, CSV findings, email sharing
✅ **No Black Box** - You can see exactly why we found each contradiction

## Files
## How It Works

1. **Ingest** - Extract text from PDF/document
2. **Chunk** - Break into logical sections (ARTICLE I, Section 2.3, etc.)
3. **Embed** - Convert to 768-dimensional vectors using Legal-BERT
4. **Search** - Query Qdrant for relevant chunks
5. **Score** - Use EBM to calculate risk score for each finding
6. **Synthesize** - Use Gemini to explain contradiction in business language
7. **Route** - Decide if analyst/partner review needed based on confidence
8. **Report** - Generate audit-ready HTML/JSON with complete math trail

## Use Cases

- **M&A Due Diligence** - Find contradictions in target company JOAs
- **Portfolio Risk** - Scan all agreements for exposure
- **Contract Review** - Flag ambiguities before signing
- **Regulatory Compliance** - Audit trail for SOX/FCPA reviews

## Roadmap

**Phase 1 (NOW)** ✅
- Single document analysis
- Audit-ready reporting
- Web UI with export

**Phase 2 (Months 3-6)**
- VDR integration (Datasite, Intralinks, S3)
- Batch processing (analyze 50+ documents)
- Portfolio dashboard

**Phase 3 (Months 6-12)**
- Cross-document contradiction detection
- Knowledge graph for O&G relationships
- API endpoints

**Phase 4 (Year 2+)**
- Enterprise (SSO, RBAC, white-label)
- Multi-tenant support
- Advanced analytics

## Requirements
See `requirements.txt` for Python dependencies.

## Installation
```bash
pip install -r requirements.txt --break-system-packages
docker run -p 6333:6333 qdrant/qdrant
export GOOGLE_API_KEY='your-key'
python3 app.py
```

## Performance

- Single document: 30-60 seconds
- PDF extraction: pdfplumber
- Embedding: Legal-BERT (local, GPU-optimized if available)
- Vector search: Qdrant (subsecond)
- LLM synthesis: Gemini 2.5 Pro (10-15 seconds)

## Security

- No data stored externally (local Qdrant)
- API keys not logged
- Reports encrypted at rest
- Reproducible (same input = same output)
- Audit trail for every finding

## Testing

Upload `Bakken_JOA_Amended_Restated_Full.docx.pdf` to see:
- 9 real contradictions detected
- Confidence scores: 64-89%
- Complete audit trails
- Routing decisions

## Status

**MVP (Minimum Viable Product)**
- Core engine working
- Glass Box framework validated
- Audit reports production-ready
- Code: Alpha (needs production hardening)

**Next:** Code cleanup, AWS migration, SOC 2 compliance (6 months, $250K)

## License

Proprietary - Verilence LLC

## Contact

Marc Greaves
Verilence LLC
Richmond, VA
