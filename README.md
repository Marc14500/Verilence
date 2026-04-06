# VERILENCE
### Glass Box Contradiction Detection for Legal Documents

Verilence finds contradictions, conflicts, and ambiguities in complex legal documents — JOAs, purchase agreements, SOWs, M&A contracts — and produces a fully auditable Glass Box report in under 120 seconds.

**Core thesis:** Legal AI you can't explain is legal AI you can't trust. Every Verilence finding includes a complete mathematical audit trail showing exactly how risk and confidence were calculated.

---

## What It Does

Upload any legal document. Verilence:

1. Chunks and embeds the document using Legal-BERT (768-dim vectors)
2. Scores every chunk with an Explainable Boosting Machine (EBM) trained on 1,200 real contract clauses from the LEDGAR dataset
3. Sends the highest-risk chunks to Gemini 2.5 Pro for conflict synthesis — Gemini explains what the EBM found, it does not detect
4. Routes findings by risk level and confidence score
5. Generates a paginated Glass Box audit report with full math trail

---

## Validated On

- **New Dominion JOA** — 5 findings including operator agency contradiction and title cost billing conflict
- **ExxonMobil / Sable Offshore PSA** — findings on a $10B transaction with active environmental litigation, including an interim period remediation liability gap
- **Commercial SOW** — IP ownership ambiguity and milestone compensation contradictions
- Any searchable PDF legal document

---

## Architecture

| Layer | Component | Purpose |
|-------|-----------|---------|
| L1 | Ingestion | PDF extraction, legal section chunking |
| L2 | Embedding | Legal-BERT 768-dim vectors |
| L3 | RAG | Qdrant vector indexing |
| L4 | EBM | Glass Box risk scoring — drives the pipeline |
| L5 | Gemini 2.5 Pro | Conflict synthesis only — explains what EBM found |
| L6 | Routing | Risk × confidence routing matrix |
| L9 | Reporting | Paginated Glass Box audit report |
| Web | Dashboard | Enterprise risk dashboard + audit report |

**Key architectural decision:** EBM scores all chunks first. Only the highest-risk chunks are sent to Gemini. The interpretable model drives detection. The LLM synthesizes and explains. This minimizes hallucination and keeps the Glass Box story intact.

---

## Glass Box Confidence Scoring

Every finding is scored by 3 independent signals:

| Signal | What It Measures | Weight |
|--------|-----------------|--------|
| Text Clarity | Distance of risk score from ambiguous midpoint | 35% |
| Gemini 2.5 Pro | LLM confidence for this specific finding | 35% |
| Chunk Quality | Specificity of retrieved section quotes | 30% |

**Formula:** `Confidence = (Clarity × 0.35) + (Gemini × 0.35) + (Chunk × 0.30)`

All weights are disclosed. All calculations are reproducible. Any finding can be independently verified.

---

## Routing Decision Matrix

| Risk Score | Confidence | Routing |
|------------|------------|---------|
| ≥ 0.70 (HIGH) | Any | Senior Partner Escalation |
| 0.40–0.69 (MEDIUM) | > 60% | Analyst Review |
| < 0.40 (LOW) | > 85% | Auto Approve |

---

## EBM Training Data

The EBM is trained on 1,200 real contract clauses from **LEDGAR** (lex_glue), a published legal dataset of 60,000 labeled contract provisions across 100 clause categories. Training data is balanced across high-risk (financial, liability, IP), medium-risk (governance, compliance), and low-risk (boilerplate, drafting errors) clause types.

**Calibration status:** Uncalibrated — pre-pilot. Scores will improve as pilot operator feedback is incorporated.

---

## Quick Start
```bash
# Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Start Verilence
cd ~/verilence
export GOOGLE_API_KEY='your-key'
python3 app.py
```

Visit `http://localhost:5000` — upload any legal document PDF.

---

## Use Cases

**Current (Phase 1)**
- JOA contradiction detection before signing
- M&A purchase agreement risk screening
- SOW and commercial contract review
- Any complex legal document analysis

**Roadmap**
- Phase 2: Batch processing, VDR integration, portfolio dashboard
- Phase 3: Cross-document contradiction detection, knowledge graph
- Phase 4: Enterprise API, SSO, multi-tenant, white-label

---

## Status

**Beta — working prototype, not production hardened**

- Core engine: Working
- Glass Box framework: Validated on real documents
- EBM: Trained on LEDGAR real contract data
- Dashboard: Enterprise-grade UI
- Audit report: Paginated Glass Box report
- Security: Needs hardening before enterprise deployment
- Infrastructure: Cloud Shell / local — needs AWS migration

---

## License

Proprietary — Verilence LLC

## Contact

Marc Greaves  
Verilence LLC · Richmond, VA  
