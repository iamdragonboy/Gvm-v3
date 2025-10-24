#!/bin/bash

# GVM Panel - Installation Script
# This script automates the installation process

set -e

echo "=========================================="
echo "GVM Panel - Installation Script"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Update system
echo "[1/6] Updating system packages..."
apt update && apt upgrade -y

# Install system dependencies
echo "[2/6] Installing system dependencies..."
apt install -y lxc lxc-templates python3 python3-pip python3-venv nginx

# Configure LXC
echo "[3/6] Configuring LXC..."
if ! lxc storage list | grep -q "btrpool"; then
    echo "Creating btrpool storage..."
    lxc storage create btrpool dir
fi

# Create application directory
echo "[4/6] Setting up application directory..."
APP_DIR="/opt/gvm-panel"
mkdir -p $APP_DIR

# Copy files to application directory
if [ -d "./templates" ] && [ -d "./static" ] && [ -f "./app.py" ]; then
    echo "Copying files to $APP_DIR..."
    cp -r ./* $APP_DIR/
else
    echo "Error: Please run this script from the gvm-panel directory"
    exit 1
fi

# Create virtual environment
echo "[5/6] Creating Python virtual environment..."
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service
echo "[6/6] Creating systemd service..."
cat > /etc/systemd/system/gvm-panel.service << EOF
[Unit]
Description=GVM Panel - VPS Management System
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx (optional)
echo ""
echo "Do you want to configure Nginx as reverse proxy? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    cat > /etc/nginx/sites-available/gvm-panel << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    # Enable site
    ln -sf /etc/nginx/sites-available/gvm-panel /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Test and reload nginx
    nginx -t && systemctl reload nginx
    echo "Nginx configured successfully!"
fi

# Enable and start service
systemctl daemon-reload
systemctl enable gvm-panel
systemctl start gvm-panel

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Service Status:"
systemctl status gvm-panel --no-pager
echo ""
echo "Access your panel at:"
if systemctl is-active --quiet nginx; then
    echo "  http://YOUR_SERVER_IP/"
else
    echo "  http://YOUR_SERVER_IP:5000/"
fi
echo ""
echo "First user to register will be the admin!"
echo ""
echo "Useful commands:"
echo "  - Check status: systemctl status gvm-panel"
echo "  - View logs: journalctl -u gvm-panel -f"
echo "  - Restart: systemctl restart gvm-panel"
echo "  - Stop: systemctl stop gvm-panel"
echo ""
