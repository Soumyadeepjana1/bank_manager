#!/bin/bash
# Run build if libbank.so doesn't exist
if [ ! -f "libbank.so" ]; then
    ./build.sh
fi

# Set up virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Setting up Python virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install PyQt5 PyQt5-sip
else
    source .venv/bin/activate
fi

# Run the UI
echo "Starting Bank Management System UI..."
python3 main_ui.py
