import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health: {response.json()}")

def test_status():
    response = requests.get(f"{BASE_URL}/status")
    print(f"Status: {response.json()}")

def test_query(query: str):
    payload = {"query": query, "top_k": 3}
    response = requests.post(f"{BASE_URL}/query", json=payload)
    result = response.json()
    
    print(f"\n{'='*70}")
    print(f"QUERY: {query}")
    print(f"{'='*70}")
    print(f"Total Findings: {result['total_findings']}")
    print(f"Auto-Approved: {result['auto_approved']}")
    print(f"Analyst Review: {result['analyst_review']}")
    print(f"Escalation: {result['escalation']}")
    print(f"Auto-Approval Rate: {result['auto_approval_rate']}")
    
    print(f"\nFindings:")
    for finding in result['findings']:
        print(f"  {finding['document']} - {finding['risk_level']} (confidence: {finding['confidence']:.2f})")
        print(f"    Routing: {finding['routing']}")
        print(f"    Summary: {finding['explanation']}")

if __name__ == "__main__":
    print("[TEST] Starting API tests...\n")
    
    test_health()
    test_status()
    
    test_query("purchase price")
    test_query("revenue")

