#!/usr/bin/env python3
"""Convert NebulaSense and GainEnergy datasets to EBM training format"""
import json
from datasets import load_dataset

print("Loading datasets...")
legal_clauses = load_dataset("NebulaSense/Legal_Clause_Instructions")
og_data = load_dataset("GainEnergy/oilandgas-engineering-dataset")

training_pairs = []

# Process NebulaSense Legal Clauses
print("Processing NebulaSense...")
for sample in legal_clauses['train']:
    input_text = sample.get('Input')
    output_text = sample.get('Output')
    
    if input_text and output_text and len(str(input_text)) > 50:
        training_pairs.append({
            'features': [0.5, 0.5, 0.5, 0.5, 0.5],
            'risk_score': 0.6,
            'clause_text': str(input_text)[:300],
            'output': str(output_text)[:300],
            'instruction_type': sample.get('Instruction_Type', '')
        })

print(f"  ✓ Extracted {len(training_pairs)} from NebulaSense")

# Process GainEnergy O&G data
print("Processing GainEnergy O&G...")
nebula_count = len(training_pairs)
for sample in og_data['train']:
    text = sample.get('text') or sample.get('content')
    
    if text and len(str(text)) > 50:
        training_pairs.append({
            'features': [0.5, 0.5, 0.5, 0.5, 0.5],
            'risk_score': 0.65,
            'clause_text': str(text)[:300]
        })

print(f"  ✓ Extracted {len(training_pairs) - nebula_count} from GainEnergy")
print(f"\nTotal created: {len(training_pairs)} training pairs")

# Save
with open('/home/greavesgm/verilence/ebm_training_data_nebulasense_gainenergy.json', 'w') as f:
    json.dump(training_pairs, f)
print("Saved to ebm_training_data_nebulasense_gainenergy.json")
