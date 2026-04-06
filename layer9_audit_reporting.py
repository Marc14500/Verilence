#!/usr/bin/env python3
"""Layer 9: Business-Friendly, Transparent Audit Reporting"""

import json
from pathlib import Path
from datetime import datetime
import hashlib

class AuditReportGenerator:

    def __init__(self):
        print("\n[L9] AUDIT-READY REPORT GENERATOR")

    def generate_audit_report(self, query, routed_findings, briefing, retrieval_result, risk_scores, output_dir="output"):
        Path(output_dir).mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self._generate_audit_json(query, routed_findings, briefing, retrieval_result, risk_scores, output_dir, timestamp)
        self._generate_audit_html(query, routed_findings, briefing, retrieval_result, risk_scores, output_dir, timestamp)
        return f"{output_dir}/audit_report_{timestamp}"

    def _calc_confidence(self, finding, retrieval_result):
        """Calculate confidence using the same formula as app.py"""
        risk = float(getattr(finding, 'risk_score', 0.5))
        clarity = min(1.0, abs(risk - 0.5) * 3.0)
        gemini = min(1.0, float(getattr(finding, 'confidence', 0.75)))
        s1 = str(getattr(finding, 'section_1', ''))
        s2 = str(getattr(finding, 'section_2', ''))
        combined_len = len(s1) + len(s2)
        if combined_len > 300: chunk = 0.90
        elif combined_len > 200: chunk = 0.80
        elif combined_len > 100: chunk = 0.70
        elif combined_len > 50: chunk = 0.60
        else: chunk = 0.50
        raw = (clarity * 0.35) + (gemini * 0.35) + (chunk * 0.30)
        return min(raw * 100, 89.0), clarity * 100, gemini * 100, chunk * 100

    def _generate_audit_json(self, query, routed_findings, briefing, retrieval_result, risk_scores, output_dir, timestamp):
        findings_detail = []
        for i, finding in enumerate(routed_findings):
            conf, clarity, gemini_sig, chunk = self._calc_confidence(finding, retrieval_result)
            findings_detail.append({
                "finding_id": finding.finding_id,
                "document": finding.document_name,
                "title": getattr(finding, 'title', 'Contradiction'),
                "risk_score": float(finding.risk_score),
                "risk_level": finding.risk_level,
                "explanation": getattr(finding, 'explanation', ''),
                "confidence_score": round(conf, 1),
                "confidence_level": finding.confidence_level,
                "routing_decision": finding.routing_action,
                "signals": {
                    "clarity": round(clarity, 1),
                    "gemini": round(gemini_sig, 1),
                    "chunk": round(chunk, 1)
                }
            })

        report = {
            "report_id": f"VER-{timestamp}",
            "generated_timestamp": datetime.now().isoformat(),
            "query": query,
            "timestamp": timestamp,
            "total_findings": len(routed_findings),
            "summary": briefing['executive_summary'],
            "document_metadata": {
                "document_name": routed_findings[0].document_name if routed_findings else "Unknown",
                "analysis_timestamp": datetime.now().isoformat(),
                "gemini_model": "gemini-2.5-pro",
                "ebm_training": "LEDGAR 1200 samples",
                "confidence_calibration": "Uncalibrated - will adjust after 10+ pilot analyses"
            },
            "findings": findings_detail
        }

        path = f"{output_dir}/audit_report_{timestamp}.json"
        with open(path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"[L9] ✓ Audit JSON: {path}")

    def _generate_audit_html(self, query, routed_findings, briefing, retrieval_result, risk_scores, output_dir, timestamp):
        doc_name = routed_findings[0].document_name if routed_findings else "Unknown"
        total = len(routed_findings)
        high = sum(1 for f in routed_findings if f.risk_level == 'HIGH')
        medium = sum(1 for f in routed_findings if f.risk_level == 'MEDIUM')
        low = sum(1 for f in routed_findings if f.risk_level == 'LOW')
        date_str = datetime.now().strftime('%B %-d, %Y')

        def risk_color(level):
            if level == 'HIGH': return '#991f1f'
            if level == 'MEDIUM': return '#854f0b'
            return '#27500a'

        def risk_bg(level):
            if level == 'HIGH': return '#fef2f2'
            if level == 'MEDIUM': return '#fffbeb'
            return '#f0fdf4'

        def route_label(r):
            if r == 'SENIOR_PARTNER_ESCALATION': return 'Senior Partner Escalation'
            if r == 'ANALYST_REVIEW': return 'Analyst Review'
            return 'Auto Approve'

        def route_color(r):
            if r == 'SENIOR_PARTNER_ESCALATION': return '#991f1f'
            if r == 'ANALYST_REVIEW': return '#854f0b'
            return '#27500a'

        def route_bg(r):
            if r == 'SENIOR_PARTNER_ESCALATION': return '#fef2f2'
            if r == 'ANALYST_REVIEW': return '#fffbeb'
            return '#f0fdf4'

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Verilence Audit Report — {doc_name}</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'DM Sans',sans-serif;background:#fff;color:#1a1d23;font-size:13px}}
.page{{width:100%;min-height:100vh;padding:48px 60px;page-break-after:always;position:relative;border-bottom:1px solid #e5e7eb}}
.page:last-child{{page-break-after:auto;border-bottom:none}}
.page-header{{display:flex;align-items:center;justify-content:space-between;padding-bottom:20px;border-bottom:1px solid #e5e7eb;margin-bottom:32px}}
.logo{{font-family:'Playfair Display',serif;font-size:16px;font-weight:900;letter-spacing:-0.01em}}
.logo span{{color:#1a5eb8}}
.logo-tag{{font-family:'DM Mono',monospace;font-size:9px;color:#9ca3af;letter-spacing:0.12em;margin-left:6px;border:1px solid #e5e7eb;padding:1px 5px;border-radius:2px}}
.page-meta{{font-family:'DM Mono',monospace;font-size:9px;color:#9ca3af;letter-spacing:0.08em;text-align:right}}
.cover-content{{display:flex;flex-direction:column;justify-content:center;min-height:80vh}}
.cover-eyebrow{{font-family:'DM Mono',monospace;font-size:9px;color:#1a5eb8;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:16px}}
.cover-title{{font-family:'Playfair Display',serif;font-size:36px;font-weight:900;line-height:1.15;color:#1a1d23;margin-bottom:8px;letter-spacing:-0.02em}}
.cover-title span{{color:#1a5eb8}}
.cover-doc{{font-size:13px;color:#6b7280;margin-bottom:40px;font-family:'DM Mono',monospace}}
.cover-kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:#e5e7eb;border:1px solid #e5e7eb;border-radius:6px;overflow:hidden;margin-bottom:40px}}
.cover-kpi{{background:#fff;padding:20px 24px}}
.kpi-label{{font-family:'DM Mono',monospace;font-size:9px;color:#9ca3af;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px}}
.kpi-val{{font-family:'Playfair Display',serif;font-size:28px;font-weight:700;line-height:1}}
.kpi-sub{{font-size:11px;color:#9ca3af;margin-top:4px}}
.cover-meta{{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;padding-top:32px;border-top:1px solid #e5e7eb}}
.meta-item{{}}
.meta-label{{font-family:'DM Mono',monospace;font-size:9px;color:#9ca3af;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:4px}}
.meta-val{{font-size:12px;color:#1a1d23;font-weight:500}}
.section-label{{font-family:'DM Mono',monospace;font-size:9px;color:#9ca3af;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:20px;padding-bottom:8px;border-bottom:1px solid #e5e7eb}}
.toc-row{{display:flex;align-items:center;padding:10px 0;border-bottom:1px solid #f3f4f6}}
.toc-num{{font-family:'DM Mono',monospace;font-size:10px;color:#9ca3af;width:24px;flex-shrink:0}}
.toc-title{{flex:1;font-size:12px;color:#1a1d23;font-weight:500}}
.toc-risk{{font-family:'DM Mono',monospace;font-size:9px;padding:2px 8px;border-radius:3px;margin-right:8px}}
.toc-route{{font-family:'DM Mono',monospace;font-size:9px;padding:2px 8px;border-radius:3px}}
.finding-num{{font-family:'DM Mono',monospace;font-size:10px;color:#9ca3af;margin-bottom:4px}}
.finding-title{{font-family:'Playfair Display',serif;font-size:22px;font-weight:700;color:#1a1d23;line-height:1.2;margin-bottom:20px;letter-spacing:-0.01em}}
.badges{{display:flex;align-items:center;gap:8px;margin-bottom:28px}}
.badge{{font-family:'DM Mono',monospace;font-size:9px;padding:4px 10px;border-radius:3px;letter-spacing:0.06em}}
.divider{{height:1px;background:#e5e7eb;margin:24px 0}}
.two-col{{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-bottom:24px}}
.field-label{{font-family:'DM Mono',monospace;font-size:9px;color:#9ca3af;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px}}
.section-quote{{background:#f7f8fa;border-left:2px solid #1a5eb8;padding:10px 12px;font-size:11px;color:#374151;line-height:1.6;border-radius:0 4px 4px 0;margin-bottom:8px}}
.field-body{{font-size:12px;color:#374151;line-height:1.7}}
.math-panel{{background:#f7f8fa;border:1px solid #e5e7eb;border-radius:6px;padding:20px;margin-bottom:24px}}
.math-label{{font-family:'DM Mono',monospace;font-size:9px;color:#9ca3af;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:12px}}
table{{width:100%;border-collapse:collapse;font-size:11px}}
thead th{{font-family:'DM Mono',monospace;font-size:9px;font-weight:500;color:#9ca3af;letter-spacing:0.08em;text-transform:uppercase;padding:6px 10px;text-align:left;border-bottom:1px solid #e5e7eb}}
tbody td{{padding:8px 10px;color:#374151;border-bottom:1px solid #f3f4f6;vertical-align:top}}
tbody tr:last-child td{{border-bottom:none}}
.total-row td{{font-weight:500;color:#1a1d23;background:#f0f6ff;border-top:1px solid #dbeafe}}
.signal-val{{color:#1a5eb8;font-weight:500;font-family:'DM Mono',monospace}}
.risk-cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:16px}}
.risk-card{{background:#fff;border:1px solid #e5e7eb;border-radius:4px;padding:10px 12px}}
.risk-card-label{{font-family:'DM Mono',monospace;font-size:9px;color:#9ca3af;letter-spacing:0.08em;margin-bottom:4px}}
.risk-card-val{{font-size:16px;font-weight:500;color:#1a1d23;font-family:'Playfair Display',serif}}
.routing-box{{display:flex;align-items:center;justify-content:space-between;background:#f7f8fa;border:1px solid #e5e7eb;border-radius:4px;padding:10px 14px;margin-top:12px}}
.routing-label{{font-family:'DM Mono',monospace;font-size:9px;color:#9ca3af;letter-spacing:0.08em}}
.calib{{background:#f0f6ff;border:1px solid #dbeafe;border-radius:4px;padding:10px 14px;margin-top:12px;font-size:10px;color:#6b7280;line-height:1.6}}
.calib-lbl{{font-family:'DM Mono',monospace;font-size:9px;color:#1a5eb8;letter-spacing:0.08em;margin-bottom:2px;font-weight:500}}
.page-footer{{position:absolute;bottom:24px;left:60px;right:60px;display:flex;justify-content:space-between;font-family:'DM Mono',monospace;font-size:9px;color:#d1d5db}}
@media print{{
  .page{{page-break-after:always;border:none}}
  .page:last-child{{page-break-after:auto}}
  body{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
}}
</style>
</head>
<body>
"""

        # PAGE 1: COVER
        html += f"""
<div class="page">
  <div class="page-header">
    <div>
      <span class="logo">VERI<span>LENCE</span></span>
      <span class="logo-tag">GLASS BOX AI</span>
    </div>
    <div class="page-meta">CONFIDENTIAL AUDIT REPORT<br>VER-{timestamp}</div>
  </div>

  <div class="cover-content">
    <div class="cover-eyebrow">Contradiction Detection Report</div>
    <div class="cover-title">Glass Box<br><span>Audit Report</span></div>
    <div class="cover-doc">{doc_name}</div>

    <div class="cover-kpis">
      <div class="cover-kpi">
        <div class="kpi-label">Total Findings</div>
        <div class="kpi-val">{total}</div>
        <div class="kpi-sub">Contradictions detected</div>
      </div>
      <div class="cover-kpi">
        <div class="kpi-label">High Risk</div>
        <div class="kpi-val" style="color:#991f1f">{high}</div>
        <div class="kpi-sub">Senior partner escalation</div>
      </div>
      <div class="cover-kpi">
        <div class="kpi-label">Medium Risk</div>
        <div class="kpi-val" style="color:#854f0b">{medium}</div>
        <div class="kpi-sub">Analyst review required</div>
      </div>
      <div class="cover-kpi">
        <div class="kpi-label">Low Risk</div>
        <div class="kpi-val" style="color:#27500a">{low}</div>
        <div class="kpi-sub">Auto-approve eligible</div>
      </div>
    </div>

    <div class="cover-meta">
      <div class="meta-item">
        <div class="meta-label">Report ID</div>
        <div class="meta-val">VER-{timestamp}</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Analysis Date</div>
        <div class="meta-val">{date_str}</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Analysis Method</div>
        <div class="meta-val">EBM + Gemini 2.5 Pro</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">EBM Training Data</div>
        <div class="meta-val">LEDGAR — 1,200 contract clauses</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Calibration Status</div>
        <div class="meta-val">Uncalibrated — pre-pilot</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Prepared By</div>
        <div class="meta-val">Verilence LLC · Richmond, VA</div>
      </div>
    </div>
  </div>

  <div class="page-footer">
    <span>VERILENCE LLC · Glass Box AI · Richmond, VA</span>
    <span>Proprietary · Not Legal Advice · Page 1</span>
  </div>
</div>
"""

        # PAGE 2: TABLE OF CONTENTS
        html += f"""
<div class="page">
  <div class="page-header">
    <div>
      <span class="logo">VERI<span>LENCE</span></span>
      <span class="logo-tag">GLASS BOX AI</span>
    </div>
    <div class="page-meta">VER-{timestamp} · {date_str}</div>
  </div>

  <div class="section-label">Table of Contents</div>

  <div class="toc-row" style="margin-bottom:8px">
    <div class="toc-num"></div>
    <div class="toc-title" style="font-family:'DM Mono',monospace;font-size:9px;color:#9ca3af;letter-spacing:0.08em;text-transform:uppercase">Finding</div>
    <div style="font-family:'DM Mono',monospace;font-size:9px;color:#9ca3af;letter-spacing:0.08em;text-transform:uppercase;margin-right:8px">Risk</div>
    <div style="font-family:'DM Mono',monospace;font-size:9px;color:#9ca3af;letter-spacing:0.08em;text-transform:uppercase">Routing</div>
  </div>
"""
        for i, finding in enumerate(routed_findings):
            conf, _, _, _ = self._calc_confidence(finding, retrieval_result)
            html += f"""
  <div class="toc-row">
    <div class="toc-num">{i+1}</div>
    <div class="toc-title">{getattr(finding, 'title', 'Finding')}</div>
    <div class="toc-risk" style="background:{risk_bg(finding.risk_level)};color:{risk_color(finding.risk_level)}">{finding.risk_level}</div>
    <div class="toc-route" style="background:{route_bg(finding.routing_action)};color:{route_color(finding.routing_action)}">{route_label(finding.routing_action)}</div>
  </div>
"""

        html += f"""
  <div style="margin-top:40px;padding:20px;background:#f7f8fa;border-radius:6px;border:1px solid #e5e7eb">
    <div class="field-label" style="margin-bottom:8px">About This Report</div>
    <div class="field-body">This report was generated by the Verilence Glass Box contradiction detection engine. Every finding includes a complete mathematical audit trail showing exactly how risk and confidence were calculated. All findings should be reviewed by qualified legal counsel before any action is taken. This report does not constitute legal advice.</div>
  </div>

  <div class="page-footer">
    <span>VERILENCE LLC · Glass Box AI · Richmond, VA</span>
    <span>Proprietary · Not Legal Advice · Page 2</span>
  </div>
</div>
"""

        # ONE PAGE PER FINDING
        for i, finding in enumerate(routed_findings):
            conf, clarity, gemini_sig, chunk = self._calc_confidence(finding, retrieval_result)
            conf_capped = min(conf, 89.0)
            title = getattr(finding, 'title', 'Finding')
            s1 = getattr(finding, 'section_1', '')
            s2 = getattr(finding, 'section_2', '')
            problem = getattr(finding, 'why_problem', getattr(finding, 'explanation', ''))
            financial_impact = getattr(finding, 'financial_impact', 'Unknown')
            routing = finding.routing_action
            risk_level = finding.risk_level
            page_num = i + 3

            html += f"""
<div class="page">
  <div class="page-header">
    <div>
      <span class="logo">VERI<span>LENCE</span></span>
      <span class="logo-tag">GLASS BOX AI</span>
    </div>
    <div class="page-meta">VER-{timestamp} · Finding {i+1} of {total}</div>
  </div>

  <div class="finding-num">Finding {i+1} of {total}</div>
  <div class="finding-title">{title}</div>

  <div class="badges">
    <span class="badge" style="background:{risk_bg(risk_level)};color:{risk_color(risk_level)}">Risk Score: {finding.risk_score:.2f} · {risk_level}</span>
    <span class="badge" style="background:#f0f6ff;color:#1a5eb8">Confidence: {conf_capped:.1f}%</span>
    <span class="badge" style="background:{route_bg(routing)};color:{route_color(routing)}">{route_label(routing)}</span>
  </div>

  <div class="divider"></div>

  <div class="two-col">
    <div>
      <div class="field-label">Section 1</div>
      <div class="section-quote">{s1}</div>
      <div class="field-label" style="margin-top:12px">Section 2</div>
      <div class="section-quote">{s2}</div>
    </div>
    <div>
      <div class="field-label">Why It Matters</div>
      <div class="field-body" style="margin-bottom:16px">{problem}</div>
      <div class="field-label">Financial Impact</div>
      <div class="field-body">{financial_impact}</div>
    </div>
  </div>

  <div class="divider"></div>

  <div class="math-panel">
    <div class="math-label">Confidence Calculation — 3 Independent Signals</div>
    <table>
      <thead>
        <tr>
          <th>Signal</th>
          <th>What it measures</th>
          <th>Strength</th>
          <th>Weight</th>
          <th>Impact</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Text clarity</td>
          <td>How unambiguous is the contradiction in the document?</td>
          <td class="signal-val">{clarity:.1f}%</td>
          <td>35%</td>
          <td class="signal-val">+{clarity * 0.35:.1f}%</td>
        </tr>
        <tr>
          <td>Gemini 2.5 Pro</td>
          <td>LLM detection confidence for this finding</td>
          <td class="signal-val">{gemini_sig:.1f}%</td>
          <td>35%</td>
          <td class="signal-val">+{gemini_sig * 0.35:.1f}%</td>
        </tr>
        <tr>
          <td>Chunk quality</td>
          <td>Specificity of retrieved document sections</td>
          <td class="signal-val">{chunk:.1f}%</td>
          <td>30%</td>
          <td class="signal-val">+{chunk * 0.30:.1f}%</td>
        </tr>
        <tr class="total-row">
          <td colspan="4"><strong>Total confidence</strong></td>
          <td class="signal-val"><strong>{conf_capped:.1f}%</strong></td>
        </tr>
      </tbody>
    </table>

    <div class="risk-cards">
      <div class="risk-card">
        <div class="risk-card-label">EBM Risk Score</div>
        <div class="risk-card-val">{finding.risk_score:.2f}</div>
      </div>
      <div class="risk-card">
        <div class="risk-card-label">Confidence</div>
        <div class="risk-card-val">{conf_capped:.1f}%</div>
      </div>
      <div class="risk-card">
        <div class="risk-card-label">Risk Level</div>
        <div class="risk-card-val" style="color:{risk_color(risk_level)}">{risk_level}</div>
      </div>
    </div>

    <div class="routing-box">
      <span class="routing-label">ROUTING DECISION</span>
      <span class="badge" style="background:{route_bg(routing)};color:{route_color(routing)}">{route_label(routing)}</span>
    </div>

    <div class="calib">
      <div class="calib-lbl">Calibration Status</div>
      Uncalibrated — weights based on initial configuration (35/35/30). EBM trained on 1,200 LEDGAR contract clauses. Scores will improve after pilot analyses with operator feedback.
    </div>
  </div>

  <div class="page-footer">
    <span>VERILENCE LLC · Glass Box AI · Richmond, VA</span>
    <span>Proprietary · Not Legal Advice · Page {page_num}</span>
  </div>
</div>
"""

        # FINAL PAGE: METHODOLOGY
        html += f"""
<div class="page">
  <div class="page-header">
    <div>
      <span class="logo">VERI<span>LENCE</span></span>
      <span class="logo-tag">GLASS BOX AI</span>
    </div>
    <div class="page-meta">VER-{timestamp} · Methodology</div>
  </div>

  <div class="section-label">Methodology & Glass Box Framework</div>

  <div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;margin-bottom:32px">
    <div>
      <div class="field-label" style="margin-bottom:8px">Analysis Engine</div>
      <div class="field-body">Verilence uses a 9-layer pipeline combining Legal-BERT embeddings, Qdrant vector search, and an Explainable Boosting Machine (EBM) trained on 1,200 real contract clauses from the LEDGAR dataset. Google Gemini 2.5 Pro synthesizes findings into plain-language explanations.</div>
    </div>
    <div>
      <div class="field-label" style="margin-bottom:8px">Why Glass Box</div>
      <div class="field-body">Unlike black box AI, every Verilence finding includes a complete mathematical audit trail. The confidence formula is disclosed, the training data is documented, and the routing logic is fully specified. Any finding can be independently verified by a lawyer or auditor.</div>
    </div>
  </div>

  <div class="math-panel" style="margin-bottom:24px">
    <div class="math-label">Confidence Formula</div>
    <table>
      <thead><tr><th>Signal</th><th>What it measures</th><th>Weight</th></tr></thead>
      <tbody>
        <tr><td>Text clarity</td><td>Distance of risk score from ambiguous midpoint — clear contradictions score higher</td><td class="signal-val">35%</td></tr>
        <tr><td>Gemini 2.5 Pro</td><td>Raw confidence returned by Gemini for this specific finding</td><td class="signal-val">35%</td></tr>
        <tr><td>Chunk quality</td><td>Specificity of retrieved section quotes — longer quotes indicate better retrieval</td><td class="signal-val">30%</td></tr>
      </tbody>
    </table>
  </div>

  <div class="math-panel" style="margin-bottom:24px">
    <div class="math-label">Routing Decision Matrix</div>
    <table>
      <thead><tr><th>Risk Score</th><th>Confidence</th><th>Routing</th><th>Reasoning</th></tr></thead>
      <tbody>
        <tr><td style="color:#991f1f;font-weight:500">≥ 0.70 (High)</td><td>Any</td><td style="color:#991f1f;font-weight:500">Senior Partner Escalation</td><td>High financial exposure requires expert judgment</td></tr>
        <tr><td style="color:#854f0b;font-weight:500">0.40–0.69 (Medium)</td><td>&gt; 60%</td><td style="color:#854f0b;font-weight:500">Analyst Review</td><td>Medium risk with sufficient confidence for analyst</td></tr>
        <tr><td style="color:#27500a;font-weight:500">&lt; 0.40 (Low)</td><td>&gt; 85%</td><td style="color:#27500a;font-weight:500">Auto Approve</td><td>Low risk, high confidence — minimal review needed</td></tr>
      </tbody>
    </table>
  </div>

  <div style="padding:16px;background:#f7f8fa;border-radius:6px;border:1px solid #e5e7eb;font-size:11px;color:#6b7280;line-height:1.7">
    <strong style="color:#1a1d23;display:block;margin-bottom:4px">Important Disclosures</strong>
    This report was generated by an AI system and does not constitute legal advice. All findings should be reviewed by qualified legal counsel before any action is taken. Confidence scores are uncalibrated and based on initial weightings — they will improve as pilot data is collected. The EBM model was trained on general commercial contract data (LEDGAR) and has not yet been fine-tuned on O&G-specific JOA outcomes. Verilence LLC makes no representations about the accuracy or completeness of this analysis.
  </div>

  <div class="page-footer">
    <span>VERILENCE LLC · Glass Box AI · Richmond, VA</span>
    <span>Proprietary · Not Legal Advice · Page {total + 3}</span>
  </div>
</div>

</body>
</html>"""

        path = f"{output_dir}/audit_report_{timestamp}.html"
        with open(path, 'w') as f:
            f.write(html)
        print(f"[L9] ✓ Audit HTML: {path}")
