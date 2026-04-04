#!/bin/bash
# VERILENCE STARTUP SCRIPT

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
echo "  2. demo      - Run demo immediately"
echo "  3. test      - Run test suite"
echo "  4. analyze   - Run deal analysis"
echo "  5. help      - Show this help"
echo ""
echo "Quick start:"
echo "  Terminal 1: ./START.sh docker"
echo "  Terminal 2: ./START.sh analyze"
echo ""
echo "======================================================================"
echo ""

case "${1:-help}" in
    docker)
        echo "[DOCKER] Starting Qdrant..."
        echo "Keep this terminal open while working"
        echo ""
        docker run -p 6333:6333 qdrant/qdrant
        ;;
    
    demo)
        echo "[DEMO] Running Verilence demo..."
        echo ""
        if ! docker ps > /dev/null 2>&1; then
            echo "Docker not running"
            exit 1
        fi
        python3 demo_oil_gas.py
        ;;
    
    test)
        echo "[TEST] Running test suite..."
        echo ""
        if ! docker ps > /dev/null 2>&1; then
            echo "Docker not running"
            exit 1
        fi
        python3 test_verilence.py
        ;;
    
    analyze)
        echo "[ANALYZE] Running deal analysis..."
        echo ""
        if ! docker ps > /dev/null 2>&1; then
            echo "Docker not running"
            exit 1
        fi
        python3 analyze_single_deal.py
        ;;
    
    *)
        echo "VERILENCE Startup Guide"
        echo ""
        echo "Prerequisites:"
        echo "  1. Docker installed"
        echo "  2. Google API Key: export GOOGLE_API_KEY='your-key'"
        echo "  3. Python 3.12+"
        echo ""
        echo "Setup:"
        echo ""
        echo "  Terminal 1 (Keep open):"
        echo "    cd ~/verilence"
        echo "    ./START.sh docker"
        echo ""
        echo "  Terminal 2 (New terminal):"
        echo "    cd ~/verilence"
        echo "    export GOOGLE_API_KEY='your-key'"
        echo "    ./START.sh analyze"
        echo ""
        ;;
esac

