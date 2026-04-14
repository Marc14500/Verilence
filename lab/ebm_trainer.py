import json
import numpy as np
from pathlib import Path
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from interpret.glassbox import ExplainableBoostingClassifier
import joblib
from config import DATA_DIR, MODELS_DIR, LOGS_DIR

def load_features_from_json(features_file):
    """Load extracted features from JSON."""
    with open(features_file, 'r') as f:
        features_list = json.load(f)
    
    if not features_list:
        print(f"✗ No features found in {features_file}")
        return None, None
    
    # Convert list of dicts to numpy array
    feature_names = list(features_list[0].keys())
    # Remove non-numeric columns
    feature_names = [f for f in feature_names if f not in ['clause_id', 'section', 'variant_id', 'verdict']]
    
    X = np.array([[f.get(name, 0) for name in feature_names] for f in features_list])
    # Labels: 1 if ACCEPT, 0 if REJECT
    y = np.array([1 if f.get('verdict') == 'ACCEPT' else 0 for f in features_list])
    
    print(f"✓ Loaded {len(features_list)} samples with {len(feature_names)} features")
    print(f"  Positive class (ACCEPT): {np.sum(y)}")
    print(f"  Negative class (REJECT): {len(y) - np.sum(y)}")
    
    return X, y, feature_names

def train_ebm_model(X, y, feature_names):
    """Train Explainable Boosting Machine."""
    
    print("\n[EBM Training]")
    print(f"  Training set size: {len(X)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"  Train: {len(X_train)}, Test: {len(X_test)}")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train EBM
    print("  → Fitting EBM model...")
    ebm = ExplainableBoostingClassifier(
        random_state=42,
        max_rounds=100,
        learning_rate=0.01,
        validation_size=0.15
    )
    
    ebm.fit(X_train_scaled, y_train)
    
    # Evaluate
    train_score = ebm.score(X_train_scaled, y_train)
    test_score = ebm.score(X_test_scaled, y_test)
    
    print(f"  ✓ Training accuracy: {train_score:.3f}")
    print(f"  ✓ Test accuracy (holdout): {test_score:.3f}")
    
    # Get feature importance
    feature_importance = list(zip(feature_names, ebm.feature_importances_))
    feature_importance.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n  Top 10 most important features:")
    for i, (name, importance) in enumerate(feature_importance[:10], 1):
        print(f"    {i}. {name}: {importance:.4f}")
    
    return ebm, scaler, train_score, test_score, feature_importance

def export_model(ebm, scaler, feature_names, model_version, train_score, test_score, feature_importance):
    """Export trained model and metadata."""
    
    # Save model
    model_file = MODELS_DIR / f"ebm_v{model_version}.pkl"
    joblib.dump(ebm, model_file)
    print(f"\n✓ Model saved to {model_file.name}")
    
    # Save scaler
    scaler_file = MODELS_DIR / f"scaler_v{model_version}.pkl"
    joblib.dump(scaler, scaler_file)
    print(f"✓ Scaler saved to {scaler_file.name}")
    
    # Save feature names
    features_file = MODELS_DIR / f"feature_names_v{model_version}.json"
    with open(features_file, 'w') as f:
        json.dump(feature_names, f, indent=2)
    print(f"✓ Feature names saved to {features_file.name}")
    
    # Save metadata
    metadata = {
        "version": model_version,
        "timestamp": datetime.now().isoformat(),
        "model_type": "ExplainableBoostingClassifier",
        "training_accuracy": float(train_score),
        "test_accuracy_holdout": float(test_score),
        "feature_count": len(feature_names),
        "top_features": [(name, float(importance)) for name, importance in feature_importance[:10]],
        "training_data_source": "Synthetic adversarial contradictions + real JOA clauses"
    }
    
    metadata_file = MODELS_DIR / f"ebm_v{model_version}_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Metadata saved to {metadata_file.name}")
    
    return metadata

def main():
    """End-to-end: Load features -> Train EBM -> Export."""
    
    print("\n" + "="*70)
    print("EBM TRAINING PIPELINE")
    print("="*70)
    
    # Load features
    features_file = DATA_DIR / "features_for_ebm.json"
    if not features_file.exists():
        print(f"✗ Features file not found: {features_file}")
        print("  Run main.py first to generate features")
        return
    
    X, y, feature_names = load_features_from_json(features_file)
    if X is None:
        return
    
    # Train EBM
    ebm, scaler, train_score, test_score, feature_importance = train_ebm_model(X, y, feature_names)
    
    # Export
    model_version = "1.0"
    metadata = export_model(ebm, scaler, feature_names, model_version, train_score, test_score, feature_importance)
    
    print("\n" + "="*70)
    print("EBM TRAINING COMPLETE")
    print("="*70)
    print(f"Model: ebm_v{model_version}.pkl")
    print(f"Test Accuracy: {test_score:.1%}")
    print(f"Features: {len(feature_names)}")
    print(f"\nReady to copy to tool: cp lab/models/ebm_v{model_version}.pkl tool/models/")

if __name__ == "__main__":
    main()
