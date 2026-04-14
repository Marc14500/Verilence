from flask import Flask, render_template, request, jsonify
import os
from layer1_ingestion import IngestionEngine
from layer2_embedding import EmbeddingLayer
from layer3_rag_qdrant import RAGEngineQdrant
from layer4_ebm import GlassBoxJudge
from layer5_llm import DiscoveryAgent

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

latest_results = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if latest_results is None:
        return render_template('index.html')
    return render_template('dashboard.html', data=latest_results)

@app.route('/api/upload', methods=['POST'])
def upload():
    """Main analysis pipeline"""
    try:
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
        
        # Layer 2: Embedding
        embedder = EmbeddingLayer()
        embedded_chunks = embedder.embed_chunks(chunks)
        embedder.save_embeddings(f"{OUTPUT_FOLDER}/embeddings.json")
        
        # Layer 3: RAG
        rag = RAGEngineQdrant()
        if embedded_chunks:
            vector_size = len(embedded_chunks[0]['embedding'])
            rag.create_collection(vector_size=vector_size)
            rag.index_chunks(embedded_chunks)
            print(f"[L3-RAG] ✓ Ready for queries")
        
        # Layer 4: EBM
        judge = GlassBoxJudge()
        all_issues = judge.find_potential_issues(embedded_chunks)
        high_risk = [issue for issue in all_issues if issue['ebm_risk_score'] > 0.35]
        
        # Format for dashboard
        findings = []
        for i, issue in enumerate(high_risk):
            score = issue['ebm_risk_score']
            section_a = issue.get('section_a', 'Unknown')
            section_b = issue.get('section_b', 'Unknown')
            
            findings.append({
                'id': f'finding_{i}',
                'title': f"Potential Issue: {section_a} vs {section_b}",
                'risk_level': 'HIGH' if score > 0.70 else 'MEDIUM' if score > 0.55 else 'LOW',
                'risk_score': round(score, 2),
                'confidence': min(100, max(50, int(score * 100 + (issue['semantic_similarity'] * 20)))),
                'problem': f"Analyzing...",
                'impact': f"{section_a} and {section_b} may contain conflicting provisions",
                'signals': {
                    'clarity': min(100, int(score * 100)),
                    'chunk': int(issue['semantic_similarity'] * 100),
                    'gemini': 0
                },
                'routing': 'ANALYST_REVIEW',
                'section_a': section_a,
                'section_b': section_b,
                'section_1': section_a,
                'section_2': section_b,
                'text_a': issue['text_a'],
                'text_b': issue['text_b'],
                'excerpt_a': issue['text_a'][:500],
                'excerpt_b': issue['text_b'][:500]
            })
        
        findings = findings[:10]
        
        # Layer 5: Gemini explanations with title
        print(f"\n[L5-LLM] Explaining {len(findings)} findings...")
        agent = DiscoveryAgent()
        for finding in findings:
            title, explanation, gemini_confidence = agent.analyze_full_document(
                finding['excerpt_a'],
                finding['excerpt_b'],
                finding['section_a'],
                finding['section_b']
            )
            if title:
                finding['title'] = f"Potential Issue: {title}"
            if explanation:
                finding['problem'] = explanation
            if gemini_confidence:
                finding['signals']['gemini'] = gemini_confidence
        
        print(f"\n[PIPELINE] ✓ Analysis complete: {len(findings)} findings")
        
        global latest_results
        latest_results = {
            'report_id': f'VER-{len(findings):04d}',
            'filename': filename,
            'findings': findings
        }
        
        return jsonify({
            'success': True,
            'redirect': '/dashboard'
        })
    
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
