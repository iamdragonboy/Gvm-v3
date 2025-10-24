# GVM Panel - VPS Management Web Application

A comprehensive web-based VPS control panel built with Flask, designed to manage LXC containers with a beautiful dark/light theme interface.

## Features

### User Features
- **Authentication System**
  - User registration and login
  - Secure password hashing
  - Session management

- **Dashboard**
  - Real-time system resource monitoring (CPU, RAM, Disk)
  - View all VPS instances
  - Active/stopped VPS status
  
- **VPS Management**
  - Create VPS with multiple plans (Starter, Basic, Standard, Pro)
  - Choose between Intel/AMD processors
  - Start/Stop/Restart VPS instances
  - SSH access via tmate
  - Delete VPS instances
  - Real-time VPS resource monitoring

- **Profile Management**
  - Update email
  - Change password
  - Switch between Dark/Light themes
  - View credits balance

### Admin Features
- **Admin Dashboard**
  - System-wide statistics
  - Total users, VPS count
  - Running/stopped VPS overview
  - System resource monitoring

- **User Management**
  - Add new users (User/Admin roles)
  - Delete user accounts
  - Manage user credits (Add/Remove)
  - View all users with VPS count

- **VPS Management**
  - View all VPS instances across all users
  - Manage any user's VPS
  - Monitor VPS resources

- **Panel Customization**
  - Change panel name
  - Update logo URL
  - Set custom background
  - Modify welcome text
  - Real-time preview

## Installation

### Prerequisites
- Python 3.8+
- LXC (Linux Containers)
- Ubuntu/Debian-based system (recommended)

### Step 1: Install System Dependencies
```bash
# Install LXC and required packages
sudo apt update
sudo apt install -y lxc lxc-templates python3-pip python3-venv
```

### Step 2: Setup Python Environment
```bash
# Create project directory
mkdir gvm-panel
cd gvm-panel

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 3: Configure LXC Storage Pool
```bash
# Create btrfs storage pool (as referenced in v2.py)
sudo lxc storage create btrpool btrfs

# Or use directory-based storage
sudo lxc storage create btrpool dir
```

### Step 4: Run the Application
```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Run the application
python app.py
```

The application will be available at `http://localhost:5000`

## First Time Setup

1. **Access the application**: Open `http://localhost:5000` in your browser
2. **Register first user**: The first registered user automatically becomes an admin
3. **Login**: Use your credentials to login
4. **Admin Panel**: Access admin features from the navigation menu

## VPS Plans

| Plan     | RAM  | CPU | Storage | Intel Price | AMD Price |
|----------|------|-----|---------|-------------|-----------|
| Starter  | 4GB  | 1   | 10GB    | 42 credits  | 83 credits|
| Basic    | 8GB  | 1   | 10GB    | 96 credits  | 164 credits|
| Standard | 12GB | 2   | 10GB    | 192 credits | 320 credits|
| Pro      | 16GB | 2   | 10GB    | 220 credits | 340 credits|

## Configuration

### Database
The application uses SQLite by default. Database file: `gvm_panel.db`

### Secret Key
**Important**: Change the secret key in `app.py` before production deployment:
```python
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
```

### LXC Configuration
Ensure LXC is properly configured and the user running the application has permissions to execute LXC commands:
```bash
# Add user to lxc group
sudo usermod -aG lxd $USER
```

## Usage

### Creating a VPS
1. Navigate to Dashboard
2. Click "Create VPS"
3. Select a plan (Starter, Basic, Standard, Pro)
4. Choose processor (Intel/AMD)
5. Click "Create VPS"

### Managing a VPS
1. From Dashboard, click "Manage" on any VPS
2. Available actions:
   - **Start**: Start the VPS
   - **Stop**: Stop the VPS
   - **Restart**: Restart the VPS
   - **SSH Access**: Get SSH connection via tmate
   - **Delete**: Permanently delete the VPS

### Admin Functions

#### Managing Users
1. Go to Admin Panel → Manage Users
2. Add users with username, email, password, and role
3. Manage user credits (add/remove)
4. Delete user accounts (all VPS will be deleted)

#### Customizing Panel
1. Go to Admin Panel → Panel Settings
2. Update panel name, logo URL, background URL, welcome text
3. Preview changes in real-time
4. Save settings

## Project Structure
```
gvm-panel/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── gvm_panel.db          # SQLite database (auto-created)
├── templates/            # HTML templates
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
└── static/               # Static files
    ├── css/
    │   └── style.css     # Custom CSS
    └── js/
        └── main.js       # JavaScript utilities
```

## Security Considerations

1. **Change Secret Key**: Always change the Flask secret key in production
2. **HTTPS**: Use HTTPS in production with proper SSL certificates
3. **Firewall**: Configure firewall rules to restrict access
4. **User Permissions**: Run the application with appropriate permissions
5. **Regular Backups**: Backup the database regularly

## Troubleshooting

### LXC Command Not Found
```bash
# Install LXC
sudo apt install -y lxc lxc-templates
```

### Permission Denied on LXC Commands
```bash
# Add user to lxd group
sudo usermod -aG lxd $USER
newgrp lxd
```

### Database Errors
```bash
# Remove and reinitialize database
rm gvm_panel.db
python app.py
```

### Port Already in Use
Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

## Production Deployment

For production deployment, use a production-grade WSGI server like Gunicorn:

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Consider using Nginx as a reverse proxy:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Features Based on v2.py

This web panel implements all major features from the Discord bot (v2.py):
- ✅ User authentication system
- ✅ VPS creation with multiple plans
- ✅ Intel/AMD processor selection
- ✅ Start/Stop/Restart VPS
- ✅ SSH access via tmate
- ✅ Credit-based system
- ✅ Admin user management
- ✅ Admin VPS management
- ✅ System resource monitoring
- ✅ Dark/Light theme support
- ✅ VPS deletion
- ✅ User profile management

## License

This project is open-source and available for personal and commercial use.

## Support

For issues and questions, please create an issue on the project repository.

## Credits

Based on the Discord bot v2.py with LXC container management.
Developed for GVM Panel VPS Management System.
