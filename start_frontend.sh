#!/bin/bash

echo "🚀 Starting AI ChatBot Frontend..."
echo "📱 Frontend will be available at: http://localhost:3000"
echo "🔗 Make sure the backend is running at: http://localhost:8000"
echo ""
echo "="*50
echo ""

# Navigate to the React app directory
cd frontend/react-app

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start the React development server
echo "🌐 Starting React development server..."
npm start 