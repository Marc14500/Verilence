#!/usr/bin/env python3
from layer8_reporting import ReportGenerator
from download_reports import download_latest_reports
from pathlib import Path

def analyze_deal_package():
    print("\n" + "="*70)
    print("VERILENCE - CHEVRON-HESS DEAL ANALYSIS")
    print("="*70)
    
    print(f"\n[INIT] Loading Chevron-Hess deal package...")
    gen = ReportGenerator(data_source="demo_data/oil_gas")
    
    queries = [
        "indemnification cap $500 million vs uncapped liability",
        "operational control 30 days vs 180 days",
        "environmental liability $100 million vs unlimited",
        "insurance $50 million vs indemnification $500 million",
        "abandonment buyer assumes all vs seller cap $50 million",
        "seller insurance vs uncapped liability"
    ]
    
    print("\n" + "="*70)
    print("DETECTING CONTRADICTIONS")
    print("="*70 + "\n")
    
    for i, query in enumerate(queries, 1):
        print(f"[{i}/{len(queries)}] {query}...", end=" ", flush=True)
        try:
            gen.generate_report(query)
            print("✓")
        except Exception as e:
            print(f"✗")
    
    print("\n" + "="*70)
    print("DOWNLOADING REPORTS")
    print("="*70)
    reports = download_latest_reports()
    
    print(f"\n✓ Generated {len(reports)} audit-ready reports")
    print(f"✓ Auto-downloaded to ~/Downloads/Verilence_Reports/")

if __name__ == "__main__":
    analyze_deal_package()
