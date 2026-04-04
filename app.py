#!/usr/bin/env python3
"""VERILENCE Web Frontend - Flask Server"""

from flask import Flask, render_template, request, jsonify
from pathlib import Path
import json
import os

# Import all layers
from layer1_ingestion import IngestionEngine
from layer2_embedding import EmbeddingLayer
from layer3_rag_qdrant import RAGEngineQdrant
from layer4_ebm import GlassBoxJudge
from layer5_llm import DiscoveryAgent
from layer6_confidence_routing import ConfidenceRouter
from layer9_audit_reporting import AuditReportGenerator

app = Flask(__name__, template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)
Path(OUTPUT_FOLDER).mkdir(exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'ok',
        'version': '1.0',
        'services': {
            'web': 'running',
            'qdrant': 'check http://localhost:6333'
        }
    })

@app.route('/api/upload', methods=['POST'])
def upload():
    """Main analysis pipeline - scan entire document for ANY contradictions"""
    try:
        # 1. INGEST
        print("\n" + "="*60)
        print("STARTING VERILENCE ANALYSIS PIPELINE")
        print("="*60)
        
        file = request.files['file']
        if not file:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        print(f"\n[UPLOAD] Saved: {filename}")
        
        # Layer 1: Ingestion
        ingester = IngestionEngine()
        documents = ingester.load_documents(UPLOAD_FOLDER)
        chunks = ingester.chunk_documents()
        ingester.save_chunks(chunks)
        
        chunks_created = len(chunks)
        
        # Layer 2: Embedding
        embedder = EmbeddingLayer()
        embedder.embed_chunks(chunks)
        embedder.save_embeddings(f"{OUTPUT_FOLDER}/embeddings.json")
        
        # Layer 3: RAG
        rag = RAGEngineQdrant()
        rag.load_and_index()
        
        # Layer 4: EBM Scoring
        judge = GlassBoxJudge()
        
        # Layer 5: LLM Discovery
        agent = DiscoveryAgent()
        
        # Layer 6: Routing
        router = ConfidenceRouter()
        
        # Layer 9: Reporting
        reporter = AuditReportGenerator()
        
        # FREE ANALYSIS: Pass ALL chunks to Gemini for contradiction detection
        print(f"\n[PIPELINE] Analyzing {len(chunks)} chunks for ANY contradictions...")
        
        # Prepare chunks for LLM analysis
        all_content = "\n\n---CHUNK BREAK---\n\n".join([c.get('content', '') for c in chunks])
        
        # Ask Gemini to find ALL contradictions
        findings = agent.analyze_full_document(all_content, filename)
        
        if not findings:
            print("[PIPELINE] ℹ No contradictions found")
            return jsonify({
                'success': True,
                'filename': filename,
                'chunks_created': chunks_created,
                'analyzed': 0,
                'results': [],
                'message': 'Document analyzed - no contradictions detected'
            })
        
        # Score and route findings
        routed = router.route_findings(findings)
        
        # Generate audit report
        briefing = {
            'executive_summary': f'Analyzed {chunks_created} chunks. Found {len(routed)} contradictions.',
            'findings_count': len(routed)
        }
        
        retrieval_result_dummy = type('Result', (), {
            'retrieval_score': 0.75,
            'citations': []
        })()
        
        report_path = reporter.generate_audit_report(
            'contradiction detection', routed, briefing, retrieval_result_dummy, 
            [{'risk_score': f.risk_score} for f in routed]
        )
        
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE")
        print("="*60 + "\n")
        
        return jsonify({
            'success': True,
            'filename': filename,
            'chunks_created': chunks_created,
            'analyzed': len(routed),
            'results': [{
                'query': 'full document scan',
                'findings': len(routed),
                'report_path': report_path
            }]
        })
    
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports')
def list_reports():
    """List all generated reports"""
    try:
        reports = []
        for file in sorted(Path(OUTPUT_FOLDER).glob('audit_report_*.json'), reverse=True):
            reports.append({
                'filename': file.name,
                'path': f'/api/report/{file.name}'
            })
        return jsonify({'reports': reports})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/report/<filename>')
def get_report(filename):
    """Get specific report"""
    try:
        filepath = Path(OUTPUT_FOLDER) / filename
        if not filepath.exists():
            return jsonify({'error': 'Report not found'}), 404
        
        with open(filepath) as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n[APP] VERILENCE Web Server Starting...")
    print("[APP] Visit: http://localhost:5000")
    app.run(debug=False, host='0.0.0.0', port=5000)

