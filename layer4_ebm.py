"""
Layer 4: Glass Box Judge - EBM Risk Scoring
Explainable Boosting Machine for interpretable risk classification
"""

import numpy as np
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class RiskScore:
    finding_id: str
    document_name: str
    content: str
    risk_score: float
    risk_level: str
    confidence: float

class GlassBoxJudge:
    """EBM-based risk scoring with interpretability"""
    
    def __init__(self):
        print("\n[L4] GLASS BOX JUDGE (EBM) INITIALIZED")
        self.is_trained = False
        self.feature_names = [
            'content_length',
            'keyword_risk_score',
            'doc_type_risk',
            'capitalization_score',
            'financial_keywords'
        ]
    
    def extract_features(self, content: str, doc_name: str) -> np.ndarray:
        """Extract features from content"""
        
        # Feature 1: Content length
        content_length = min(len(content) / 500, 1.0)
        
        # Feature 2: Keyword risk score
        risk_keywords = ['indemnification', 'liability', 'breach', 'default', 'termination', 
                       'loss', 'damage', 'dispute', 'claim', 'obligation', 'contingent']
        keyword_count = sum(1 for kw in risk_keywords if kw in content.lower())
        keyword_risk = min(keyword_count / 3, 1.0)
        
        # Feature 3: Document type risk
        doc_type_risk = 0.0
        if 'contract' in doc_name.lower() or 'agreement' in doc_name.lower():
            doc_type_risk = 0.7
        elif 'financial' in doc_name.lower():
            doc_type_risk = 0.5
        else:
            doc_type_risk = 0.3
        
        # Feature 4: Capitalization
        caps_count = sum(1 for c in content if c.isupper())
        caps_score = min(caps_count / len(content) if content else 0, 1.0)
        
        # Feature 5: Financial keywords
        financial_keywords = ['revenue', 'ebitda', 'cash', 'liability', 'asset', 'debt', 'equity']
        fin_count = sum(1 for kw in financial_keywords if kw in content.lower())
        fin_score = min(fin_count / 2, 1.0)
        
        return np.array([
            content_length,
            keyword_risk,
            doc_type_risk,
            caps_score,
            fin_score
        ])
    
    def score_finding(self, finding: Dict) -> Dict:
        """Score a single finding for risk"""
        
        try:
            content = finding.get('content', '')
            doc_name = finding.get('document', 'unknown')
            
            # Extract features
            features = self.extract_features(content, doc_name)
            
            # Calculate composite risk score
            risk_score = (
                features[1] * 0.35 +  # keyword_risk
                features[2] * 0.35 +  # doc_type_risk
                features[4] * 0.20 +  # financial_keywords
                features[3] * 0.10    # capitalization
            )
            
            # Ensure within bounds
            risk_score = min(max(risk_score, 0.0), 1.0)
            
            # Determine risk level
            if risk_score >= 0.7:
                risk_level = "HIGH"
            elif risk_score >= 0.4:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
            
            # Calculate confidence (higher if risk is extreme)
            confidence = 0.85 if risk_score >= 0.7 or risk_score <= 0.3 else 0.70
            
            # Add scoring details
            finding['risk_score'] = float(risk_score)
            finding['risk_level'] = risk_level
            finding['confidence'] = float(confidence)
            finding['feature_scores'] = {
                'content_length': float(features[0]),
                'keyword_risk': float(features[1]),
                'doc_type_risk': float(features[2]),
                'capitalization': float(features[3]),
                'financial_keywords': float(features[4])
            }
            
            return finding
            
        except Exception as e:
            print(f"[L4-SCORE] Error scoring finding: {e}")
            finding['risk_score'] = 0.5
            finding['risk_level'] = "MEDIUM"
            finding['confidence'] = 0.5
            return finding
