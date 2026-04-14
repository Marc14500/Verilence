import json
import google.generativeai as genai
from config import GEMINI_API_KEY

class GeminiCritic:
    """Scores clause variants."""
    
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-pro")
    
    def evaluate(self, original_clause, variants):
        """Score variants."""
        
        variants_text = "\n".join([f"{v['variant_id']}: {v.get('modified_clause', '')[:200]}" for v in variants])
        
        prompt = f"""Rate each variant on whether it preserves the meaning of the original.

Original: {original_clause[:300]}

Variants:
{variants_text}

Output 5 JSON objects. Each has: variant_id, is_valid (true/false), reasoning (brief).

Example:
{{"variant_id": "v1", "is_valid": true, "reasoning": "Good alternative phrasing"}}
{{"variant_id": "v2", "is_valid": false, "reasoning": "Changed meaning too much"}}

Output ONLY JSON."""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 600,
                }
            )
            
            if response.candidates[0].finish_reason.name != 'STOP':
                return []
            
            if not response.text:
                return []
            
            verdicts = []
            for line in response.text.strip().split('\n'):
                line = line.strip()
                if line and line.startswith('{'):
                    try:
                        v = json.loads(line)
                        verdicts.append({
                            "variant_id": v.get("variant_id"),
                            "verdict": "ACCEPT" if v.get("is_valid") else "REJECT",
                            "reasoning": v.get("reasoning", ""),
                            "is_real_contradiction": v.get("is_valid", False)
                        })
                    except:
                        pass
            
            if verdicts:
                accepted = len([v for v in verdicts if v["verdict"] == "ACCEPT"])
                print(f"    ✓ Scored {len(verdicts)} variants. Valid: {accepted}")
            return verdicts
        
        except Exception as e:
            print(f"    ✗ Error: {str(e)[:100]}")
            return []

if __name__ == "__main__":
    critic = GeminiCritic(GEMINI_API_KEY)
    original = "The Operator shall be responsible for all costs."
    variants = [
        {"variant_id": "v1", "modified_clause": "The Operator is responsible for all costs."},
        {"variant_id": "v2", "modified_clause": "All costs are the Operator's responsibility."},
    ]
    verdicts = critic.evaluate(original, variants)
    print(json.dumps(verdicts, indent=2))
