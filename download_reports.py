#!/usr/bin/env python3
"""
Auto-download latest audit reports
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

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
    for report in json_reports[:5]:  # Last 5 reports
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
    
    # Open in browser if on macOS/Linux with xdg-open
    if copied_files:
        latest_html = [f for f in copied_files if f.suffix == '.html']
        if latest_html:
            html_path = latest_html[0]
            
            # Try to open in default browser
            try:
                if os.uname().sysname == "Darwin":  # macOS
                    os.system(f"open '{html_path}'")
                    print(f"[DOWNLOAD] Opening in browser: {html_path}")
                elif os.uname().sysname == "Linux":
                    os.system(f"xdg-open '{html_path}' 2>/dev/null &")
                    print(f"[DOWNLOAD] Opening in browser: {html_path}")
            except:
                print(f"[DOWNLOAD] To view: {html_path}")
    
    return copied_files

if __name__ == "__main__":
    download_latest_reports()
