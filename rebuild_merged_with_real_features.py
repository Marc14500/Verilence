#!/usr/bin/env python3
"""Rebuild merged dataset with real features"""
import json

# Load all with real features
with open('ebm_training_data.json') as f:
    ledgar = json.load(f)

with open('ebm_training_data_acord_updated.json') as f:
    acord = json.load(f)

# Convert to LEDGAR format
acord_X = [item['features'] for item in acord]
acord_y = [item['risk_score'] for item in acord]

# Merge
merged_X = ledgar['X'] + acord_X
merged_y = ledgar['y'] + acord_y

merged = {
    'X': merged_X,
    'y': merged_y,
    'n_samples': len(merged_X),
    'feature_names': ['financial', 'conflict', 'ambiguity', 'party_exposure', 'enforceability']
}

print(f"Rebuilt merged with {len(merged_X)} samples (real features)")

with open('ebm_training_data_merged.json', 'w') as f:
    json.dump(merged, f)

print("Saved")
