#!/usr/bin/env python3
import os
import json
from layer3_rag_qdrant import RAGEngineQdrant
from layer4_ebm import GlassBoxJudge
from layer5_llm import DiscoveryAgent
from layer6_confidence_routing import ConfidenceRouter
from dataclasses import asdict
from datetime import datetime

def main():
    print("\n" + "="*70)
    print("VERILENCE - WEEK 4: CONFIDENCE ROUTING + HITL")
    print("="*70)
    
    if not os.path.exists("output/embeddings.json"):
        print("Error: Run Week 1 first")
        return
    
    print("\n[INIT] Initializing all layers...")
    rag = RAGEngineQdrant()
    rag.load_and_index()
    
    judge = GlassBoxJudge()
    agent = DiscoveryAgent(api_key=os.getenv('GOOGLE_API_KEY'))
    router = ConfidenceRouter()
    
    print("\n[READY] Type queries or 'quit' to exit\n")
    
    while True:
        query = input("[QUERY] > ").strip()
        if query.lower() == 'quit':
            break
        if not query:
            continue
        
        # Step 1: Retrieve
        retrieval_result = rag.retrieve(query, top_k=3)
        
        if not retrieval_result.citations:
            print("No relevant documents found\n")
            continue
        
        # Step 2: Score with EBM
        risk_scores = judge.score_citations(retrieval_result.citations)
        
        # Step 3: Synthesize with LLM
        findings = agent.synthesize_findings(risk_scores)
        
        # Step 4: Route with confidence
        routed_findings = router.route_findings(findings, retrieval_score=retrieval_result.retrieval_score)
        
        # Step 5: Generate briefing
        briefing = router.generate_briefing(routed_findings)
        
        # Display results
        print(f"\n{'='*70}")
        print(f"ANALYSIS: {query}")
        print(f"{'='*70}\n")
        
        print(f"Executive Summary: {briefing['executive_summary']}")
        print(f"Auto-Approval Rate: {briefing['auto_approval_rate']}\n")
        
        # Auto-approved
        if briefing['auto_approved_findings']:
            print("[AUTO-APPROVED] (No human review needed)")
            for f in briefing['auto_approved_findings']:
                print(f"  ✓ {f['document_name']} - {f['risk_level']} (confidence: {f['confidence_score']:.2f})")
            print()
        
        # Analyst queue
        if briefing['analyst_review_queue']:
            print("[ANALYST REVIEW QUEUE] (Standard review)")
            for f in briefing['analyst_review_queue']:
                print(f"  ⚠ {f['document_name']} - {f['risk_level']} (confidence: {f['confidence_score']:.2f})")
            print()
        
        # Escalation
        if briefing['escalation_queue']:
            print("[ESCALATION QUEUE] (Senior partner review)")
            for f in briefing['escalation_queue']:
                print(f"  🚨 {f['document_name']} - {f['risk_level']} (confidence: {f['confidence_score']:.2f})")
            print()
        
        # Save briefing
        save_briefing(briefing, query)

def save_briefing(briefing, query):
    Path = __import__('pathlib').Path
    output = {
        'query': query,
        'briefing': briefing,
        'timestamp': datetime.now().isoformat()
    }
    
    Path('output').mkdir(exist_ok=True)
    filename = f"output/briefing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)

if __name__ == '__main__':
    main()

