#!/bin/bash

# Deployment script for SAS Log and LST Checker Web Application

# Create a virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install flask pandas gunicorn

# Create necessary directories if they don't exist
echo "Setting up directories..."
mkdir -p uploads

# Set permissions
echo "Setting permissions..."
chmod -R 755 .
chmod -R 777 uploads

# Run tests
echo "Running tests..."
python test_app.py

# Start the application
echo "Starting the application..."
echo "You can access the application at http://localhost:5000"
gunicorn -w 4 -b 0.0.0.0:5000 app:app
