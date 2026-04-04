#!/usr/bin/env python3
"""Layer 5: LLM Synthesis - Free-form contradiction detection on entire document"""

import google.generativeai as genai
import json
import re

class DiscoveryAgent:
    def __init__(self):
        print("\n[L5] DISCOVERY AGENT (GEMINI)")
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        try:
            self.model.generate_content("test")
            print("[L5] ✓ Gemini connected")
        except Exception as e:
            print(f"[L5] ⚠ Gemini error: {e}")
    
    def analyze_full_document(self, full_text, filename):
        """Analyze entire document for ANY contradictions - no constraints"""
        print(f"[L5-ANALYZE] Full document analysis (unconstrained)...")
        
        # Prompt that asks Gemini to find ALL contradictions
        prompt = f"""You are a legal contract expert analyzing a Joint Operating Agreement (JOA) for contradictions, inconsistencies, and ambiguities.

DOCUMENT TEXT:
{full_text[:50000]}  # Limit to first 50k chars to avoid token limits

INSTRUCTIONS:
1. Find ALL contradictions, conflicts, ambiguities, and inconsistencies in this document
2. Include: conflicting definitions, contradictory provisions, ambiguous language, unresolved disputes
3. For each contradiction, provide:
   - Title/name of the contradiction
   - Exact section references and quotes from the document
   - Why it's a problem legally/financially
   - Estimated financial impact
   - Your confidence (0.0-1.0) that this is a real issue

Return as JSON array:
[
  {{
    "found": true,
    "title": "Contradiction title",
    "section_1": "Section X.X: exact quote",
    "section_2": "Section Y.Y: conflicting quote",
    "problem": "Why this matters",
    "financial_impact": "$X or description",
    "confidence": 0.85,
    "risk_level": "HIGH/MEDIUM/LOW"
  }},
  ...
]

If you find NO contradictions, return: []

Be thorough. A real JOA should have contradictions - if you're not finding any, look harder.
"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Extract JSON array
            json_match = re.search(r'\[[\s\S]*\]', response_text)
            if json_match:
                findings_data = json.loads(json_match.group())
            else:
                print("[L5] No JSON found in response")
                return []
            
            # Convert to Finding objects
            findings = []
            for i, f in enumerate(findings_data):
                if f.get('found', False):
                    finding = type('Finding', (), {
                        'finding_id': f'finding_{i}',
                        'document_name': filename,
                        'title': f.get('title', 'Contradiction'),
                        'risk_score': 0.7 if f.get('risk_level') == 'HIGH' else 0.5 if f.get('risk_level') == 'MEDIUM' else 0.3,
                        'risk_level': f.get('risk_level', 'MEDIUM'),
                        'confidence': f.get('confidence', 0.75),
                        'confidence_score': f.get('confidence', 0.75),
                        'confidence_level': 'HIGH' if f.get('confidence', 0.75) > 0.8 else 'MEDIUM' if f.get('confidence', 0.75) > 0.6 else 'LOW',
                        'explanation': f"{f.get('section_1', '')}\n\nvs\n\n{f.get('section_2', '')}\n\nProblem: {f.get('problem', '')}",
                        'section_1': f.get('section_1', ''),
                        'section_2': f.get('section_2', ''),
                        'why_problem': f.get('problem', ''),
                        'financial_impact': f.get('financial_impact', 'Unknown'),
                        'recommendation': f"Resolve contradiction between sections mentioned above",
                        'routing_action': 'SENIOR_PARTNER_ESCALATION',
                        'requires_human_review': True
                    })
                    findings.append(finding)
            
            print(f"[L5] ✓ Found {len(findings)} contradictions in full document")
            return findings
        
        except Exception as e:
            print(f"[L5] Error: {e}")
            import traceback
            traceback.print_exc()
            return []

