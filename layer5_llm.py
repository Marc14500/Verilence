#!/usr/bin/env python3
"""Layer 5: LLM Synthesis - Gemini synthesizes conflicts from EBM-selected sections only"""

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

    def analyze_full_document(self, ebm_selected_text, filename):
        """
        Gemini's ONLY job here is synthesis.
        EBM has already identified the high-risk sections.
        Gemini explains conflicts between those sections in plain language.
        Gemini does NOT detect, hunt for, or invent issues.
        """
        print(f"[L5-ANALYZE] Synthesizing conflicts from EBM-selected sections...")

        prompt = f"""You are a legal contract analyst. The sections below have been pre-selected by a risk scoring engine as the highest-risk clauses in a legal document. This may be any type of legal document — a Joint Operating Agreement, Purchase and Sale Agreement, Statement of Work, employment contract, partnership agreement, or any other complex legal document.

YOUR ONLY JOB is to identify where these specific sections explicitly conflict with each other and explain each conflict clearly. You are a writer and explainer, not a detector.

STRICT RULES:
- Only report conflicts that are explicitly and unambiguously present in the text below
- Do NOT invent, speculate, or infer issues beyond what the text directly states
- Do NOT report a finding unless you can cite two specific sections that directly contradict each other
- Do NOT editorialize or use dramatic language — be factual and precise
- Be conservative — if you are uncertain whether a conflict is real, do not report it
- Financial impact should be specific and grounded in the text, not speculative
- If no genuine conflicts exist between the provided sections, return an empty array

PRE-SELECTED HIGH-RISK SECTIONS:

{ebm_selected_text[:50000]}

For each genuine conflict you can explicitly identify, return a JSON object:
{{
    "found": true,
    "title": "Brief descriptive title (max 10 words)",
    "section_1": "Section X.X reference: exact quote from first conflicting section",
    "section_2": "Section Y.Y reference: exact quote from second conflicting section",
    "problem": "Plain factual explanation of why these sections conflict. Two to three sentences maximum. No speculation.",
    "financial_impact": "Specific dollar amount if calculable from the text, otherwise: Requires legal assessment",
    "confidence": 0.0,
    "risk_level": "HIGH or MEDIUM or LOW"
}}

Return a JSON array only. No preamble, no explanation, no markdown. If no genuine conflicts exist, return: []
"""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text

            # Extract JSON array
            json_match = re.search(r'\[[\s\S]*\]', response_text)
            if not json_match:
                print("[L5] No conflicts identified in EBM-selected sections")
                return []

            findings_data = json.loads(json_match.group())

            if not findings_data:
                print("[L5] Gemini confirmed no genuine conflicts in selected sections")
                return []

            # Convert to Finding objects
            findings = []
            for i, f in enumerate(findings_data):
                if f.get('found', False):
                    finding = type('Finding', (), {
                        'finding_id': f'finding_{i}',
                        'document_name': filename,
                        'title': f.get('title', 'Conflict'),
                        'risk_score': 0.7 if f.get('risk_level') == 'HIGH' else 0.5 if f.get('risk_level') == 'MEDIUM' else 0.3,
                        'risk_level': f.get('risk_level', 'MEDIUM'),
                        'confidence': f.get('confidence', 0.75),
                        'confidence_score': f.get('confidence', 0.75),
                        'confidence_level': 'HIGH' if f.get('confidence', 0.75) > 0.8 else 'MEDIUM' if f.get('confidence', 0.75) > 0.6 else 'LOW',
                        'explanation': f"{f.get('section_1', '')}\n\nvs\n\n{f.get('section_2', '')}\n\nConflict: {f.get('problem', '')}",
                        'section_1': f.get('section_1', ''),
                        'section_2': f.get('section_2', ''),
                        'why_problem': f.get('problem', ''),
                        'financial_impact': f.get('financial_impact', 'Requires legal assessment'),
                        'recommendation': f"Review conflict between sections cited above with qualified legal counsel",
                        'routing_action': 'SENIOR_PARTNER_ESCALATION',
                        'requires_human_review': True
                    })()
                    findings.append(finding)

            print(f"[L5] ✓ Gemini synthesized {len(findings)} genuine conflicts from EBM-selected sections")
            return findings

        except Exception as e:
            print(f"[L5] Error: {e}")
            import traceback
            traceback.print_exc()
            return []
