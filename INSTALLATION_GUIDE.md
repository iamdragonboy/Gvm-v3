# GVM Panel - Complete Installation Guide

## 📦 Download & Extract

### Method 1: Direct Download
```bash
# Download the archive
wget -O gvm-panel.tar.gz "https://gensparkstorageprodwest.blob.core.windows.net/web-drive/af12cf13-754c-41de-9f85-b2777599740c/1be4b28d-111a-485e-816b-34a78ed1cdd2?se=2025-10-24T07%3A14%3A58Z&sp=r&sv=2025-05-05&sr=b&rscd=attachment%3B%20filename%3D%22gvm-panel.tar.gz%22&sig=nKI3fu7kqn7n4AbdnEIW7fXS%2BToN68I4Qg/yx5xJBVM%3D"

# Extract
tar -xzf gvm-panel.tar.gz
cd gvm-panel
```

## 🚀 Automated Installation (Recommended)

The easiest way to install GVM Panel is using the automated installer:

```bash
cd gvm-panel
sudo bash install.sh
```

This will:
1. ✅ Update system packages
2. ✅ Install LXC, Python, and Nginx
3. ✅ Configure LXC storage pool
4. ✅ Setup Python virtual environment
5. ✅ Install all dependencies
6. ✅ Create systemd service
7. ✅ Configure Nginx (optional)
8. ✅ Start the service

After installation:
- Access via: `http://YOUR_SERVER_IP/` (with Nginx) or `http://YOUR_SERVER_IP:5000/` (without)
- First user to register becomes admin with 10,000 credits

## 🛠️ Manual Installation

If you prefer manual installation:

### Step 1: Install System Dependencies
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y lxc lxc-templates python3 python3-pip python3-venv
```

### Step 2: Configure LXC
```bash
# Create storage pool
sudo lxc storage create btrpool dir

# Verify
sudo lxc storage list
```

### Step 3: Setup Application
```bash
cd gvm-panel

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Application
```bash
# Edit app.py and change secret key (IMPORTANT for production)
nano app.py

# Find this line and change it:
app.config['SECRET_KEY'] = 'your-unique-secret-key-here'
```

### Step 5: Run Application

**Development Mode:**
```bash
python app.py
```

**Production Mode (with Gunicorn):**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**As Systemd Service:**
```bash
# Create service file
sudo nano /etc/systemd/system/gvm-panel.service

# Add content:
[Unit]
Description=GVM Panel
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/path/to/gvm-panel
Environment="PATH=/path/to/gvm-panel/venv/bin"
ExecStart=/path/to/gvm-panel/venv/bin/python /path/to/gvm-panel/app.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable gvm-panel
sudo systemctl start gvm-panel
sudo systemctl status gvm-panel
```

## 🌐 Nginx Configuration (Optional)

To run on port 80 with domain:

```bash
# Install Nginx
sudo apt install -y nginx

# Create configuration
sudo nano /etc/nginx/sites-available/gvm-panel

# Add:
server {
    listen 80;
    server_name your-domain.com;  # Change this

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/gvm-panel /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test and restart
sudo nginx -t
sudo systemctl restart nginx
```

## 🔒 SSL/HTTPS Setup (Recommended for Production)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
sudo certbot renew --dry-run
```

## 📊 Post-Installation

### 1. Access the Panel
Open browser and go to:
- With Nginx: `http://your-domain.com` or `http://YOUR_SERVER_IP/`
- Without Nginx: `http://YOUR_SERVER_IP:5000/`

### 2. Create Admin Account
1. Click "Register"
2. Fill in username, email, password
3. **Important**: First user becomes admin automatically
4. Login with your credentials

### 3. Verify Installation
Check that you can see:
- ✅ Dashboard with system resources (CPU, RAM, Disk)
- ✅ "Create VPS" button
- ✅ "Admin Panel" link (for admin users)
- ✅ Profile section with your credits (first admin gets 10,000)

### 4. Test VPS Creation
1. Click "Create VPS"
2. Select "Starter" plan
3. Choose "Intel" processor
4. Click "Create VPS"
5. Wait 1-2 minutes for creation
6. Click "Manage" to control the VPS

## 🔧 Configuration

### Change Panel Appearance (Admin Only)
1. Go to Admin Panel → Panel Settings
2. Customize:
   - Panel Name (e.g., "Your Company VPS")
   - Logo URL (from Discord CDN or image host)
   - Background URL (optional)
   - Welcome Text
3. Preview changes
4. Save

### User Management (Admin Only)
1. Go to Admin Panel → Manage Users
2. Add users with different roles
3. Manage credits
4. Delete users if needed

## 🔍 Verification Checklist

After installation, verify:

- [ ] Application is running (check systemd status)
- [ ] Can access web interface
- [ ] Can register and login
- [ ] Dashboard shows system resources
- [ ] Can create a test VPS
- [ ] VPS appears in "lxc list"
- [ ] Can start/stop VPS
- [ ] Admin panel is accessible (for admin)
- [ ] Can manage users (admin)
- [ ] Theme switching works (dark/light)

## 🐛 Troubleshooting

### Service Won't Start
```bash
# Check logs
journalctl -u gvm-panel -n 50 --no-pager

# Check if port is already in use
sudo lsof -i :5000

# Restart service
sudo systemctl restart gvm-panel
```

### LXC Permission Denied
```bash
# Add user to lxd group
sudo usermod -aG lxd $USER
newgrp lxd

# Or run app as root (not recommended for production)
sudo python app.py
```

### Database Errors
```bash
# Reset database
cd gvm-panel
rm gvm_panel.db

# Restart application (database will be recreated)
python app.py
```

### VPS Creation Fails
```bash
# Check LXC status
sudo lxc list

# Check storage
sudo lxc storage list

# Check logs
journalctl -u gvm-panel -f
```

### Nginx 502 Bad Gateway
```bash
# Check if GVM Panel service is running
sudo systemctl status gvm-panel

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Restart both services
sudo systemctl restart gvm-panel
sudo systemctl restart nginx
```

## 📋 System Requirements

**Minimum:**
- OS: Ubuntu 20.04+ / Debian 11+
- CPU: 2 cores
- RAM: 2 GB
- Disk: 20 GB
- LXC support

**Recommended:**
- OS: Ubuntu 22.04 LTS
- CPU: 4+ cores
- RAM: 8+ GB
- Disk: 100+ GB SSD
- Dedicated server or VPS

## 🔐 Security Best Practices

1. **Change Secret Key**: Edit `app.py` before production
2. **Use HTTPS**: Setup SSL certificate
3. **Firewall**: Configure UFW
   ```bash
   sudo ufw allow 22/tcp   # SSH
   sudo ufw allow 80/tcp   # HTTP
   sudo ufw allow 443/tcp  # HTTPS
   sudo ufw enable
   ```
4. **Regular Updates**: Keep system updated
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```
5. **Backups**: Backup database regularly
   ```bash
   cp gvm_panel.db gvm_panel.db.backup
   ```

## 📞 Support

For issues:
1. Check the logs: `journalctl -u gvm-panel -f`
2. Review README.md and QUICKSTART.md
3. Check LXC status: `lxc list`
4. Verify storage: `lxc storage list`

## 📝 File Structure

```
gvm-panel/
├── app.py                    # Main application
├── requirements.txt          # Python dependencies
├── install.sh               # Automated installer
├── README.md                # Full documentation
├── QUICKSTART.md            # Quick start guide
├── INSTALLATION_GUIDE.md    # This file
├── templates/               # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── create_vps.html
│   ├── manage_vps.html
│   ├── admin_panel.html
│   ├── admin_users.html
│   ├── admin_vps_list.html
│   └── admin_settings.html
└── static/                  # Static files
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## 🎯 Next Steps

After successful installation:

1. **Customize the panel** (Admin Panel → Settings)
2. **Add users** (Admin Panel → Manage Users)
3. **Create test VPS** to verify everything works
4. **Setup SSL** for secure access
5. **Configure backups** for the database
6. **Monitor resources** regularly

## 🚀 Ready to Go!

Your GVM Panel is now installed and ready to manage VPS instances!

Access it at: `http://YOUR_SERVER_IP:5000/` or `http://your-domain.com/`

First user to register becomes admin with 10,000 credits automatically.

Enjoy! 🎉
