#!/usr/bin/env python3
import os
import json
from layer3_rag_qdrant import RAGEngineQdrant
from layer4_ebm import GlassBoxJudge
from layer5_llm import DiscoveryAgent
from dataclasses import asdict

def main():
    print("\n" + "="*70)
    print("VERILENCE - WEEK 3: EBM SCORING + LLM SYNTHESIS")
    print("="*70)
    
    if not os.path.exists("output/embeddings.json"):
        print("Error: Run Week 1 first")
        return
    
    print("\n[INIT] Initializing all layers...")
    rag = RAGEngineQdrant()
    rag.load_and_index()
    
    judge = GlassBoxJudge()
    agent = DiscoveryAgent(api_key=os.getenv('GOOGLE_API_KEY'))
    
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
        
        # Display results
        print(f"\n{'='*70}")
        print(f"FINDINGS FOR: {query}")
        print(f"{'='*70}\n")
        
        for i, finding in enumerate(findings, 1):
            print(f"[Finding {i}]")
            print(f"  Document: {finding.document_name}")
            print(f"  Risk Level: {finding.risk_level} (Score: {finding.risk_score:.2f}, Confidence: {finding.confidence:.2f})")
            print(f"  Summary: {finding.explanation}")
            print(f"  Action: {finding.recommendation}")
            print()
        
        # Save findings
        save_findings(findings, query)

def save_findings(findings, query):
    output = {
        'query': query,
        'findings': [asdict(f) for f in findings],
        'timestamp': __import__('datetime').datetime.now().isoformat()
    }
    
    filename = f"output/findings_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)

if __name__ == '__main__':
    main()

