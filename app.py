"""
GVM Panel - VPS Management Web Application
Complete web-based VPS control panel with user and admin interfaces
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import subprocess
import json
import shlex
from datetime import datetime
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('gvm_panel')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gvm_panel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    panel_name = db.Column(db.String(100), default='GVM Panel')
    logo_url = db.Column(db.String(500), default='https://cdn.discordapp.com/attachments/1417915306227142746/1430629663645892820/IMG_20251020_132544.jpg')
    background_url = db.Column(db.String(500), default='')
    welcome_text = db.Column(db.String(500), default='Welcome to GVM Panel')
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'admin' or 'user'
    credits = db.Column(db.Integer, default=0)
    theme = db.Column(db.String(10), default='dark')  # 'dark' or 'light'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    vps_instances = db.relationship('VPS', backref='owner', lazy=True, cascade='all, delete-orphan')

class VPS(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    container_name = db.Column(db.String(100), unique=True, nullable=False)
    plan = db.Column(db.String(50), default='Custom')
    ram = db.Column(db.String(20))
    cpu = db.Column(db.String(20))
    storage = db.Column(db.String(20))
    processor = db.Column(db.String(20), default='Intel')
    status = db.Column(db.String(20), default='stopped')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Helper Functions
def execute_lxc_sync(command, timeout=120):
    """Execute LXC command synchronously"""
    try:
        cmd = shlex.split(command)
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            text=True
        )
        if result.returncode != 0:
            error = result.stderr.strip() if result.stderr else "Command failed"
            logger.error(f"LXC Error: {command} - {error}")
            return False, error
        return True, result.stdout.strip() if result.stdout else True
    except subprocess.TimeoutExpired:
        logger.error(f"LXC command timed out: {command}")
        return False, f"Command timed out after {timeout} seconds"
    except Exception as e:
        logger.error(f"LXC Error: {command} - {str(e)}")
        return False, str(e)

def get_system_resources():
    """Get system CPU, RAM, and Disk usage"""
    try:
        # CPU Usage
        cpu_cmd = "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1"
        cpu_result = subprocess.run(cpu_cmd, shell=True, capture_output=True, text=True)
        cpu_usage = float(cpu_result.stdout.strip()) if cpu_result.stdout.strip() else 0.0
        
        # RAM Usage
        ram_cmd = "free -m | awk 'NR==2{printf \"%.2f\", $3*100/$2 }'"
        ram_result = subprocess.run(ram_cmd, shell=True, capture_output=True, text=True)
        ram_usage = float(ram_result.stdout.strip()) if ram_result.stdout.strip() else 0.0
        
        # Disk Usage
        disk_cmd = "df -h / | awk 'NR==2{print $5}' | sed 's/%//'"
        disk_result = subprocess.run(disk_cmd, shell=True, capture_output=True, text=True)
        disk_usage = float(disk_result.stdout.strip()) if disk_result.stdout.strip() else 0.0
        
        return {
            'cpu': round(cpu_usage, 2),
            'ram': round(ram_usage, 2),
            'disk': round(disk_usage, 2)
        }
    except Exception as e:
        logger.error(f"Error getting system resources: {e}")
        return {'cpu': 0, 'ram': 0, 'disk': 0}

def get_vps_stats(container_name):
    """Get individual VPS statistics"""
    try:
        # Check if container exists
        check_cmd = f"lxc list {container_name} --format json"
        success, output = execute_lxc_sync(check_cmd)
        if not success:
            return None
        
        containers = json.loads(output)
        if not containers:
            return None
            
        container = containers[0]
        state = container.get('state', {})
        
        # Get memory usage
        memory = state.get('memory', {})
        memory_usage = memory.get('usage', 0) / (1024 * 1024)  # Convert to MB
        
        # Get CPU usage
        cpu = state.get('cpu', {})
        cpu_usage = cpu.get('usage', 0)
        
        return {
            'memory_mb': round(memory_usage, 2),
            'cpu_seconds': cpu_usage,
            'status': state.get('status', 'Unknown')
        }
    except Exception as e:
        logger.error(f"Error getting VPS stats: {e}")
        return None

# Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    settings = Settings.query.first()
    if not settings:
        settings = Settings()
        db.session.add(settings)
        db.session.commit()
    return render_template('index.html', settings=settings)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([username, email, password, confirm_password]):
            flash('All fields are required', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        # Create user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        
        # Make first user admin
        if User.query.count() == 0:
            new_user.role = 'admin'
            new_user.credits = 10000
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    settings = Settings.query.first()
    return render_template('register.html', settings=settings)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    settings = Settings.query.first()
    return render_template('login.html', settings=settings)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    vps_list = VPS.query.filter_by(user_id=user.id).all()
    system_resources = get_system_resources()
    settings = Settings.query.first()
    
    return render_template('dashboard.html', 
                         user=user, 
                         vps_list=vps_list,
                         system_resources=system_resources,
                         settings=settings)

@app.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    settings = Settings.query.first()
    return render_template('profile.html', user=user, settings=settings)

@app.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    user = User.query.get(session['user_id'])
    
    email = request.form.get('email')
    theme = request.form.get('theme')
    
    if email:
        # Check if email is already taken by another user
        existing = User.query.filter_by(email=email).first()
        if existing and existing.id != user.id:
            flash('Email already in use', 'danger')
            return redirect(url_for('profile'))
        user.email = email
    
    if theme:
        user.theme = theme
    
    db.session.commit()
    flash('Profile updated successfully', 'success')
    return redirect(url_for('profile'))

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    user = User.query.get(session['user_id'])
    
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not check_password_hash(user.password, current_password):
        flash('Current password is incorrect', 'danger')
        return redirect(url_for('profile'))
    
    if new_password != confirm_password:
        flash('New passwords do not match', 'danger')
        return redirect(url_for('profile'))
    
    user.password = generate_password_hash(new_password)
    db.session.commit()
    
    flash('Password changed successfully', 'success')
    return redirect(url_for('profile'))

# VPS Management Routes
@app.route('/vps/create', methods=['GET', 'POST'])
@login_required
def create_vps():
    user = User.query.get(session['user_id'])
    settings = Settings.query.first()
    
    plans = {
        'Starter': {'ram': '4GB', 'cpu': '1', 'storage': '10GB', 'price': {'Intel': 42, 'AMD': 83}},
        'Basic': {'ram': '8GB', 'cpu': '1', 'storage': '10GB', 'price': {'Intel': 96, 'AMD': 164}},
        'Standard': {'ram': '12GB', 'cpu': '2', 'storage': '10GB', 'price': {'Intel': 192, 'AMD': 320}},
        'Pro': {'ram': '16GB', 'cpu': '2', 'storage': '10GB', 'price': {'Intel': 220, 'AMD': 340}}
    }
    
    if request.method == 'POST':
        plan = request.form.get('plan')
        processor = request.form.get('processor', 'Intel')
        
        if plan not in plans:
            flash('Invalid plan selected', 'danger')
            return redirect(url_for('create_vps'))
        
        cost = plans[plan]['price'][processor]
        
        if user.credits < cost:
            flash(f'Insufficient credits. You need {cost} credits but have {user.credits}', 'danger')
            return redirect(url_for('create_vps'))
        
        # Create VPS
        vps_count = VPS.query.filter_by(user_id=user.id).count() + 1
        container_name = f"vps-{user.id}-{vps_count}"
        
        plan_specs = plans[plan]
        ram_mb = int(plan_specs['ram'].replace('GB', '')) * 1024
        cpu = plan_specs['cpu']
        
        # Execute LXC command
        lxc_cmd = f"lxc launch ubuntu:22.04 {container_name} --config limits.memory={ram_mb}MB --config limits.cpu={cpu} -s btrpool"
        success, output = execute_lxc_sync(lxc_cmd)
        
        if not success:
            flash(f'Failed to create VPS: {output}', 'danger')
            return redirect(url_for('create_vps'))
        
        # Deduct credits
        user.credits -= cost
        
        # Save to database
        new_vps = VPS(
            user_id=user.id,
            container_name=container_name,
            plan=plan,
            ram=plan_specs['ram'],
            cpu=cpu,
            storage=plan_specs['storage'],
            processor=processor,
            status='running'
        )
        
        db.session.add(new_vps)
        db.session.commit()
        
        flash(f'VPS {container_name} created successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('create_vps.html', user=user, plans=plans, settings=settings)

@app.route('/vps/manage/<int:vps_id>')
@login_required
def manage_vps(vps_id):
    vps = VPS.query.get_or_404(vps_id)
    user = User.query.get(session['user_id'])
    settings = Settings.query.first()
    
    # Check ownership or admin
    if vps.user_id != user.id and user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get VPS stats
    stats = get_vps_stats(vps.container_name)
    
    return render_template('manage_vps.html', vps=vps, user=user, stats=stats, settings=settings)

@app.route('/api/vps/<int:vps_id>/start', methods=['POST'])
@login_required
def start_vps(vps_id):
    vps = VPS.query.get_or_404(vps_id)
    user = User.query.get(session['user_id'])
    
    if vps.user_id != user.id and user.role != 'admin':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    success, output = execute_lxc_sync(f"lxc start {vps.container_name}")
    
    if success:
        vps.status = 'running'
        db.session.commit()
        return jsonify({'success': True, 'message': 'VPS started successfully'})
    else:
        return jsonify({'success': False, 'message': output}), 500

@app.route('/api/vps/<int:vps_id>/stop', methods=['POST'])
@login_required
def stop_vps(vps_id):
    vps = VPS.query.get_or_404(vps_id)
    user = User.query.get(session['user_id'])
    
    if vps.user_id != user.id and user.role != 'admin':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    success, output = execute_lxc_sync(f"lxc stop {vps.container_name}")
    
    if success:
        vps.status = 'stopped'
        db.session.commit()
        return jsonify({'success': True, 'message': 'VPS stopped successfully'})
    else:
        return jsonify({'success': False, 'message': output}), 500

@app.route('/api/vps/<int:vps_id>/restart', methods=['POST'])
@login_required
def restart_vps(vps_id):
    vps = VPS.query.get_or_404(vps_id)
    user = User.query.get(session['user_id'])
    
    if vps.user_id != user.id and user.role != 'admin':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    success, output = execute_lxc_sync(f"lxc restart {vps.container_name}")
    
    if success:
        return jsonify({'success': True, 'message': 'VPS restarted successfully'})
    else:
        return jsonify({'success': False, 'message': output}), 500

@app.route('/api/vps/<int:vps_id>/delete', methods=['POST'])
@login_required
def delete_vps(vps_id):
    vps = VPS.query.get_or_404(vps_id)
    user = User.query.get(session['user_id'])
    
    if vps.user_id != user.id and user.role != 'admin':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    success, output = execute_lxc_sync(f"lxc delete {vps.container_name} --force")
    
    if success:
        db.session.delete(vps)
        db.session.commit()
        return jsonify({'success': True, 'message': 'VPS deleted successfully'})
    else:
        return jsonify({'success': False, 'message': output}), 500

# Admin Routes
@app.route('/admin')
@admin_required
def admin_panel():
    users = User.query.all()
    all_vps = VPS.query.all()
    system_resources = get_system_resources()
    settings = Settings.query.first()
    
    stats = {
        'total_users': len(users),
        'total_vps': len(all_vps),
        'running_vps': len([v for v in all_vps if v.status == 'running']),
        'stopped_vps': len([v for v in all_vps if v.status == 'stopped'])
    }
    
    user = User.query.get(session['user_id'])
    
    return render_template('admin_panel.html', 
                         user=user,
                         users=users, 
                         stats=stats, 
                         system_resources=system_resources,
                         settings=settings)

@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.all()
    settings = Settings.query.first()
    user = User.query.get(session['user_id'])
    return render_template('admin_users.html', users=users, settings=settings, user=user)

@app.route('/admin/user/add', methods=['POST'])
@admin_required
def admin_add_user():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role', 'user')
    
    if User.query.filter_by(username=username).first():
        flash('Username already exists', 'danger')
        return redirect(url_for('admin_users'))
    
    if User.query.filter_by(email=email).first():
        flash('Email already registered', 'danger')
        return redirect(url_for('admin_users'))
    
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, email=email, password=hashed_password, role=role)
    
    db.session.add(new_user)
    db.session.commit()
    
    flash(f'User {username} created successfully', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting yourself
    if user.id == session['user_id']:
        flash('Cannot delete your own account', 'danger')
        return redirect(url_for('admin_users'))
    
    # Delete all VPS owned by this user
    for vps in user.vps_instances:
        execute_lxc_sync(f"lxc delete {vps.container_name} --force")
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.username} deleted successfully', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/user/<int:user_id>/credits', methods=['POST'])
@admin_required
def admin_manage_credits(user_id):
    user = User.query.get_or_404(user_id)
    action = request.form.get('action')
    amount = int(request.form.get('amount', 0))
    
    if action == 'add':
        user.credits += amount
        flash(f'Added {amount} credits to {user.username}', 'success')
    elif action == 'remove':
        user.credits = max(0, user.credits - amount)
        flash(f'Removed {amount} credits from {user.username}', 'success')
    
    db.session.commit()
    return redirect(url_for('admin_users'))

@app.route('/admin/vps')
@admin_required
def admin_vps_list():
    all_vps = VPS.query.all()
    settings = Settings.query.first()
    user = User.query.get(session['user_id'])
    return render_template('admin_vps_list.html', vps_list=all_vps, settings=settings, user=user)

@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    settings = Settings.query.first()
    if not settings:
        settings = Settings()
        db.session.add(settings)
        db.session.commit()
    
    if request.method == 'POST':
        settings.panel_name = request.form.get('panel_name', settings.panel_name)
        settings.logo_url = request.form.get('logo_url', settings.logo_url)
        settings.background_url = request.form.get('background_url', settings.background_url)
        settings.welcome_text = request.form.get('welcome_text', settings.welcome_text)
        
        db.session.commit()
        flash('Settings updated successfully', 'success')
        return redirect(url_for('admin_settings'))
    
    user = User.query.get(session['user_id'])
    return render_template('admin_settings.html', settings=settings, user=user)

# Initialize database
def init_db():
    with app.app_context():
        db.create_all()
        
        # Create default settings if not exists
        if not Settings.query.first():
            settings = Settings()
            db.session.add(settings)
            db.session.commit()
        
        logger.info("Database initialized successfully")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
