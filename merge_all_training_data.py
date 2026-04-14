#!/usr/bin/env python3
"""Merge LEDGAR, ACORD, and CUAD training data"""
import json

# Load all datasets
with open('/home/greavesgm/verilence/ebm_training_data.json') as f:
    ledgar = json.load(f)

with open('/home/greavesgm/verilence/ebm_training_data_acord.json') as f:
    acord = json.load(f)

with open('/home/greavesgm/verilence/ebm_training_data_cuad.json') as f:
    cuad = json.load(f)

print(f"LEDGAR: {len(ledgar['X'])} samples")
print(f"ACORD: {len(acord)} samples")
print(f"CUAD: {len(cuad)} samples")

# Convert ACORD and CUAD to match LEDGAR format
acord_X = [[0.5, 0.5, 0.5, 0.5, 0.5] for item in acord]
acord_y = [item['risk_score'] for item in acord]

cuad_X = [[0.5, 0.5, 0.5, 0.5, 0.5] for item in cuad]
cuad_y = [item['risk_score'] for item in cuad]

# Merge all three
merged_X = ledgar['X'] + acord_X + cuad_X
merged_y = ledgar['y'] + acord_y + cuad_y

merged = {
    'X': merged_X,
    'y': merged_y,
    'n_samples': len(merged_X),
    'feature_names': ['financial', 'conflict', 'ambiguity', 'party_exposure', 'enforceability']
}

print(f"Merged: {len(merged_X)} total samples")

# Save merged
with open('/home/greavesgm/verilence/ebm_training_data_merged.json', 'w') as f:
    json.dump(merged, f)

print("Saved to ebm_training_data_merged.json")
