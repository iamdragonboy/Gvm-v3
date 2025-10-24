# GVM Panel - Quick Start Guide

## One-Click Installation (Recommended)

```bash
# 1. Download the project
wget https://path-to-your-gvm-panel.zip
unzip gvm-panel.zip
cd gvm-panel

# 2. Run the automated installer (as root)
sudo bash install.sh
```

The installer will:
- Install all system dependencies (LXC, Python, Nginx)
- Configure LXC storage
- Create Python virtual environment
- Install Python dependencies
- Setup systemd service
- Optionally configure Nginx

## Manual Installation

### Step 1: Install Dependencies
```bash
sudo apt update
sudo apt install -y lxc lxc-templates python3 python3-pip python3-venv
```

### Step 2: Setup LXC Storage
```bash
# Create storage pool
sudo lxc storage create btrpool dir
```

### Step 3: Setup Application
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
# Development mode
python app.py

# Production mode (with Gunicorn)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## First Login

1. Open browser and navigate to `http://YOUR_SERVER_IP:5000`
2. Click "Register" to create your account
3. **Important**: The first user to register becomes the admin automatically
4. Login with your credentials
5. You'll see the dashboard with system resources

## Creating Your First VPS

1. From the dashboard, click **"Create VPS"**
2. Select a plan:
   - **Starter**: 4GB RAM, 1 CPU (42/83 credits)
   - **Basic**: 8GB RAM, 1 CPU (96/164 credits)
   - **Standard**: 12GB RAM, 2 CPU (192/320 credits)
   - **Pro**: 16GB RAM, 2 CPU (220/340 credits)
3. Choose processor: **Intel** or **AMD**
4. Click **"Create VPS"**
5. Wait for VPS to be created (may take 1-2 minutes)

## Managing VPS

From the dashboard, click **"Manage"** on any VPS to:
- **Start/Stop/Restart** the VPS
- Get **SSH access** via tmate
- **Delete** the VPS

## Admin Functions

### Access Admin Panel
Click **"Admin Panel"** in the navigation menu

### Manage Users
1. Go to **Admin Panel → Manage Users**
2. Add new users with role (User/Admin)
3. Manage credits (Add/Remove)
4. Delete users (this also deletes their VPS)

### Customize Panel
1. Go to **Admin Panel → Panel Settings**
2. Change:
   - Panel Name (e.g., "GVM Panel")
   - Logo URL (from Discord CDN or image hosting)
   - Background URL (optional)
   - Welcome Text
3. Preview changes in real-time
4. Click **"Save Settings"**

## User Profile

Click **"Profile"** in navigation to:
- Update email
- Change password
- Switch theme (Dark/Light)
- View your credits balance

## Credits System

- Users need credits to create VPS
- Admin can add/remove credits from any user
- Different plans have different costs
- First admin user gets 10,000 credits automatically

## Troubleshooting

### LXC Permission Denied
```bash
sudo usermod -aG lxd $USER
newgrp lxd
```

### Port Already in Use
Change port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

### Service Not Starting
```bash
# Check logs
journalctl -u gvm-panel -f

# Restart service
sudo systemctl restart gvm-panel
```

### Database Issues
```bash
# Reset database
rm gvm_panel.db
python app.py
# Then register first user again
```

## System Requirements

**Minimum:**
- Ubuntu 20.04+ or Debian 11+
- 2GB RAM
- 20GB Disk Space
- LXC support

**Recommended:**
- Ubuntu 22.04 LTS
- 4GB+ RAM
- 50GB+ SSD
- Dedicated server or VPS

## Security Tips

1. **Change Secret Key**: Edit `app.py` and change the secret key
2. **Use HTTPS**: Setup SSL with Let's Encrypt
3. **Firewall**: Configure UFW or iptables
4. **Regular Backups**: Backup `gvm_panel.db` regularly
5. **Update System**: Keep system packages updated

## Service Management

```bash
# Start service
sudo systemctl start gvm-panel

# Stop service
sudo systemctl stop gvm-panel

# Restart service
sudo systemctl restart gvm-panel

# Check status
sudo systemctl status gvm-panel

# View logs
journalctl -u gvm-panel -f
```

## Nginx Configuration (Optional)

If you want to run on port 80 with Nginx:

```bash
# Install Nginx
sudo apt install nginx

# Create config
sudo nano /etc/nginx/sites-available/gvm-panel

# Add content:
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/gvm-panel /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

## Default Credentials

There are no default credentials. The first user you register becomes the admin.

## Need Help?

- Check the full README.md for detailed documentation
- Review logs: `journalctl -u gvm-panel -f`
- Check LXC status: `lxc list`
- Verify storage: `lxc storage list`

## Feature Highlights

✅ **User Management**: Register, login, profile management
✅ **VPS Creation**: Multiple plans with Intel/AMD options
✅ **VPS Control**: Start, stop, restart, SSH access
✅ **Admin Panel**: Full control over users and VPS
✅ **Resource Monitoring**: Real-time CPU, RAM, Disk usage
✅ **Theme Support**: Dark and Light themes
✅ **Credits System**: Built-in credit management
✅ **Customization**: Change panel name, logo, background

## Production Checklist

- [ ] Change secret key in `app.py`
- [ ] Setup HTTPS/SSL
- [ ] Configure firewall
- [ ] Setup automated backups
- [ ] Use Gunicorn instead of Flask dev server
- [ ] Setup monitoring/logging
- [ ] Configure Nginx as reverse proxy
- [ ] Set up proper user permissions
- [ ] Enable automatic updates
- [ ] Test disaster recovery

Enjoy your GVM Panel! 🚀
