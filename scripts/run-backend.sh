#!/bin/bash

# Run Backend Services

set -e

echo "🚀 Starting Odoo Support Agent Backend..."

cd backend

# Activate virtual environment
source venv/bin/activate

# Load environment variables
if [ -f ../.env ]; then
    export $(cat ../.env | grep -v '^#' | xargs)
fi

# Start API server in background
echo "Starting API server..."
python -m uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000} &
API_PID=$!

# Give API server time to start
sleep 2

# Start agent
echo "Starting voice agent..."
python -m agent.agent &
AGENT_PID=$!

echo ""
echo "✅ Backend services started!"
echo "API Server PID: $API_PID"
echo "Agent PID: $AGENT_PID"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "kill $API_PID $AGENT_PID; exit" INT TERM

wait
