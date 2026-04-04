#!/bin/bash
# VERILENCE STARTUP SCRIPT
# Opens all required terminals and services

set -e

echo ""
echo "======================================================================"
echo "VERILENCE v1.0 - STARTUP SEQUENCE"
echo "======================================================================"
echo ""

# Check prerequisites
echo "[CHECK] Google API Key..."
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  GOOGLE_API_KEY not set"
    echo "Set it with: export GOOGLE_API_KEY='your-key-here'"
    exit 1
fi
echo "✓ GOOGLE_API_KEY set"

echo ""
echo "[CHECK] Python environment..."
python3 --version

echo ""
echo "======================================================================"
echo "STARTUP OPTIONS"
echo "======================================================================"
echo ""
echo "Usage: ./START.sh [option]"
echo ""
echo "  1. docker    - Start Qdrant Docker container only"
echo "  2. demo      - Run demo immediately (requires Docker running)"
echo "  3. test      - Run test suite"
echo "  4. analyze   - Run single deal analysis"
echo "  5. help      - Show this help"
echo ""
echo "Quick start:"
echo "  Terminal 1: ./START.sh docker"
echo "  Terminal 2: python3 analyze_single_deal.py"
echo ""
echo "======================================================================"
echo ""

# Parse arguments
case "${1:-help}" in
    docker)
        echo "[DOCKER] Starting Qdrant..."
        echo "⚠️  Keep this terminal open while working"
        echo ""
        docker run -p 6333:6333 qdrant/qdrant
        ;;
    
    demo)
        echo "[DEMO] Running Verilence demo..."
        echo ""
        # Check if Docker is running
        if ! docker ps > /dev/null 2>&1; then
            echo "❌ Docker not running"
            echo "Start it first: ./START.sh docker (in separate terminal)"
            exit 1
        fi
        python3 demo_oil_gas.py
        ;;
    
    test)
        echo "[TEST] Running test suite..."
        echo ""
        if ! docker ps > /dev/null 2>&1; then
            echo "❌ Docker not running"
            echo "Start it first: ./START.sh docker (in separate terminal)"
            exit 1
        fi
        python3 test_verilence.py
        ;;
    
    analyze)
        echo "[ANALYZE] Running deal analysis..."
        echo ""
        if ! docker ps > /dev/null 2>&1; then
            echo "❌ Docker not running"
            echo "Start it first: ./START.sh docker (in separate terminal)"
            exit 1
        fi
        python3 analyze_single_deal.py
        ;;
    
    *)
        echo "[HELP] VERILENCE Startup Guide"
        echo ""
        echo "Prerequisites:"
        echo "  1. Docker installed: docker --version"
        echo "  2. Google API Key: export GOOGLE_API_KEY='your-key'"
        echo "  3. Python 3.12+: python3 --version"
        echo ""
        echo "Quick Setup:"
        echo ""
        echo "  Step 1 - Terminal 1 (Keep open):"
        echo "    cd ~/verilence"
        echo "    ./START.sh docker"
        echo ""
        echo "  Step 2 - Terminal 2 (New terminal):"
        echo "    cd ~/verilence"
        echo "    export GOOGLE_API_KEY='your-key'"
        echo "    python3 analyze_single_deal.py"
        echo ""
        echo "Files you'll need:"
        echo "  - layer1_ingestion.py"
        echo "  - layer2_embedding.py"
        echo "  - layer3_rag_qdrant.py"
        echo "  - layer4_ebm.py"
        echo "  - layer5_llm.py"
        echo "  - layer6_confidence_routing.py"
        echo "  - layer8_reporting.py"
        echo "  - layer9_audit_reporting.py"
        echo "  - download_reports.py"
        echo ""
        echo "Demo data location:"
        echo "  - demo_data/oil_gas/*.txt"
        echo ""
        echo "Output files:"
        echo "  - output/audit_report_*.json"
        echo "  - output/audit_report_*.html"
        echo "  - ~/Downloads/Verilence_Reports/ (auto-downloaded)"
        echo ""
        ;;
esac
