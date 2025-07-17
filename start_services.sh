#!/bin/bash

# Start both frontend and backend services

echo "🏥 Starting Neurologix Smart Search Services..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run ./setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Create tmux session or use screen to run both services
if command -v tmux &> /dev/null; then
    echo "🚀 Starting services with tmux..."
    
    # Create new tmux session
    tmux new-session -d -s neurologix
    
    # Start backend in first window
    tmux send-keys -t neurologix "cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000" Enter
    
    # Create new window for frontend
    tmux new-window -t neurologix
    tmux send-keys -t neurologix "streamlit run frontend.py --server.port 8501 --server.address 0.0.0.0" Enter
    
    echo "✅ Services started in tmux session 'neurologix'"
    echo "📱 Access the application:"
    echo "   Frontend: http://localhost:8501"
    echo "   Backend API: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo ""
    echo "🔧 To manage services:"
    echo "   View sessions: tmux list-sessions"
    echo "   Attach to session: tmux attach -t neurologix"
    echo "   Stop services: tmux kill-session -t neurologix"
    
elif command -v screen &> /dev/null; then
    echo "🚀 Starting services with screen..."
    
    # Start backend in detached screen
    screen -dmS neurologix-backend bash -c "cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    
    # Start frontend in detached screen
    screen -dmS neurologix-frontend bash -c "streamlit run frontend.py --server.port 8501 --server.address 0.0.0.0"
    
    echo "✅ Services started in screen sessions"
    echo "📱 Access the application:"
    echo "   Frontend: http://localhost:8501"
    echo "   Backend API: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo ""
    echo "🔧 To manage services:"
    echo "   List sessions: screen -ls"
    echo "   Attach to backend: screen -r neurologix-backend"
    echo "   Attach to frontend: screen -r neurologix-frontend"
    echo "   Stop backend: screen -S neurologix-backend -X quit"
    echo "   Stop frontend: screen -S neurologix-frontend -X quit"
    
else
    echo "❌ Neither tmux nor screen found. Please install one of them or run services manually:"
    echo ""
    echo "Terminal 1 (Backend):"
    echo "cd backend && uvicorn main:app --reload"
    echo ""
    echo "Terminal 2 (Frontend):"
    echo "streamlit run frontend.py"
fi
