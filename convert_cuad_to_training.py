#!/usr/bin/env python3
"""Convert CUAD dataset to EBM training format"""
import json

cuad_path = "/home/greavesgm/verilence/cuad/CUADv1.json"

print("Loading CUAD...")
with open(cuad_path) as f:
    cuad_data = json.load(f)

print(f"Loaded {len(cuad_data['data'])} contracts")

# Extract clause pairs with relevance scores
training_pairs = []

for contract in cuad_data['data']:
    contract_text = contract.get('paragraphs', [{}])[0].get('context', '')
    
    for paragraph in contract.get('paragraphs', []):
        for qa in paragraph.get('qas', []):
            question = qa.get('question', '')
            answers = qa.get('answers', [])
            
            if answers:
                # Answers indicate relevant clauses
                for answer in answers:
                    answer_text = answer.get('text', '')
                    if answer_text and len(answer_text) > 50:
                        # Score based on answer presence (relevant = 1.0)
                        training_pairs.append({
                            'features': [0.5, 0.5, 0.5, 0.5, 0.5],
                            'risk_score': 0.75,  # Relevant clauses get higher score
                            'clause_text': answer_text[:300],
                            'question': question
                        })
            else:
                # No answers = not relevant
                if len(contract_text) > 50:
                    training_pairs.append({
                        'features': [0.5, 0.5, 0.5, 0.5, 0.5],
                        'risk_score': 0.25,
                        'clause_text': contract_text[:300],
                        'question': question
                    })

print(f"Created {len(training_pairs)} training pairs")

# Save
with open('/home/greavesgm/verilence/ebm_training_data_cuad.json', 'w') as f:
    json.dump(training_pairs, f)
print("Saved to ebm_training_data_cuad.json")
