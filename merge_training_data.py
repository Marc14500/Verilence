#!/usr/bin/env python3
"""Merge ACORD and LEDGAR training data"""
import json
import numpy as np

# Load existing LEDGAR data
with open('/home/greavesgm/verilence/ebm_training_data.json') as f:
    ledgar = json.load(f)

# Load ACORD data
with open('/home/greavesgm/verilence/ebm_training_data_acord.json') as f:
    acord = json.load(f)

print(f"LEDGAR: {len(ledgar['X'])} samples")
print(f"ACORD: {len(acord)} samples")

# Convert ACORD to match LEDGAR format
acord_X = [[0.5, 0.5, 0.5, 0.5, 0.5] for item in acord]  # Dummy features
acord_y = [item['risk_score'] for item in acord]

# Merge
merged_X = ledgar['X'] + acord_X
merged_y = ledgar['y'] + acord_y

merged = {
    'X': merged_X,
    'y': merged_y,
    'n_samples': len(merged_X),
    'feature_names': ledgar.get('feature_names', ['financial', 'conflict', 'ambiguity', 'party_exposure', 'enforceability'])
}

print(f"Merged: {len(merged_X)} total samples")

# Save merged
with open('/home/greavesgm/verilence/ebm_training_data_merged.json', 'w') as f:
    json.dump(merged, f)

print("Saved to ebm_training_data_merged.json")
