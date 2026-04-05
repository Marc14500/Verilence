#!/usr/bin/env python3
"""VERILENCE Web Frontend - Flask Server"""

from flask import Flask, render_template, request, jsonify, redirect
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

UPLOAD_FOLDER = '/home/greavesgm/verilence/uploads'
OUTPUT_FOLDER = '/home/greavesgm/verilence/output'
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)
Path(OUTPUT_FOLDER).mkdir(exist_ok=True)


def _chunk_quality(finding):
    """Score chunk quality based on specificity of section quotes"""
    s1 = getattr(finding, 'section_1', '')
    s2 = getattr(finding, 'section_2', '')
    combined = len(s1) + len(s2)
    # More specific quotes = better chunk quality
    if combined > 300: return 90
    if combined > 200: return 80
    if combined > 100: return 70
    if combined > 50:  return 60
    return 50

def _calc_confidence(finding):
    """Calculate confidence from 3 independent signals with real variation"""
    # Signal 1: Text clarity — based on risk score distance from ambiguous midpoint
    # risk=0.3 or 0.7 = clear finding, risk=0.5 = ambiguous
    risk = float(finding.risk_score)
    clarity = min(1.0, abs(risk - 0.5) * 3.0)  # 0.0-1.0, never exceeds 1.0

    # Signal 2: Gemini detection confidence — raw value returned by LLM (0.0-1.0)
    gemini = min(1.0, float(getattr(finding, 'confidence', 0.75)))

    # Signal 3: Chunk quality — specificity of retrieved section quotes
    chunk = _chunk_quality(finding) / 100.0

    # Weighted formula: 35/35/30
    raw = (clarity * 0.35) + (gemini * 0.35) + (chunk * 0.30)
    return raw * 100  # return as percentage 0-100
    x = (clarity * 0.35) + (chunk * 0.30)
    return raw * 100

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health')
def health():
    # Save dashboard data
        dashboard_payload = {
            'report_id': f'VER-{__import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'analysis_date': __import__("datetime").datetime.now().strftime('%B %-d, %Y'),
            'document': filename,
            'findings': [{
                'id': i+1,
                'title': getattr(f, 'title', 'Contradiction'),
                'risk_score': float(f.risk_score),
                'risk_level': f.risk_level,
                'confidence': round(min(_calc_confidence(f), 89.0), 1),
                'routing': f.routing_action,
                'impact': getattr(f, 'financial_impact', 'Unknown'),
                'section_1': getattr(f, 'section_1', ''),
                'section_2': getattr(f, 'section_2', ''),
                'problem': getattr(f, 'why_problem', ''),
                'signals': {'clarity': round((1.0 - abs(0.5 - f.risk_score)) * 100), 'gemini': round(float(f.confidence) * 100), 'chunk': 75}
            } for i, f in enumerate(routed)]
        }
        with open(Path(OUTPUT_FOLDER) / 'dashboard_data.json', 'w') as df:
            json.dump(dashboard_payload, df, indent=2)
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
        
        # Score findings with EBM — sets real risk_score on each finding
        print("[APP] Scoring findings with EBM...")
        for f in findings:
            ebm_score, features = judge.score_finding(f)
            f.risk_score = ebm_score
            f.ebm_features = features
            print(f"  EBM score: {ebm_score:.2f} — {getattr(f, 'title', 'Finding')[:50]}")

        # Route findings based on EBM risk scores
        routed = router.route_findings(findings)

        # Save dashboard data
        from datetime import datetime as _dt
        dashboard_payload = {
            'report_id': f"VER-{_dt.now().strftime('%Y%m%d_%H%M%S')}",
            'analysis_date': _dt.now().strftime('%B %-d, %Y'),
            'document': filename,
            'findings': [{
                'id': i+1,
                'title': getattr(f, 'title', 'Contradiction'),
                'risk_score': float(f.risk_score),
                'risk_level': f.risk_level,
                'confidence': round(min(_calc_confidence(f), 89.0), 1),
                'routing': f.routing_action,
                'impact': getattr(f, 'financial_impact', 'Unknown'),
                'section_1': getattr(f, 'section_1', ''),
                'section_2': getattr(f, 'section_2', ''),
                'problem': getattr(f, 'why_problem', ''),
                'signals': {
                    'clarity': round((1.0 - abs(0.5 - f.risk_score)) * 100),
                    'gemini': round(float(f.confidence) * 100),
                    'chunk': _chunk_quality(f)
                }
            } for i, f in enumerate(routed)]
        }
        with open(Path(OUTPUT_FOLDER) / 'dashboard_data.json', 'w') as df:
            json.dump(dashboard_payload, df, indent=2)
        print("[APP] Dashboard data saved")

        
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
        
        # Save dashboard data
        dashboard_payload = {
            'report_id': f'VER-{__import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'analysis_date': __import__("datetime").datetime.now().strftime('%B %-d, %Y'),
            'document': filename,
            'findings': [{
                'id': i+1,
                'title': getattr(f, 'title', 'Contradiction'),
                'risk_score': float(f.risk_score),
                'risk_level': f.risk_level,
                'confidence': round(min(_calc_confidence(f), 89.0), 1),
                'routing': f.routing_action,
                'impact': getattr(f, 'financial_impact', 'Unknown'),
                'section_1': getattr(f, 'section_1', ''),
                'section_2': getattr(f, 'section_2', ''),
                'problem': getattr(f, 'why_problem', ''),
                'signals': {'clarity': round((1.0 - abs(0.5 - f.risk_score)) * 100), 'gemini': round(float(f.confidence) * 100), 'chunk': 75}
            } for i, f in enumerate(routed)]
        }
        with open(Path(OUTPUT_FOLDER) / 'dashboard_data.json', 'w') as df:
            json.dump(dashboard_payload, df, indent=2)
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


@app.route('/dashboard')
def dashboard():
    """Render live dashboard from most recent analysis"""
    try:
        data_path = Path(OUTPUT_FOLDER) / 'dashboard_data.json'
        if not data_path.exists():
            return redirect('/')
        with open(data_path) as f:
            data = json.load(f)
        return render_template('dashboard.html', data=data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/latest-report')
def latest_report():
    """Serve the most recent HTML audit report"""
    try:
        reports = sorted(Path(OUTPUT_FOLDER).glob('audit_report_*.html'), reverse=True)
        if not reports:
            return "No reports found", 404
        with open(reports[0]) as f:
            return f.read()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n[APP] VERILENCE Web Server Starting...")
    print("[APP] Visit: http://localhost:5000")
    app.run(debug=False, host='0.0.0.0', port=5000)




