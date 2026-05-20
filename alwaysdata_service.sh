#!/bin/bash
# AlwaysData Service Script for Hududiy Agent Bot
# This script is designed to run as an AlwaysData Service for 24/7 operation

# Change to bot directory
cd ~/bot

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the bot
exec python3 working_bot.py
