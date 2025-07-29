#!/bin/bash

# AI Resume Builder Development Startup Script

echo "🚀 Starting AI Resume Builder Development Environment"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "resume-env" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Function to start backend
start_backend() {
    echo "🔧 Starting Backend (FastAPI)..."
    cd /home/msmith/AIResumeBuilder
    source resume-env/bin/activate
    python run_backend.py &
    BACKEND_PID=$!
    echo "✅ Backend started on http://localhost:8000 (PID: $BACKEND_PID)"
}

# Function to start frontend
start_frontend() {
    echo "🎨 Starting Frontend (Next.js)..."
    cd /home/msmith/AIResumeBuilder/resume-builder
    npm run dev &
    FRONTEND_PID=$!
    echo "✅ Frontend started on http://localhost:3000 (PID: $FRONTEND_PID)"
}

# Start both services
start_backend
sleep 3
start_frontend

echo ""
echo "🎉 Development environment is ready!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap 'echo "🛑 Stopping services..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0' INT
wait