import json

def extract_features(original_clause, modified_clause, contradiction_type):
    """Extract 50+ features from a contradiction."""
    
    features = {
        # Lexical features (10)
        "word_overlap": len(set(original_clause.split()) & set(modified_clause.split())) / max(len(set(original_clause.split())), 1),
        "char_distance": abs(len(original_clause) - len(modified_clause)),
        "punctuation_change": abs(original_clause.count(',') - modified_clause.count(',')),
        "capitalization_change": sum(1 for a, b in zip(original_clause, modified_clause) if a.isupper() != b.isupper()),
        "quote_change": abs(original_clause.count('"') - modified_clause.count('"')),
        "number_change": abs(sum(c.isdigit() for c in original_clause) - sum(c.isdigit() for c in modified_clause)),
        "sentence_count_original": original_clause.count('.'),
        "sentence_count_modified": modified_clause.count('.'),
        "keyword_count_original": sum(1 for kw in ["operator", "cost", "liability", "obligation"] if kw.lower() in original_clause.lower()),
        "keyword_count_modified": sum(1 for kw in ["operator", "cost", "liability", "obligation"] if kw.lower() in modified_clause.lower()),
        
        # Temporal features (8)
        "date_reference_change": abs(original_clause.count("20") - modified_clause.count("20")),
        "temporal_keyword_change": abs(sum(1 for kw in ["year", "month", "day", "period"] if kw in original_clause.lower()) - sum(1 for kw in ["year", "month", "day", "period"] if kw in modified_clause.lower())),
        "percent_change": abs(original_clause.count("%") - modified_clause.count("%")),
        "duration_reference": 1 if any(kw in modified_clause.lower() for kw in ["initial phase", "interim period", "phase one"]) else 0,
        "timing_ambiguity": 1 if "timing" in modified_clause.lower() else 0,
        "deadline_shift": 1 if any(kw in modified_clause.lower() for kw in ["before", "after", "upon", "within"]) else 0,
        "effective_date_change": 1 if "effective" in modified_clause.lower() else 0,
        "retroactive_reference": 1 if "retroactive" in modified_clause.lower() else 0,
        
        # Financial features (8)
        "percentage_value_change": 1 if any(c.isdigit() for c in original_clause) and any(c.isdigit() for c in modified_clause) else 0,
        "currency_symbol_change": abs(original_clause.count("$") - modified_clause.count("$")),
        "cost_allocation_change": 1 if "cost" in modified_clause.lower() else 0,
        "liability_shift": 1 if "liable" in modified_clause.lower() else 0,
        "payment_term_change": 1 if any(kw in modified_clause.lower() for kw in ["payment", "remuneration", "compensation"]) else 0,
        "interest_rate_reference": 1 if any(kw in modified_clause.lower() for kw in ["interest", "rate", "return"]) else 0,
        "budget_impact": 1 if any(kw in modified_clause.lower() for kw in ["budget", "capital", "expenditure"]) else 0,
        "discount_or_premium": 1 if any(kw in modified_clause.lower() for kw in ["discount", "premium", "adjustment"]) else 0,
        
        # Structural features (10)
        "clause_reference_change": abs(original_clause.count("Section") - modified_clause.count("Section")),
        "party_reference_change": abs(sum(1 for party in ["Operator", "Non-Operator", "Co-Owner"] if party in original_clause) - sum(1 for party in ["Operator", "Non-Operator", "Co-Owner"] if party in modified_clause)),
        "scope_qualifier_change": 1 if any(kw in modified_clause.lower() for kw in ["initial", "except", "excluding", "limited"]) else 0,
        "definition_reference": 1 if '"' in modified_clause else 0,
        "cross_reference_added": 1 if "see" in modified_clause.lower() or "refer" in modified_clause.lower() else 0,
        "parenthetical_addition": 1 if "(" in modified_clause and "(" not in original_clause else 0,
        "list_structure_change": abs(original_clause.count(";") - modified_clause.count(";")),
        "subsection_reference": 1 if any(f"({c})" in modified_clause for c in "abcdefghij") else 0,
        "obligation_shift": 1 if "shall" in modified_clause.lower() else 0,
        "discretion_change": 1 if any(kw in modified_clause.lower() for kw in ["may", "discretion", "election"]) else 0,
        
        # Semantic features (14)
        "contradiction_type_encoded": hash(contradiction_type) % 100,
        "liability_mention": 1 if any(kw in modified_clause.lower() for kw in ["liable", "liability", "indemnify"]) else 0,
        "risk_allocation": 1 if any(kw in modified_clause.lower() for kw in ["risk", "hazard", "danger"]) else 0,
        "indemnification": 1 if "indemnif" in modified_clause.lower() else 0,
        "force_majeure": 1 if "force majeure" in modified_clause.lower() else 0,
        "dispute_resolution": 1 if any(kw in modified_clause.lower() for kw in ["arbitration", "dispute", "resolution"]) else 0,
        "confidentiality": 1 if "confidential" in modified_clause.lower() else 0,
        "termination_clause": 1 if "terminat" in modified_clause.lower() else 0,
        "amendment_scope": 1 if "amend" in modified_clause.lower() else 0,
        "waiver_reference": 1 if "waiv" in modified_clause.lower() else 0,
        "counterparty_obligation": 1 if any(kw in modified_clause.lower() for kw in ["counterparty", "other party", "co-owner"]) else 0,
        "condition_precedent": 1 if "unless" in modified_clause.lower() or "except" in modified_clause.lower() else 0,
        "exclusivity": 1 if "exclusive" in modified_clause.lower() else 0,
        "most_favored_nation": 1 if "most favored" in modified_clause.lower() else 0,
    }
    
    return features

if __name__ == "__main__":
    original = "The Operator shall be responsible for all costs."
    modified = "The Operator may be responsible for costs during the initial phase."
    features = extract_features(original, modified, "cost_allocation_change")
    print(json.dumps(features, indent=2))
    print(f"Total features: {len(features)}")
