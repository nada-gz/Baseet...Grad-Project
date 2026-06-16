#!/bin/bash
set -e

echo "--- Starting deployment for baseet.tech ---"

cd /home/baseet/Baseet...Grad-Project/

echo ">>> Pulling latest changes from main..."
git fetch origin
git reset --hard origin/main

echo ">>> Building frontend for production..."
cd SW/frontend
npm install
REACT_APP_API_URL="https://baseet.tech" \
REACT_APP_WS_URL="wss://baseet.tech" \
npm run build

echo ">>> Installing backend dependencies..."
cd /home/baseet/Baseet...Grad-Project/SW/backend
source venv/bin/activate
pip install -r requirements.txt

echo ">>> Restarting backend process with pm2..."
pm2 delete baseet-backend || true

pm2 start venv/bin/python \
  --name baseet-backend \
  -- -m uvicorn main:app --host 0.0.0.0 --port 8000

pm2 save

echo "--- Deployment finished successfully! ---"