#!/usr/bin/env python3
"""Layer 4: Glass Box Judge - EBM Risk Scoring trained on LEDGAR real contract data"""
from interpret.glassbox import ExplainableBoostingRegressor
import numpy as np
import json
import os

class GlassBoxJudge:
    def __init__(self):
        print("\n[L4] GLASS BOX JUDGE (EBM)")
        self.ebm = self._train()

    def _train(self):
        """Train EBM on real LEDGAR contract clause data"""
        data_path = os.path.join(os.path.dirname(__file__), 'ebm_training_data.json')
        
        if os.path.exists(data_path):
            print("[L4] Loading LEDGAR training data...")
            with open(data_path) as f:
                data = json.load(f)
            X = np.array(data['X'])
            y = np.array(data['y'])
            print(f"[L4] ✓ Loaded {len(X)} real contract clause samples")
        else:
            print("[L4] Warning: LEDGAR data not found, using fallback synthetic data")
            X = np.array([
                [0.9, 0.8, 0.2, 0.8, 0.8],
                [0.7, 0.7, 0.3, 0.7, 0.7],
                [0.5, 0.5, 0.5, 0.5, 0.5],
                [0.3, 0.3, 0.6, 0.3, 0.3],
                [0.1, 0.2, 0.8, 0.2, 0.1],
            ])
            y = np.array([0.85, 0.70, 0.50, 0.30, 0.15])

        ebm = ExplainableBoostingRegressor(max_bins=64, interactions=3)
        ebm.fit(X, y)
        print(f"[L4] ✓ EBM trained — risk range: {y.min():.2f}–{y.max():.2f}")
        return ebm

    def extract_features(self, finding):
        """Extract 5 risk features from a finding object"""
        title = str(getattr(finding, 'title', '')).lower()
        s1 = str(getattr(finding, 'section_1', ''))
        s2 = str(getattr(finding, 'section_2', ''))
        problem = str(getattr(finding, 'why_problem', getattr(finding, 'explanation', '')))
        financial_impact = str(getattr(finding, 'financial_impact', ''))
        combined = f"{title} {s1} {s2} {problem} {financial_impact}".lower()

        # Feature 1: Financial specificity
        fin_kw = ['payment', 'fee', 'cost', 'expense', 'revenue', 'compensation',
                  'salary', 'bonus', 'percent', '%', 'dollar', '$', 'capital',
                  'tax', 'withhold', 'royalt', 'profit', 'loss', 'interest',
                  'working interest', 'override', 'afe', 'operator fee']
        fin_score = min(1.0, sum(1 for k in fin_kw if k in combined) / 4.0)

        # Feature 2: Section conflict severity
        conflict_kw = ['notwithstanding', 'except', 'provided however', 'unless',
                       'in the event', 'shall not', 'may not', 'conflict', 'supersede',
                       'override', 'contrary', 'vs', 'versus', 'contradict', 'inconsistent']
        conflict_score = min(1.0, sum(1 for k in conflict_kw if k in combined) / 3.0)

        # Feature 3: Ambiguity level
        amb_kw = ['reasonable', 'material', 'substantial', 'appropriate', 'may',
                  'discretion', 'judgment', 'good faith', 'sole', 'satisfactory',
                  'mutually', 'agreed upon', 'unclear', 'ambiguous', 'undefined',
                  'placeholder', 'blank', 'tbd']
        amb_score = min(1.0, sum(1 for k in amb_kw if k in combined) / 4.0)

        # Feature 4: Party exposure
        party_kw = ['indemnif', 'liabilit', 'oblig', 'warrant', 'represent',
                    'covenant', 'agree', 'shall', 'party', 'parties',
                    'operator', 'non-operator', 'contractor', 'company']
        party_score = min(1.0, sum(1 for k in party_kw if k in combined) / 5.0)

        # Feature 5: Enforceability risk
        enforce_kw = ['void', 'voidable', 'unenforceable', 'invalid', 'null',
                      'breach', 'default', 'terminat', 'injunctive', 'specific performance',
                      'arbitrat', 'litigation', 'court', 'legal entity', 'enforceable']
        enforce_score = min(1.0, sum(1 for k in enforce_kw if k in combined) / 3.0)

        return [fin_score, conflict_score, amb_score, party_score, enforce_score]

    def score_finding(self, finding):
        """Score a single finding using EBM — returns (risk_score, features)"""
        features = self.extract_features(finding)
        X = np.array([features])
        raw = float(self.ebm.predict(X)[0])
        # Clamp to valid range with meaningful floor/ceiling
        score = max(0.15, min(0.90, raw))
        return round(score, 2), features

    def score_citations(self, citations):
        """Legacy method for citation scoring"""
        print(f"[L4-SCORE] Scoring {len(citations)} citations...")
        scored = []
        for i, citation in enumerate(citations):
            features = [0.5, 0.5, 0.5, 0.5, 0.5]
            score = float(self.ebm.predict(np.array([features]))[0])
            scored.append({
                'finding_id': f"finding_{i}",
                'document_name': str(getattr(citation, 'document_name', 'Unknown')),
                'content_excerpt': str(getattr(citation, 'content_excerpt', ''))[:500],
                'risk_score': max(0.15, min(0.90, score)),
                'keywords': getattr(citation, 'keywords', []),
                'retrieval_score': float(getattr(citation, 'retrieval_score', 0.5))
            })
        print(f"[L4-SCORE] ✓ Scored {len(scored)} citations")
        return scored
