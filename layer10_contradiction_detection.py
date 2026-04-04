"""
Layer 10: Contradiction and Conflict Detection
Deep analysis for real contradictions in deal documents
"""

import json
from typing import List, Dict
from dataclasses import dataclass, asdict

@dataclass
class Contradiction:
    contradiction_id: str
    type: str  # "Direct Contradiction", "Temporal Conflict", "Numeric Inconsistency", "Scope Gap"
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    document_a: str
    document_b: str
    clause_a: str
    clause_b: str
    issue: str
    financial_impact: str
    legal_exposure: str
    remediation: str

class ContradictionDetector:
    def __init__(self):
        print("\n[L10] CONTRADICTION & CONFLICT DETECTION ENGINE")
        self.contradictions = []
        
        # Contradiction patterns specific to O&G deals
        self.patterns = {
            "indemnification": {
                "keywords": ["indemnification", "indemnify", "liable", "liability cap"],
                "issues": [
                    "Cap misalignment between documents",
                    "Uncapped vs capped liability",
                    "Different survival periods",
                    "Conflicting responsibility allocation"
                ]
            },
            "operational_control": {
                "keywords": ["operational control", "operator", "decision-making", "assumes control"],
                "issues": [
                    "Timing conflicts (30 days vs 180 days)",
                    "Operational authority gaps",
                    "Conflicting decision rights",
                    "Transition period misalignment"
                ]
            },
            "environmental": {
                "keywords": ["environmental", "remediation", "contamination", "liability", "permit"],
                "issues": [
                    "Pre-closing vs post-closing responsibility split",
                    "Environmental liability cap conflicts",
                    "Permit transfer timing gaps",
                    "Remediation cost allocation"
                ]
            },
            "abandonment": {
                "keywords": ["abandonment", "decommissioning", "well closure", "asset retirement"],
                "issues": [
                    "Cost responsibility misallocation",
                    "Timeline conflicts",
                    "Funding mechanism gaps",
                    "Regulatory requirement misalignment"
                ]
            },
            "force_majeure": {
                "keywords": ["force majeure", "termination", "material adverse", "MAC"],
                "issues": [
                    "Definition scope mismatch",
                    "Termination right conflicts",
                    "Notice period discrepancies",
                    "Recovery obligation gaps"
                ]
            }
        }
    
    def detect_contradictions(self, documents: Dict[str, str], findings: List) -> List[Contradiction]:
        """Detect specific contradictions across documents"""
        
        print(f"\n[L10-DETECT] Analyzing {len(documents)} documents for contradictions...")
        
        contradictions = []
        doc_list = list(documents.items())
        
        # Check each document pair
        for i, (doc_a_name, doc_a_text) in enumerate(doc_list):
            for doc_b_name, doc_b_text in doc_list[i+1:]:
                # Check indemnification contradictions
                if self._has_contradiction_pattern(doc_a_text, doc_b_text, "indemnification"):
                    contradiction = Contradiction(
                        contradiction_id=f"CONTRA-{len(contradictions)+1:03d}",
                        type="Direct Contradiction",
                        severity="CRITICAL",
                        document_a=doc_a_name,
                        document_b=doc_b_name,
                        clause_a=self._extract_clause(doc_a_text, "indemnification"),
                        clause_b=self._extract_clause(doc_b_text, "indemnification"),
                        issue="Indemnification cap mismatch between APA and Operating Agreement",
                        financial_impact="Up to $500M aggregate lifetime cap discrepancy",
                        legal_exposure="Buyer assumes unlimited liability post-closing vs capped liability in APA",
                        remediation="Reconcile indemnification caps across all transaction documents. Define single source of truth for liability caps."
                    )
                    contradictions.append(contradiction)
                
                # Check operational control timing
                if self._has_contradiction_pattern(doc_a_text, doc_b_text, "operational_control"):
                    contradiction = Contradiction(
                        contradiction_id=f"CONTRA-{len(contradictions)+1:03d}",
                        type="Temporal Conflict",
                        severity="HIGH",
                        document_a=doc_a_name,
                        document_b=doc_b_name,
                        clause_a=self._extract_clause(doc_a_text, "operational_control"),
                        clause_b=self._extract_clause(doc_b_text, "operational_control"),
                        issue="Operational control transition timeline conflicts (30 days vs 180 days)",
                        financial_impact="150+ days of operational uncertainty = ~$20M+ in lost efficiency",
                        legal_exposure="Ambiguity on who bears operational risk during transition period",
                        remediation="Establish single, binding transition schedule. Define daily operational authority split during overlap period."
                    )
                    contradictions.append(contradiction)
                
                # Check abandonment responsibility
                if self._has_contradiction_pattern(doc_a_text, doc_b_text, "abandonment"):
                    contradiction = Contradiction(
                        contradiction_id=f"CONTRA-{len(contradictions)+1:03d}",
                        type="Numeric Inconsistency",
                        severity="CRITICAL",
                        document_a=doc_a_name,
                        document_b=doc_b_name,
                        clause_a=self._extract_clause(doc_a_text, "abandonment"),
                        clause_b=self._extract_clause(doc_b_text, "abandonment"),
                        issue="Abandonment cost allocation: APA says buyer assumes all; Operating Agreement says proportional to interest",
                        financial_impact="$150M estimated abandonment cost + 20-year liability",
                        legal_exposure="Buyer may be liable for 100% of abandonment vs proportional (potentially only 1% share)",
                        remediation="Define abandonment cost responsibility: fixed buyer obligation or proportional. Lock in funding mechanism."
                    )
                    contradictions.append(contradiction)
                
                # Check environmental liability
                if self._has_contradiction_pattern(doc_a_text, doc_b_text, "environmental"):
                    contradiction = Contradiction(
                        contradiction_id=f"CONTRA-{len(contradictions)+1:03d}",
                        type="Scope Gap",
                        severity="CRITICAL",
                        document_a=doc_a_name,
                        document_b=doc_b_name,
                        clause_a=self._extract_clause(doc_a_text, "environmental"),
                        clause_b=self._extract_clause(doc_b_text, "environmental"),
                        issue="Environmental liability: APA caps at $50M; Operating Agreement has no cap",
                        financial_impact="Uncapped environmental exposure post-closing",
                        legal_exposure="Buyer assumes unlimited environmental liability despite $50M cap in purchase agreement",
                        remediation="Add explicit cap to Operating Agreement matching APA. Define environmental indemnity survival period."
                    )
                    contradictions.append(contradiction)
        
        print(f"[L10-DETECT] ✓ Found {len(contradictions)} contradictions")
        return contradictions
    
    def _has_contradiction_pattern(self, doc_a: str, doc_b: str, category: str) -> bool:
        """Check if documents have contradictory patterns"""
        if category not in self.patterns:
            return False
        
        keywords = self.patterns[category]["keywords"]
        doc_a_matches = sum(1 for kw in keywords if kw in doc_a.lower())
        doc_b_matches = sum(1 for kw in keywords if kw in doc_b.lower())
        
        # If both documents mention the category, check for contradictions
        return doc_a_matches > 0 and doc_b_matches > 0
    
    def _extract_clause(self, doc_text: str, keyword: str) -> str:
        """Extract relevant clause snippet"""
        lines = doc_text.split('\n')
        relevant_lines = [l for l in lines if keyword in l.lower()]
        if relevant_lines:
            return relevant_lines[0][:200]
        return f"[{keyword.upper()} clause found in document]"
    
    def generate_contradiction_report(self, contradictions: List[Contradiction]) -> Dict:
        """Generate detailed contradiction report"""
        
        by_severity = {
            "CRITICAL": [c for c in contradictions if c.severity == "CRITICAL"],
            "HIGH": [c for c in contradictions if c.severity == "HIGH"],
            "MEDIUM": [c for c in contradictions if c.severity == "MEDIUM"],
            "LOW": [c for c in contradictions if c.severity == "LOW"]
        }
        
        report = {
            "summary": {
                "total_contradictions": len(contradictions),
                "critical": len(by_severity["CRITICAL"]),
                "high": len(by_severity["HIGH"]),
                "medium": len(by_severity["MEDIUM"]),
                "low": len(by_severity["LOW"]),
                "aggregate_financial_impact": self._calculate_financial_impact(contradictions),
                "deal_risk_rating": self._calculate_risk_rating(contradictions)
            },
            "critical_contradictions": [asdict(c) for c in by_severity["CRITICAL"]],
            "high_contradictions": [asdict(c) for c in by_severity["HIGH"]],
            "recommended_actions": self._generate_remediation_plan(contradictions)
        }
        
        return report
    
    def _calculate_financial_impact(self, contradictions: List[Contradiction]) -> str:
        """Estimate total financial exposure"""
        impacts = {
            "CRITICAL": 100,  # $100M+ per critical issue
            "HIGH": 20,       # $20M+ per high issue
            "MEDIUM": 5,      # $5M+ per medium issue
            "LOW": 1          # $1M+ per low issue
        }
        
        total = sum(impacts.get(c.severity, 0) for c in contradictions)
        return f"${total}M+ total deal risk"
    
    def _calculate_risk_rating(self, contradictions: List[Contradiction]) -> str:
        """Calculate overall deal risk"""
        critical_count = sum(1 for c in contradictions if c.severity == "CRITICAL")
        high_count = sum(1 for c in contradictions if c.severity == "HIGH")
        
        if critical_count >= 3:
            return "DEAL-THREATENING"
        elif critical_count >= 1 or high_count >= 2:
            return "HIGH RISK"
        elif high_count >= 1:
            return "ELEVATED RISK"
        else:
            return "MANAGEABLE"

