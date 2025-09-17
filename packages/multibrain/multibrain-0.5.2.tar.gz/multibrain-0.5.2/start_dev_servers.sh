#!/bin/bash

# Start development servers for MultiBrain

echo "Starting MultiBrain development servers..."

# Function to cleanup on exit
cleanup() {
    echo -e "\nShutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

# Set up trap for cleanup
trap cleanup EXIT INT TERM

# Start backend server
echo "Starting backend server on port 8000..."
cd "$(dirname "$0")"
python -m uvicorn src.multibrain.api.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 3

# Check if backend is running
if ! curl -s http://localhost:8000/docs > /dev/null; then
    echo "Error: Backend failed to start"
    exit 1
fi

echo "Backend started successfully!"

# Start frontend server
echo "Starting frontend server on port 5173..."
cd frontend
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
echo "Waiting for frontend to start..."
sleep 5

echo -e "\n✅ Both servers are running!"
echo "Backend API: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo -e "\nPress Ctrl+C to stop both servers\n"

# Keep script running
wait