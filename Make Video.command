#!/bin/bash
cd "$(dirname "$0")"
PORT=8765
python3 -m http.server $PORT >/dev/null 2>&1 &
SERVER=$!
trap 'kill $SERVER 2>/dev/null' EXIT
sleep 1
open -a "Google Chrome" "http://localhost:$PORT/video-maker.html" 2>/dev/null || open "http://localhost:$PORT/video-maker.html"
echo "The video maker is open in your browser: http://localhost:$PORT/video-maker.html"
echo "Close this window when you're done."
wait $SERVER
