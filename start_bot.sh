#!/bin/bash
# Start bot script

cd /home/doniyoebrk/bot

# Load environment variables
export $(cat .env | xargs)

# Start bot
python3 app/main.py
