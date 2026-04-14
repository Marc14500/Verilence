#!/usr/bin/env python3

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from forger import GeminiForger
from critic import GeminiCritic
from feature_extraction import extract_features
from config import (
    GEMINI_API_KEY, DATA_DIR, VARIANTS_DIR, ACCEPTED_DIR, 
    FEATURES_DIR, MODELS_DIR, LOGS_DIR
)

# Ensure directories exist
for d in [VARIANTS_DIR, ACCEPTED_DIR, FEATURES_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def load_real_joa_clauses():
    """Extract real high-risk clauses from New Dominion JOA."""
    joa_clauses = {
        "joa_001": {
            "id": "joa_001",
            "name": "New Dominion JOA - Luther Prospect",
            "clauses": [
                {
                    "id": "joa_001_clause_001",
                    "section": "III.B - Interests of Parties in Costs and Production",
                    "text": "Unless changed by other provisions, all costs and liabilities incurred in operations under this agreement shall be borne and paid, and all equipment and materials acquired in operations on the Contract Area shall be owned, by the parties as their interests are set forth in Exhibit A. In the same manner, the parties shall also own all production of Oil and Gas from the Contract Area subject, however, to the payment of royalties and other burdens on production as described in this agreement."
                },
                {
                    "id": "joa_001_clause_002",
                    "section": "VI.B.2 - Operations by Less than All Parties",
                    "text": "If any Party to whom a notice is delivered elects not to participate in the proposed operation, the relinquishment shall be effective until the proceeds of the sale of the share, calculated at the well, or market value of it, if the share is not sold (after deducting applicable ad valorem, production, severance and excise taxes, royalty, overriding royalty, and other interests) shall equal 500% of each of the Non-Consenting Parties' share of the cost of any newly acquired surface equipment beyond the wellhead connections plus 100% of each of the Non-Consenting Parties' share of the cost of operating the well commencing with first production."
                },
                {
                    "id": "joa_001_clause_003",
                    "section": "VII.B - Liens and Security Interests",
                    "text": "Each Party grants to the other parties to this agreement a lien on any interest it now owns or later acquires in Oil and Gas Leases and Oil and Gas Interests in the Contract Area, and a security interest in any interest it now owns or later acquires in the personal property and fixtures on or used or obtained for use in connection with any interest, to secure performance of all of its obligations under this agreement including payment of expense, interest and fees, the proper disbursement of all monies paid under this agreement, the assignment or relinquishment of interest in Oil and Gas Leases as required hereunder, and the proper performance of operations under this agreement."
                },
                {
                    "id": "joa_001_clause_004",
                    "section": "Article XVI.E - Saltwater Disposal and Infrastructure Costs",
                    "text": "Each Party shall prepay to NDL its Proportionate Share of the turnkey saltwater disposal costs attributable to each New Well in the amount of Four Hundred Thousand dollars ($400,000.00). This payment is a one-time fee for each New Well that, upon payment, entitles each Party to access to NDL's saltwater disposal system for the life of the New Well. NDL reserves the right to increase this amount in increments of Fifty Thousand Dollars ($50,000.00) per well per year in the event of increased costs of drilling equipment and services on saltwater disposal wells."
                },
                {
                    "id": "joa_001_clause_005",
                    "section": "XVI.I - Acquisitions within the Contract Area",
                    "text": "In the event NDL proposes to acquire any existing producing wells and associated leasehold from third parties within the Contract Area, NDL shall provide the Parties with notice of the acquisition. Each Party shall have the right to acquire its Percentage Interest of the Purchased Producing Well(s) for an amount equal to NDL's actual cost multiplied by such Party's Percentage Interest plus fifteen percent (15%) of NDL's actual cost. In the event a Party elects not to acquire its Percentage Interest, the Party shall forfeit its right to participate in the next nine (9) New Wells proposed to be drilled in drilling and spacing units adjacent to the Purchased Producing Well(s)."
                }
            ]
        }
    }
    return joa_clauses

def process_joas():
    """Main pipeline: Forger -> Critic -> Features -> Save."""
    
    print("\n" + "="*70)
    print("ADVERSARIAL LAB - GEMINI PIPELINE (REAL JOA DATA)")
    print("="*70)
    
    if not GEMINI_API_KEY:
        print("✗ GEMINI_API_KEY not set. Export it: export GEMINI_API_KEY='your-key'")
        sys.exit(1)
    
    # Initialize
    forger = GeminiForger(GEMINI_API_KEY)
    critic = GeminiCritic(GEMINI_API_KEY)
    
    # Load real JOA clauses
    joas = load_real_joa_clauses()
    print(f"\n✓ Loaded {len(joas)} JOAs from New Dominion Luther Prospect")
    
    all_variants = []
    all_verdicts = []
    all_accepted = []
    all_features = []
    
    # Process each JOA
    for joa_id, joa_data in joas.items():
        print(f"\n{'='*70}")
        print(f"Processing {joa_id} ({len(joa_data['clauses'])} clauses)")
        print(f"{'='*70}")
        
        for clause in joa_data['clauses']:
            clause_id = clause['id']
            clause_text = clause['text']
            section = clause['section']
            
            print(f"\n[{section}]")
            print(f"Clause ID: {clause_id}")
            print(f"Text: {clause_text[:80]}...")
            
            # DAY 1: FORGER generates variants
            print(f"\n  → [Forger] Generating 5 variants...")
            variants = forger.generate(clause_text, clause_id=clause_id)
            
            if not variants:
                print(f"    ✗ Failed to generate variants")
                continue
            
            all_variants.extend(variants)
            
            # Save variants to disk
            variants_file = VARIANTS_DIR / f"{clause_id}_variants.json"
            with open(variants_file, 'w') as f:
                json.dump(variants, f, indent=2)
            print(f"    ✓ Saved {len(variants)} variants")
            
            # DAY 2: CRITIC evaluates variants
            print(f"  → [Critic] Evaluating sneakiness...")
            verdicts = critic.evaluate(clause_text, variants)
            
            if not verdicts:
                print(f"    ✗ Failed to evaluate variants")
                continue
            
            all_verdicts.extend(verdicts)
            
            # Save verdicts
            verdicts_file = ACCEPTED_DIR / f"{clause_id}_verdicts.json"
            with open(verdicts_file, 'w') as f:
                json.dump(verdicts, f, indent=2)
            
            # Filter accepted variants
            accepted = [v for v in verdicts if v.get('verdict') == 'ACCEPT']
            all_accepted.extend(accepted)
            print(f"    ✓ Accepted {len(accepted)}/{len(verdicts)} variants")
            
            # DAY 3: FEATURE EXTRACTION
            print(f"  → [Features] Extracting 50+ features...")
            for variant in variants:
                for verdict in verdicts:
                    if verdict['variant_id'] == variant['variant_id']:
                        if verdict.get('verdict') == 'ACCEPT':
                            features = extract_features(
                                variant['original_clause'],
                                variant['modified_clause'],
                                variant['contradiction_type']
                            )
                            features['clause_id'] = clause_id
                            features['section'] = section
                            features['variant_id'] = variant['variant_id']
                            features['verdict'] = verdict['verdict']
                            all_features.append(features)
            
            print(f"    ✓ Extracted features for accepted variants")
    
    # Save summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_joas": len(joas),
        "total_clauses": sum(len(joa['clauses']) for joa in joas.values()),
        "total_variants_generated": len(all_variants),
        "total_verdicts": len(all_verdicts),
        "total_accepted": len(all_accepted),
        "acceptance_rate": f"{100 * len(all_accepted) / len(all_verdicts):.1f}%" if all_verdicts else "N/A",
        "total_features_extracted": len(all_features),
    }
    
    summary_file = LOGS_DIR / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    for key, value in summary.items():
        print(f"  {key}: {value}")
    print("="*70)
    
    # Export accepted contradictions for data licensing
    export_file = DATA_DIR / "accepted_contradictions.json"
    with open(export_file, 'w') as f:
        json.dump(all_accepted, f, indent=2)
    print(f"\n✓ Exported {len(all_accepted)} accepted contradictions to {export_file.name}")
    
    # Export features for EBM training
    features_export = DATA_DIR / "features_for_ebm.json"
    with open(features_export, 'w') as f:
        json.dump(all_features, f, indent=2)
    print(f"✓ Exported {len(all_features)} features to {features_export.name}")
    
    print("\n✓ Lab MVP complete!")
    print("\nNext steps:")
    print("  1. Review lab/data/accepted_contradictions.json")
    print("  2. Commit and push to GitHub")
    print("  3. Show investors: 'Here's the Adversarial Lab working on real O&G JOA clauses'")

if __name__ == "__main__":
    process_joas()
