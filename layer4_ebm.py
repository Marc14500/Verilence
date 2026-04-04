#!/usr/bin/env python3
"""Layer 4: Glass Box Judge - EBM Risk Scoring"""

from interpret.glassbox import ExplainableBoostingRegressor
import numpy as np

class GlassBoxJudge:
    def __init__(self):
        print("\n[L4] GLASS BOX JUDGE (EBM)")
        self.ebm = None
    
    def score_citations(self, citations):
        """Score citations using EBM"""
        print(f"[L4-SCORE] Scoring {len(citations)} citations...")
        
        # Prepare features from citations
        features = []
        
        for citation in citations:
            # Extract features safely
            doc_name = str(getattr(citation, 'document_name', 'Unknown'))
            content = str(getattr(citation, 'content_excerpt', ''))
            score = float(getattr(citation, 'score', 0.5))
            
            # Build feature vector
            feature = {
                'keyword_risk': score * 0.6,  # Retrieval score influence
                'doc_type_risk': 0.3,  # Base risk for any document
                'financial_score': score * 0.4,  # Score influence
                'caps_score': 0.1  # Base caps/liability risk
            }
            
            features.append(feature)
        
        # Train EBM on synthetic data (avoid fitting on small datasets)
        print("[L4-SCORE] Training EBM with synthetic data...")
        
        X_train = np.array([
            [0.1, 0.2, 0.15, 0.05],
            [0.3, 0.3, 0.25, 0.1],
            [0.5, 0.4, 0.35, 0.15],
            [0.7, 0.5, 0.45, 0.2],
            [0.9, 0.6, 0.55, 0.25]
        ])
        y_train = np.array([0.15, 0.35, 0.55, 0.75, 0.95])
        
        self.ebm = ExplainableBoostingRegressor(max_bins=16, interactions=0)
        self.ebm.fit(X_train, y_train)
        print("[L4-SCORE] ✓ EBM trained on synthetic data")
        
        # Score citations
        X_test = np.array([
            [f['keyword_risk'], f['doc_type_risk'], f['financial_score'], f['caps_score']]
            for f in features
        ])
        
        scores = self.ebm.predict(X_test)
        
        # Create scored citations
        scored = []
        for i, citation in enumerate(citations):
            scored_citation = {
                'finding_id': f"finding_{i}",
                'document_name': str(getattr(citation, 'document_name', 'Unknown')),
                'content_excerpt': str(getattr(citation, 'content_excerpt', ''))[:500],
                'risk_score': float(scores[i]),
                'keywords': getattr(citation, 'keywords', []),
                'retrieval_score': float(getattr(citation, 'retrieval_score', 0.5))
            }
            scored.append(scored_citation)
        
        print(f"[L4-SCORE] ✓ Scored {len(scored)} citations")
        return scored

