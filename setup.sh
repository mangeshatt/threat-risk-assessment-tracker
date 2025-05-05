#!/bin/bash

# setup.sh - Setup script for TRA Tracker

echo "Setting up the Threat & Risk Assessment (TRA) Tracker..."

# Step 1: Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Step 2: Activate environment
echo "Activating virtual environment..."
source venv/bin/activate

# Step 3: Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Step 4: Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Step 5: Create necessary directories
echo "Ensuring data directory exists..."
mkdir -p data

# Step 6: Launch Streamlit app
echo "Launching the TRA Tracker app..."
streamlit run app.py
