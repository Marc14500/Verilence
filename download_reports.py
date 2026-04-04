#!/usr/bin/env python3
"""Auto-download latest audit reports"""

import os
import shutil
from pathlib import Path

def download_latest_reports(output_dir="output", local_dir=None):
    """Download latest audit reports to local machine"""
    
    if local_dir is None:
        local_dir = str(Path.home() / "Downloads" / "Verilence_Reports")
    
    Path(local_dir).mkdir(parents=True, exist_ok=True)
    
    print(f"\n[DOWNLOAD] Copying reports to: {local_dir}")
    
    # Find all audit reports
    json_reports = sorted(Path(output_dir).glob("audit_report_*.json"), 
                         key=lambda x: x.stat().st_mtime, reverse=True)
    html_reports = sorted(Path(output_dir).glob("audit_report_*.html"), 
                         key=lambda x: x.stat().st_mtime, reverse=True)
    
    copied_files = []
    
    # Copy JSON reports
    for report in json_reports[:5]:
        dest = Path(local_dir) / report.name
        shutil.copy2(report, dest)
        copied_files.append(dest)
        print(f"  ✓ {report.name}")
    
    # Copy HTML reports
    for report in html_reports[:5]:
        dest = Path(local_dir) / report.name
        shutil.copy2(report, dest)
        copied_files.append(dest)
        print(f"  ✓ {report.name}")
    
    print(f"\n[DOWNLOAD] ✓ {len(copied_files)} reports downloaded")
    print(f"[DOWNLOAD] Location: {local_dir}")
    
    # Show view command
    latest_html = [f for f in copied_files if f.suffix == '.html']
    if latest_html:
        print(f"\n[DOWNLOAD] View latest report:")
        print(f"  cat {latest_html[0]}")
    
    return copied_files

if __name__ == "__main__":
    download_latest_reports()

