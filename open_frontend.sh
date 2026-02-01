#!/bin/bash
cd "$(dirname "$0")/frontend"

# Check if port 8000 is in use, use 8001 if so
PORT=8000
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "Port 8000 is in use, using 8001 instead..."
    PORT=8001
    # Kill existing process on 8000 if it's our server
    lsof -ti:8000 | xargs kill -9 2>/dev/null
fi

echo "Opening Operations Agent Chatbot..."
echo "Server: http://localhost:$PORT"
echo ""
python3 -m http.server $PORT
