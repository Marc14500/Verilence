#!/usr/bin/env python3
"""
VERILENCE Web Frontend - Flask API Server
Handles PDF uploads, document ingestion, and analysis
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path
import json
import os
import shutil
from datetime import datetime
import PyPDF2
import threading

from layer1_ingestion import IngestionEngine
from layer3_rag_qdrant import RAGEngineQdrant
from layer4_ebm import GlassBoxJudge
from layer5_llm import DiscoveryAgent
from layer6_confidence_routing import ConfidenceRouter
from layer9_audit_reporting import AuditReportGenerator

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

Path(UPLOAD_FOLDER).mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Global state
analysis_state = {
    "status": "ready",
    "current_file": None,
    "progress": 0,
    "message": ""
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_pdf_text(pdf_path):
    """Extract text from PDF"""
    text = ""
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"
    return text

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "1.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload PDF or text document"""
    global analysis_state
    
    # CACHE FIX: Clear old uploads before processing new one
    if Path(UPLOAD_FOLDER).exists():
        shutil.rmtree(UPLOAD_FOLDER)
    Path(UPLOAD_FOLDER).mkdir(exist_ok=True)
    
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF, TXT, and DOCX files allowed"}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = Path(UPLOAD_FOLDER) / filename
        file.save(str(filepath))
        
        # Extract text if PDF
        if filename.endswith('.pdf'):
            text = extract_pdf_text(str(filepath))
            txt_path = filepath.with_suffix('.txt')
            with open(txt_path, 'w') as f:
                f.write(text)
            filepath = txt_path
        
        analysis_state["current_file"] = filename
        analysis_state["status"] = "uploaded"
        analysis_state["progress"] = 20
        
        return jsonify({
            "success": True,
            "filename": filename,
            "path": str(filepath),
            "size": filepath.stat().st_size
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Run full analysis pipeline"""
    global analysis_state
    
    try:
        analysis_state["status"] = "analyzing"
        analysis_state["progress"] = 30
        
        # Layer 1: Ingestion
        ingestion = IngestionEngine()
        documents = ingestion.load_documents(UPLOAD_FOLDER)
        
        if not documents:
            return jsonify({"error": "No documents found"}), 400
        
        # Layer 2: Embedding (skipped for speed)
        analysis_state["progress"] = 40
        
        # Layer 3-5: RAG + LLM Analysis
        rag = RAGEngineQdrant()
        llm = DiscoveryAgent()
        
        all_findings = []
        for doc in documents:
            findings = llm.analyze_full_document(doc['text'], doc['filename'])
            all_findings.extend(findings)
        
        analysis_state["progress"] = 60
        
        # Layer 4: EBM Scoring
        judge = GlassBoxJudge()
        scored_findings = [judge.score_finding(f) for f in all_findings]
        
        analysis_state["progress"] = 80
        
        # Layer 6: Confidence Routing
        router = ConfidenceRouter()
        routed_findings = [router.route(f) for f in scored_findings]
        
        # Layer 9: Audit Report
        report_gen = AuditReportGenerator()
        json_report = report_gen.generate_json_report(routed_findings, documents[0]['filename'])
        html_report = report_gen.generate_html_report(routed_findings, documents[0]['filename'])
        
        analysis_state["status"] = "complete"
        analysis_state["progress"] = 100
        
        # Save reports
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        json_path = output_dir / "report.json"
        html_path = output_dir / "report.html"
        
        with open(json_path, 'w') as f:
            json.dump(json_report, f, indent=2)
        
        with open(html_path, 'w') as f:
            f.write(html_report)
        
        return jsonify({
            "success": True,
            "findings": routed_findings,
            "report_json": str(json_path),
            "report_html": str(html_path),
            "status": "complete"
        }), 200
        
    except Exception as e:
        analysis_state["status"] = "error"
        return jsonify({"error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Get analysis status"""
    return jsonify(analysis_state), 200

@app.route('/output/<path:filename>', methods=['GET'])
def download_report(filename):
    """Download generated report"""
    try:
        return send_file(f"output/{filename}", as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

if __name__ == '__main__':
    print("=" * 60)
    print("VERILENCE WEB SERVER STARTING")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
