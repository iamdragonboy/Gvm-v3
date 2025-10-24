# GVM Panel - Admin Setup Complete ✅

## Admin Credentials Created

**Username:** `admin`  
**Password:** `admin`  
**Email:** `admin@gvmpanel.local`  
**Role:** `admin`  
**Initial Credits:** `10000`

---

## Database Information

- **Database Type:** SQLite
- **Database Location:** `./instance/gvm_panel.db`
- **Database Size:** 28KB
- **Status:** ✅ Initialized and ready

---

## Application Structure

```
gvm-panel/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── add_admin.py               # Admin user creation script (NEW)
├── instance/
│   └── gvm_panel.db           # SQLite database (CREATED)
├── templates/                  # HTML templates
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
└── static/                     # CSS and JavaScript
    ├── css/style.css
    └── js/main.js
```

---

## How to Start the Application

### 1. Start the Flask Server

```bash
cd /home/user/gvm-panel
python3 app.py
```

The application will run on: **http://0.0.0.0:5000**

### 2. Access the Application

- **Homepage:** http://localhost:5000
- **Login Page:** http://localhost:5000/login
- **Admin Panel:** http://localhost:5000/admin (after login)

### 3. Login with Admin Credentials

1. Navigate to the login page
2. Enter username: `admin`
3. Enter password: `admin`
4. Click "Login"

---

## Admin Features

Once logged in as admin, you have access to:

### 👥 User Management (`/admin/users`)
- View all registered users
- Add new users (regular or admin)
- Delete users
- Manage user credits (add/remove)

### 🖥️ VPS Management (`/admin/vps`)
- View all VPS instances across all users
- Manage any user's VPS
- Start/Stop/Restart/Delete VPS containers

### ⚙️ Panel Settings (`/admin/settings`)
- Customize panel name
- Set logo URL
- Set background image
- Update welcome text

### 📊 Dashboard (`/admin`)
- View system statistics
- Monitor resource usage (CPU, RAM, Disk)
- See total users and VPS counts

---

## Regular User Features

Regular users can:

- Create VPS instances (costs credits)
- Manage their own VPS (start/stop/restart/delete)
- View their profile and credits
- Change password and theme preferences
- View dashboard with their VPS list

### VPS Plans Available

| Plan     | RAM  | CPU | Storage | Price (Intel) | Price (AMD) |
|----------|------|-----|---------|---------------|-------------|
| Starter  | 4GB  | 1   | 10GB    | 42 credits    | 83 credits  |
| Basic    | 8GB  | 1   | 10GB    | 96 credits    | 164 credits |
| Standard | 12GB | 2   | 10GB    | 192 credits   | 320 credits |
| Pro      | 16GB | 2   | 10GB    | 220 credits   | 340 credits |

---

## Security Notes

⚠️ **IMPORTANT:** This is a development setup. For production:

1. Change the SECRET_KEY in app.py (line 22)
2. Change the admin password immediately after first login
3. Use a production-grade database (PostgreSQL/MySQL)
4. Enable HTTPS/SSL
5. Set up proper firewall rules
6. Use environment variables for sensitive data
7. Enable rate limiting and CSRF protection

---

## Dependencies Installed

- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- Werkzeug 3.0.1
- python-dotenv 1.0.0

---

## LXC/LXD Requirements

This panel manages LXC containers. Ensure you have:

- LXC/LXD installed on the host system
- Proper permissions to run LXC commands
- Storage pool named `btrpool` configured
- Ubuntu 22.04 image available

To check LXC status:
```bash
lxc list
lxc storage list
```

---

## Troubleshooting

### Cannot create VPS
- Ensure LXC/LXD is installed: `lxc version`
- Check storage pool exists: `lxc storage list`
- Verify permissions to run LXC commands

### Database errors
- Delete `instance/gvm_panel.db` and restart app to recreate
- Or run `python3 add_admin.py` again

### Port already in use
- Change port in app.py (line 607): `app.run(debug=True, host='0.0.0.0', port=5001)`

---

## Created By

Setup completed on: **2025-10-24 06:35 UTC**

Admin user added successfully with script: `add_admin.py`

---

**🎉 Setup Complete! Your GVM Panel is ready to use!**
