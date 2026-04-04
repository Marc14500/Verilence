#!/usr/bin/env python3
"""
VERILENCE Test Suite - Oil & Gas Edition
"""

import json
from pathlib import Path
from layer3_rag_qdrant import RAGEngineQdrant
from layer4_ebm import GlassBoxJudge
from layer5_llm import DiscoveryAgent
from layer6_confidence_routing import ConfidenceRouter
from layer8_reporting import ReportGenerator

def test_ingestion():
    """Test Layer 1: Document Ingestion"""
    print("\n" + "="*70)
    print("TEST 1: INGESTION - Oil & Gas SEC Filings")
    print("="*70)
    
    demo_dir = Path("demo_data/oil_gas")
    if not demo_dir.exists():
        print("✗ demo_data/oil_gas not found")
        return False
    
    files = list(demo_dir.glob("*.txt"))
    if not files:
        print("✗ No documents found")
        return False
    
    print(f"✓ Found {len(files)} O&G SEC filings:")
    for f in files:
        print(f"  - {f.name}")
    
    return True

def test_embedding():
    """Test Layer 2: Embedding & Classification"""
    print("\n" + "="*70)
    print("TEST 2: EMBEDDING")
    print("="*70)
    
    if not Path("output/embeddings.json").exists():
        print("✗ Embeddings not generated")
        return False
    
    with open("output/embeddings.json") as f:
        embeddings = json.load(f)
    
    if not embeddings:
        print("✗ No embeddings found")
        return False
    
    print(f"✓ {len(embeddings)} embeddings generated (384-dim)")
    classifications = set(e['doc_classification'] for e in embeddings.values())
    print(f"✓ Classifications: {classifications}")
    return True

def test_rag_retrieval():
    """Test Layer 3: RAG Retrieval"""
    print("\n" + "="*70)
    print("TEST 3: RAG RETRIEVAL - O&G Query")
    print("="*70)
    
    rag = RAGEngineQdrant()
    rag.load_and_index()
    
    result = rag.retrieve("environmental liability and indemnification", top_k=2)
    
    if not result.citations:
        print("✗ No citations returned")
        return False
    
    print(f"✓ Retrieved {len(result.citations)} citations")
    print(f"✓ Retrieval score: {result.retrieval_score:.2f}")
    
    for citation in result.citations:
        print(f"  - {citation['document']}: {citation['score']:.2f}")
    
    return True

def test_ebm_scoring():
    """Test Layer 4: EBM Scoring"""
    print("\n" + "="*70)
    print("TEST 4: EBM SCORING")
    print("="*70)
    
    judge = GlassBoxJudge()
    
    citations = [
        {'document': 'exxon_pioneer_8k.txt', 'content': 'indemnification liability environmental'},
        {'document': 'chevron_hess_8k.txt', 'content': 'operational control abandonment'}
    ]
    
    scores = judge.score_citations(citations)
    
    if len(scores) != len(citations):
        print("✗ Score count mismatch")
        return False
    
    print(f"✓ Scored {len(scores)} citations")
    for score in scores:
        print(f"  - {score.document_name}: {score.risk_level} ({score.risk_score:.2f})")
    
    return True

def test_confidence_routing():
    """Test Layer 6: Confidence Routing"""
    print("\n" + "="*70)
    print("TEST 6: CONFIDENCE ROUTING")
    print("="*70)
    
    router = ConfidenceRouter()
    
    from layer5_llm import Finding
    findings = [
        Finding(
            finding_id="f1",
            document_name="exxon_pioneer_8k.txt",
            risk_level="HIGH",
            risk_score=0.75,
            confidence=0.90,
            content_excerpt="Environmental liability",
            explanation="High risk environmental exposure",
            recommendation="Escalate to partner review"
        )
    ]
    
    routed = router.route_findings(findings, retrieval_score=0.8)
    
    if len(routed) != len(findings):
        print("✗ Routing count mismatch")
        return False
    
    print(f"✓ Routed {len(routed)} findings")
    for finding in routed:
        print(f"  - {finding.document_name}: {finding.confidence_level} → {finding.routing_action}")
    
    return True

def test_report_generation():
    """Test Layer 8: Report Generation"""
    print("\n" + "="*70)
    print("TEST 8: REPORT GENERATION - O&G Data")
    print("="*70)
    
    gen = ReportGenerator(data_source="demo_data/oil_gas")
    gen.generate_report("environmental liability")
    
    json_files = list(Path("output").glob("report_*.json"))
    html_files = list(Path("output").glob("report_*.html"))
    
    if not json_files or not html_files:
        print("✗ No reports generated")
        return False
    
    with open(json_files[-1]) as f:
        data = json.load(f)
    
    if 'findings' not in data:
        print("✗ Missing findings in report")
        return False
    
    print(f"✓ JSON report: {json_files[-1].name}")
    print(f"✓ HTML report: {html_files[-1].name}")
    print(f"✓ {len(data['findings'])} findings in report")
    
    return True

def test_end_to_end():
    """Full pipeline test"""
    print("\n" + "="*70)
    print("TEST E2E: END-TO-END O&G ANALYSIS")
    print("="*70)
    
    gen = ReportGenerator(data_source="demo_data/oil_gas")
    
    queries = [
        "environmental liability",
        "operational control",
        "indemnification caps"
    ]
    
    for query in queries:
        print(f"\n  Query: {query}")
        gen.generate_report(query)
    
    json_files = list(Path("output").glob("report_*.json"))
    print(f"\n✓ Generated {len(json_files)} reports")
    
    return len(json_files) > 0

def main():
    print("\n" + "="*70)
    print("VERILENCE - OIL & GAS TEST SUITE")
    print("Real SEC Filing Analysis")
    print("="*70)
    
    tests = [
        ("Ingestion", test_ingestion),
        ("Embedding", test_embedding),
        ("RAG Retrieval", test_rag_retrieval),
        ("EBM Scoring", test_ebm_scoring),
        ("Confidence Routing", test_confidence_routing),
        ("Report Generation", test_report_generation),
        ("End-to-End", test_end_to_end),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"✗ {name} failed: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - O&G Analysis Ready!")
    else:
        print(f"\n⚠️  {total - passed} tests failed")

if __name__ == "__main__":
    main()

