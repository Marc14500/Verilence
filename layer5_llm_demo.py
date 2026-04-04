#!/usr/bin/env python3
"""Layer 5 Demo Mode - Real Findings from Manual Analysis"""

import json

class DiscoveryAgentDemo:
    def __init__(self):
        print("\n[L5] DISCOVERY AGENT (DEMO MODE)")
        # Load pre-analyzed findings
        with open("manual_findings.json") as f:
            self.findings_db = json.load(f)
        print(f"[L5] Loaded {len(self.findings_db['findings'])} pre-analyzed findings")
    
    def get_findings(self):
        """Return real findings from manual analysis"""
        findings = []
        for f in self.findings_db['findings']:
            finding = type('Finding', (), {
                'finding_id': f['finding_id'],
                'document_name': self.findings_db['document'],
                'title': f['title'],
                'explanation': f['explanation'],
                'risk_score': f['risk_score'],
                'risk_level': f['risk_level'],
                'confidence': f['confidence'],
                'confidence_score': f['confidence'],
                'confidence_level': 'HIGH' if f['confidence'] > 0.8 else 'MEDIUM' if f['confidence'] > 0.6 else 'LOW',
                'routing_action': 'ANALYST_REVIEW' if f['risk_level'] == 'MEDIUM' else 'SENIOR_PARTNER_ESCALATION',
                'quote_a': f['quote_a'],
                'quote_b': f['quote_b'],
                'sections': f['sections'],
                'consequences': f['consequences'],
                'document_quote': f.get('document_quote', '')
            })
            findings.append(finding)
        
        print(f"[L5] Returning {len(findings)} real findings")
        return findings

