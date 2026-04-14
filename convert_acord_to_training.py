#!/usr/bin/env python3
"""Convert ACORD dataset to EBM training format"""
import json

acord_dir = "/home/greavesgm/verilence/acord/ACORD Dataset & ReadMe (external)"

# Load corpus
print("Loading corpus...")
corpus = {}
with open(f"{acord_dir}/corpus.jsonl") as f:
    for line in f:
        doc = json.loads(line)
        corpus[doc['_id']] = doc['text']

print(f"Loaded {len(corpus)} clauses")

# Load qrels (relevance ratings)
print("Loading qrels...")
training_pairs = []
with open(f"{acord_dir}/qrels/train.tsv") as f:
    for i, line in enumerate(f):
        if i == 0: continue  # Skip header
        parts = line.strip().split('\t')
        if len(parts) >= 3:
            query_id, corpus_id, score = parts[0], parts[1], int(parts[2])
            
            if corpus_id in corpus:
                # Score 0-4 maps to risk_score
                risk_score = score / 4.0  # Normalize to 0-1
                
                training_pairs.append({
                    'features': [0.5, 0.5, 0.5, 0.5, 0.5],
                    'risk_score': risk_score,
                    'clause_text': corpus[corpus_id][:300],
                    'query': query_id
                })

print(f"Created {len(training_pairs)} training pairs")

# Save as EBM training data
with open('/home/greavesgm/verilence/ebm_training_data_acord.json', 'w') as f:
    json.dump(training_pairs, f, indent=2)
print("Saved to ebm_training_data_acord.json")
