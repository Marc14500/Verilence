#!/usr/bin/env python3
"""Layer 5: Gemini Synthesis - Explains EBM-discovered contradictions"""
import google.generativeai as genai
import os
import json
import re

class DiscoveryAgent:
    def __init__(self):
        print("\n[L5] DISCOVERY AGENT (GEMINI)")
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        print("[L5] ✓ Gemini connected")

    def analyze_full_document(self, text_a, text_b, section_a="Section A", section_b="Section B"):
        """Single explanation with confidence score and title"""
        print(f"[L5-SYNTHESIZE] Analyzing {section_a} vs {section_b}...")
        
        prompt = f"""Analyze the contradiction between these sections. Respond ONLY with valid JSON (no markdown, no code blocks):

{section_a}:
{text_a[:400]}

{section_b}:
{text_b[:400]}

{{"title": "Short issue title (5-8 words)", "explanation": "1-2 sentence explanation", "confidence": 50}}"""

        try:
            response = self.model.generate_content(prompt, request_options={"timeout": 30})
            if response and response.text:
                text = response.text.strip()
                
                # Remove markdown code blocks if present
                text = re.sub(r'```json\s*|\s*```', '', text)
                text = re.sub(r'```\s*|\s*```', '', text)
                
                try:
                    result = json.loads(text)
                    title = result.get('title', f'{section_a} vs {section_b}')
                    explanation = result.get('explanation', '')
                    confidence = int(result.get('confidence', 50))
                    return title, explanation, confidence
                except json.JSONDecodeError:
                    return f'{section_a} vs {section_b}', text, 50
            return f'{section_a} vs {section_b}', None, 0
        except Exception as e:
            print(f"[L5-SYNTHESIZE] Error: {e}")
            return f'{section_a} vs {section_b}', None, 0
