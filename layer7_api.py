from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os

from layer3_rag_qdrant import RAGEngineQdrant
from layer4_ebm import GlassBoxJudge
from layer5_llm import DiscoveryAgent
from layer6_confidence_routing import ConfidenceRouter

app = FastAPI(title="Verilence API", version="0.1.0")

rag = None
judge = None
agent = None
router = None

@app.on_event("startup")
async def startup():
    global rag, judge, agent, router
    print("[API] Initializing engines...")
    rag = RAGEngineQdrant()
    rag.load_and_index()
    judge = GlassBoxJudge()
    agent = DiscoveryAgent(api_key=os.getenv('GOOGLE_API_KEY'))
    router = ConfidenceRouter()
    print("[API] ✓ Ready")

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3

@app.post("/query")
async def query_documents(request: QueryRequest):
    """Query documents and get findings"""
    print(f"\n[API-QUERY] {request.query}")
    
    try:
        retrieval_result = rag.retrieve(request.query, top_k=request.top_k)
        
        if not retrieval_result.citations:
            return {
                'query': request.query,
                'total_findings': 0,
                'auto_approved': 0,
                'analyst_review': 0,
                'escalation': 0,
                'auto_approval_rate': '0%',
                'findings': []
            }
        
        risk_scores = judge.score_citations(retrieval_result.citations)
        findings = agent.synthesize_findings(risk_scores)
        routed_findings = router.route_findings(findings, retrieval_score=retrieval_result.retrieval_score)
        
        findings_list = []
        for f in routed_findings:
            findings_list.append({
                'document': f.document_name,
                'risk_level': f.risk_level,
                'risk_score': f.risk_score,
                'confidence': f.confidence_score,
                'confidence_level': f.confidence_level,
                'routing': f.routing_action,
                'explanation': f.explanation,
                'recommendation': f.recommendation
            })
        
        auto_approved = sum(1 for f in routed_findings if f.confidence_level == "HIGH")
        analyst_review = sum(1 for f in routed_findings if f.confidence_level == "MEDIUM")
        escalation = sum(1 for f in routed_findings if f.confidence_level == "LOW")
        
        return {
            'query': request.query,
            'total_findings': len(routed_findings),
            'auto_approved': auto_approved,
            'analyst_review': analyst_review,
            'escalation': escalation,
            'auto_approval_rate': f"{auto_approved / len(routed_findings) * 100:.1f}%" if routed_findings else "0%",
            'findings': findings_list
        }
    
    except Exception as e:
        print(f"[API-QUERY] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}

@app.get("/status")
async def status():
    return {
        "qdrant_collection": "verilence",
        "embeddings_loaded": True,
        "ebm_ready": True,
        "llm_ready": True,
        "router_ready": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

