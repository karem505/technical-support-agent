#!/bin/bash

# Run Frontend

set -e

echo "🚀 Starting Frontend..."

cd frontend

# Load environment variables
if [ -f .env.local ]; then
    export $(cat .env.local | grep -v '^#' | xargs)
fi

echo "Starting Next.js development server..."
pnpm dev
