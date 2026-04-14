#!/usr/bin/env python3
"""Replace dummy features with rule-based extraction"""
import json
import re

def extract_features(text):
    """Extract real features from text"""
    text_lower = text.lower()
    
    financial = 1.0 if any(w in text_lower for w in ['price', 'cost', 'fee', 'payment', 'royalty', '$']) else 0.2
    conflict = 1.0 if any(w in text_lower for w in ['prohibit', 'shall not', 'cannot', 'exclude']) else 0.2
    ambiguity = 1.0 if any(w in text_lower for w in ['may', 'might', 'could', 'should', 'reasonable']) else 0.2
    party = 1.0 if any(w in text_lower for w in ['operator', 'lessee', 'lessor', 'party', 'working interest']) else 0.2
    enforce = 1.0 if any(w in text_lower for w in ['covenant', 'obligation', 'liable', 'breach', 'default']) else 0.2
    
    return [financial, conflict, ambiguity, party, enforce]

# Load merged data
with open('ebm_training_data_merged.json') as f:
    data = json.load(f)

print(f"Updating {len(data['X'])} samples with real features...")

# We need to go back to source and extract features properly
# For now, use the acord texts we have
with open('ebm_training_data_acord.json') as f:
    acord = json.load(f)

# Extract features from acord clauses
print("Extracting features from ACORD...")
for i, item in enumerate(acord):
    acord[i]['features'] = extract_features(item['clause_text'])

# Save updated
with open('ebm_training_data_acord_updated.json', 'w') as f:
    json.dump(acord, f)

print("Saved updated ACORD with real features")
