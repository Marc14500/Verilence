import json
from pathlib import Path
from datetime import datetime
from layer1_ingestion import IngestionEngine
from layer3_rag_qdrant import RAGEngineQdrant
from layer4_ebm import GlassBoxJudge
from layer5_llm import DiscoveryAgent
from layer6_confidence_routing import ConfidenceRouter
from layer9_audit_reporting import AuditReportGenerator

class ReportGenerator:
    def __init__(self, data_source="data"):
        print(f"\n[L8] REPORT GENERATOR (source: {data_source})")
        self.data_source = data_source
        self.rag = None
        self.judge = GlassBoxJudge()
        self.agent = DiscoveryAgent()
        self.router = ConfidenceRouter()
        self.auditor = AuditReportGenerator()
        self._load_data()
    
    def _load_data(self):
        ingester = IngestionEngine()
        ingester.ingest_documents([self.data_source])
        ingester.chunk_documents()
        ingester.save_state("output")
        self.rag = RAGEngineQdrant()
        self.rag.load_and_index()
    
    def generate_report(self, query: str, output_dir: str = "output"):
        print(f"\n[REPORT] Analyzing: {query}")
        
        retrieval_result = self.rag.retrieve(query, top_k=3)
        if not retrieval_result.citations:
            print("[REPORT] No results")
            return
        
        risk_scores = self.judge.score_citations(retrieval_result.citations)
        findings = self.agent.synthesize_findings(risk_scores)
        routed_findings = self.router.route_findings(findings, retrieval_score=retrieval_result.retrieval_score)
        briefing = self.router.generate_briefing(routed_findings)
        
        self.auditor.generate_audit_report(query, routed_findings, briefing, retrieval_result, routed_findings, output_dir)

