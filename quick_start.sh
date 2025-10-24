#!/bin/bash

# GVM Panel - Quick Start Script
# This script will set up and start the GVM Panel with admin user already configured

echo "================================================"
echo "  GVM Panel - Quick Start"
echo "================================================"
echo ""

# Check if running in the correct directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the gvm-panel directory."
    exit 1
fi

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install --quiet --no-input -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check if database exists
if [ ! -f "instance/gvm_panel.db" ]; then
    echo ""
    echo "🗄️  Database not found. Creating admin user..."
    python3 add_admin.py
    
    if [ $? -eq 0 ]; then
        echo "✓ Admin user created"
    else
        echo "❌ Failed to create admin user"
        exit 1
    fi
else
    echo ""
    echo "✓ Database already exists"
fi

# Display credentials
echo ""
echo "================================================"
echo "  Admin Credentials"
echo "================================================"
echo "  Username: admin"
echo "  Password: admin"
echo "================================================"
echo ""
echo "🚀 Starting GVM Panel..."
echo ""
echo "   Access the panel at: http://localhost:5000"
echo "   Login page: http://localhost:5000/login"
echo "   Admin panel: http://localhost:5000/admin"
echo ""
echo "   Press Ctrl+C to stop the server"
echo ""
echo "================================================"
echo ""

# Start the Flask application
python3 app.py
