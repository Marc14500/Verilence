#!/usr/bin/env python3
"""Layer 6: Confidence Router - Route findings to appropriate review level"""

class ConfidenceRouter:
    def __init__(self):
        print("\n[L6] CONFIDENCE ROUTER")
    
    def route_findings(self, findings):
        """Route findings based on confidence threshold"""
        print(f"[L6-ROUTE] Routing {len(findings)} findings...")
        
        routed = []
        
        for finding in findings:
            # Extract confidence safely
            confidence = getattr(finding, 'confidence_score', getattr(finding, 'confidence', 0.5))
            risk_level = getattr(finding, 'risk_level', 'MEDIUM')
            
            # Determine routing based on confidence
            if confidence > 0.85:
                routing = 'AUTO_APPROVE'
            elif confidence > 0.60:
                routing = 'ANALYST_REVIEW'
            else:
                routing = 'SENIOR_PARTNER_ESCALATION'
            
            # Update finding with routing
            finding.routing_action = routing
            finding.confidence_level = 'HIGH' if confidence > 0.8 else 'MEDIUM' if confidence > 0.6 else 'LOW'
            
            # Ensure all required attributes exist
            if not hasattr(finding, 'content_excerpt'):
                finding.content_excerpt = getattr(finding, 'explanation', '')[:500]
            if not hasattr(finding, 'recommendation'):
                finding.recommendation = f"Review and resolve {getattr(finding, 'title', 'finding')}"
            if not hasattr(finding, 'retrieval_score'):
                finding.retrieval_score = 0.5
            
            routed.append(finding)
            print(f"  ✓ {getattr(finding, 'title', 'Finding')} → {routing} (confidence: {confidence:.2f})")
        
        print(f"[L6-ROUTE] ✓ Routed {len(routed)} findings")
        return routed

