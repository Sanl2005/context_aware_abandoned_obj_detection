#!/bin/bash
# Quick Start Script for Object Detection Dashboard
# This starts all required services in the correct order

echo "🚀 Starting SentinelEye Object Detection System..."
echo ""

# Check if running on Windows (PowerShell)
if [ "$OS" == "Windows_NT" ]; then
    echo "Note: This is a bash script. For Windows, use the quick_start.bat file instead."
    exit 1
fi

# Step 1: Start ML Service (Flask)
echo "📹 Starting ML Service (Video Feed + Object Detection)..."
cd ml_service
python app.py &
ML_PID=$!
echo "   ML Service running on http://127.0.0.1:5000 (PID: $ML_PID)"
cd ..
sleep 3

# Step 2: Start Rails Backend (Optional - for storing detections)
echo ""
echo "💾 Starting Rails Backend (API)..."
cd rails_backend
rails server -p 3000 &
RAILS_PID=$!
echo "   Rails Backend running on http://127.0.0.1:3000 (PID: $RAILS_PID)"
cd ..
sleep 5

# Step 3: Start Frontend Dashboard
echo ""
echo "🎨 Starting Frontend Dashboard..."
cd frontend_dashboard
npm start &
FRONTEND_PID=$!
echo "   Frontend Dashboard opening at http://localhost:3001"
cd ..

echo ""
echo "✅ All services started!"
echo ""
echo "🌐 Open your browser to: http://localhost:3001"
echo ""
echo "To stop all services:"
echo "  kill $ML_PID $RAILS_PID $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop this script (services will continue running)"
echo "──────────────────────────────────────────────────"

# Keep script running
wait
