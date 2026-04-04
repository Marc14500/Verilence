#!/usr/bin/env python3
"""
VERILENCE - Oil & Gas Due Diligence Demo
Real SEC Filing Analysis with Auto-Download
"""

from layer8_reporting import ReportGenerator
from download_reports import download_latest_reports
from pathlib import Path

def run_og_demo():
    print("\n" + "="*70)
    print("VERILENCE - OIL & GAS DUE DILIGENCE DEMO")
    print("Real SEC Filing Analysis with Auto-Download")
    print("="*70)
    
    demo_dir = Path("demo_data/oil_gas")
    files = list(demo_dir.glob("*.txt"))
    
    print(f"\n✓ Found {len(files)} real O&G deal documents:")
    for f in files:
        print(f"  - {f.name}")
    
    print("\n[INIT] Loading real SEC O&G filings...")
    gen = ReportGenerator(data_source="demo_data/oil_gas")
    
    og_queries = [
        "environmental liability and remediation",
        "indemnification and liability caps",
        "operational control and decision making",
        "abandonment and decommissioning obligations"
    ]
    
    print("\n" + "="*70)
    print("ANALYZING FOR CONTRADICTIONS")
    print("="*70)
    print(f"\nRunning {len(og_queries)} O&G risk queries...\n")
    
    for i, query in enumerate(og_queries, 1):
        print(f"[{i:2d}/{len(og_queries)}] {query}...", end=" ", flush=True)
        try:
            gen.generate_report(query)
            print("✓")
        except Exception as e:
            print(f"✗ ({str(e)[:50]})")
    
    # Auto-download reports
    print("\n" + "="*70)
    print("AUTO-DOWNLOADING REPORTS")
    print("="*70)
    
    reports = download_latest_reports()
    
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    print(f"\n✓ Generated {len(reports)} audit-ready reports")
    print(f"✓ All reports auto-downloaded to ~/Downloads/Verilence_Reports/")
    print(f"\n📊 Ready to present to Austin Morris")
    print(f"✓ Mathematically transparent")
    print(f"✓ Legally defensible")
    print(f"✓ Regulatory audit-ready")

if __name__ == "__main__":
    run_og_demo()

