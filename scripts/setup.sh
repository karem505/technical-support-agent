#!/bin/bash

# Odoo Technical Support Agent - Setup Script

set -e

echo "🚀 Setting up Odoo Technical Support Agent..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your credentials before running the application"
else
    echo "✓ .env file already exists"
fi

# Setup backend
echo ""
echo "🐍 Setting up Python backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

cd ..

# Setup frontend
echo ""
echo "📦 Setting up frontend..."
cd frontend

if ! command -v pnpm &> /dev/null; then
    echo "Installing pnpm..."
    npm install -g pnpm
fi

echo "Installing frontend dependencies..."
pnpm install

# Create .env.local from example
if [ ! -f .env.local ]; then
    cp .env.example .env.local
fi

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your credentials"
echo "2. Edit frontend/.env.local with your configuration"
echo "3. Run 'docker-compose up' or use individual scripts:"
echo "   - Backend: ./scripts/run-backend.sh"
echo "   - Frontend: ./scripts/run-frontend.sh"
echo ""
