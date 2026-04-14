#!/usr/bin/env python3
"""Layer 4: Glass Box Judge (EBM) - Finds contradictions via pairwise comparison"""
import json
import numpy as np
from scipy.spatial.distance import cosine
from interpret.glassbox import ExplainableBoostingRegressor

class GlassBoxJudge:
    def __init__(self):
        print("\n[L4] GLASS BOX JUDGE (EBM)")
        print("[L4] Loading LEDGAR training data...")
        
        with open('ebm_training_data_merged.json', 'r') as f:
            data = json.load(f)
        
        # Data format: {"X": [[...], ...], "y": [...]}
        X = np.array(data['X'])
        y = np.array(data['y'])
        
        self.ebm = ExplainableBoostingRegressor(random_state=42, max_rounds=100)
        self.ebm.fit(X, y)
        
        print(f"[L4] ✓ Loaded {len(y)} real contract clause samples")
        print(f"[L4] ✓ EBM trained — risk range: {min(y):.2f}–{max(y):.2f}")

    def extract_features(self, text_a, text_b):
        """Extract 5 features from chunk pair"""
        combined = (text_a + " " + text_b).lower()
        
        financial_keywords = ['price', 'cost', 'fee', 'payment', 'royalty', 'revenue', 'million', '$']
        financial_score = sum(1 for kw in financial_keywords if kw in combined) / len(financial_keywords)
        
        conflict_keywords = ['prohibit', 'shall not', 'cannot', 'exclude', 'except', 'provided']
        conflict_score = sum(1 for kw in conflict_keywords if kw in combined) / len(conflict_keywords)
        
        ambiguity_keywords = ['may', 'might', 'could', 'should', 'reasonable', 'appropriate']
        ambiguity_score = sum(1 for kw in ambiguity_keywords if kw in combined) / len(ambiguity_keywords)
        
        party_keywords = ['operator', 'non-operator', 'working interest owner', 'lessee', 'lessor']
        party_score = sum(1 for kw in party_keywords if kw in combined) / len(party_keywords)
        
        enforce_keywords = ['covenant', 'obligation', 'liable', 'breach', 'default', 'indemnify']
        enforce_score = sum(1 for kw in enforce_keywords if kw in combined) / len(enforce_keywords)
        
        return [financial_score, conflict_score, ambiguity_score, party_score, enforce_score]

    def find_potential_issues(self, embedded_chunks):
        """Compare all chunk pairs to find potential issues"""
        issues = []
        
        print(f"\n[L4-DISCOVERY] Comparing {len(embedded_chunks)} chunks for potential issues...")
        
        for i in range(len(embedded_chunks)):
            for j in range(i+1, len(embedded_chunks)):
                chunk_a = embedded_chunks[i]
                chunk_b = embedded_chunks[j]
                
                text_a = chunk_a['text']
                text_b = chunk_b['text']
                emb_a = np.array(chunk_a['embedding'])
                emb_b = np.array(chunk_b['embedding'])
                
                # Calculate semantic similarity
                sim = 1 - cosine(emb_a, emb_b)
                
                # Extract features from both chunks
                features = self.extract_features(text_a, text_b)
                X = np.array([features])
                risk_score = float(self.ebm.predict(X)[0])
                risk_score = max(0.15, min(0.90, risk_score))
                
                # Flag if: high similarity (same topic) + high risk (potential conflict)
                if sim > 0.6 and risk_score > 0.45:
                    issues.append({
                        'chunk_a_id': chunk_a['id'],
                        'chunk_b_id': chunk_b['id'],
                        'section_a': chunk_a['metadata'].get('section', 'Unknown'),
                        'section_b': chunk_b['metadata'].get('section', 'Unknown'),
                        'text_a': text_a[:300],
                        'text_b': text_b[:300],
                        'semantic_similarity': round(sim, 3),
                        'ebm_risk_score': round(risk_score, 2),
                        'features': dict(zip(['financial', 'conflict', 'ambiguity', 'party_exposure', 'enforceability'], features))
                    })
        
        # Sort by risk score descending
        issues.sort(key=lambda x: x['ebm_risk_score'], reverse=True)
        print(f"[L4-DISCOVERY] ✓ Found {len(issues)} potential issues")
        
        return issues
