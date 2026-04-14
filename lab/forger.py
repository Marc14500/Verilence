import json
import google.generativeai as genai
from config import GEMINI_API_KEY

class GeminiForger:
    """Generates clause variants for training."""
    
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-pro")
    
    def generate(self, clause_text, clause_id=None):
        """Generate 5 clause variants."""
        
        # Truncate clause to first 300 chars to avoid token overflow
        clause_summary = clause_text[:300] + ("..." if len(clause_text) > 300 else "")
        
        prompt = f"""Rewrite this contract clause 5 ways with same meaning:

{clause_summary}

Output 5 JSON objects, one per line:
{{"variant_id": "v1", "modified_clause": "rewrite 1", "concept_type": "phrasing"}}
{{"variant_id": "v2", "modified_clause": "rewrite 2", "concept_type": "phrasing"}}
{{"variant_id": "v3", "modified_clause": "rewrite 3", "concept_type": "structure"}}
{{"variant_id": "v4", "modified_clause": "rewrite 4", "concept_type": "emphasis"}}
{{"variant_id": "v5", "modified_clause": "rewrite 5", "concept_type": "order"}}

ONLY JSON. No text."""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 1200,  # Increased
                }
            )
            
            finish_reason = response.candidates[0].finish_reason.name
            
            if finish_reason != 'STOP':
                print(f"    ℹ Finish reason: {finish_reason}")
                return []
            
            if not response.text:
                return []
            
            variants = []
            for line in response.text.strip().split('\n'):
                line = line.strip()
                if line and line.startswith('{'):
                    try:
                        variant = json.loads(line)
                        variant["contradiction_type"] = variant.get("concept_type", "phrasing")
                        variant["sneakiness_score"] = 0.5
                        variant["original_clause"] = clause_text
                        variant["original_clause_id"] = clause_id
                        variants.append(variant)
                    except:
                        pass
            
            if variants:
                print(f"    ✓ Generated {len(variants)} variants")
            else:
                print(f"    ✗ No valid JSON in response")
            return variants
        
        except Exception as e:
            print(f"    ✗ Error: {str(e)[:80]}")
            return []

if __name__ == "__main__":
    forger = GeminiForger(GEMINI_API_KEY)
    test = "The Operator shall be responsible for all costs."
    variants = forger.generate(test, clause_id="test")
    print(json.dumps(variants, indent=2))
