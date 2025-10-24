#!/usr/bin/env python3
"""
Script to add admin user to GVM Panel
Usage: python add_admin.py
"""

from app import app, db, User
from werkzeug.security import generate_password_hash

def add_admin_user():
    """Add admin user with username 'admin' and password 'admin'"""
    with app.app_context():
        # Initialize database
        db.create_all()
        
        # Check if admin user already exists
        existing_admin = User.query.filter_by(username='admin').first()
        
        if existing_admin:
            print(f"⚠️  User 'admin' already exists!")
            print(f"   User ID: {existing_admin.id}")
            print(f"   Email: {existing_admin.email}")
            print(f"   Role: {existing_admin.role}")
            print(f"   Credits: {existing_admin.credits}")
            
            # Update password and ensure admin role
            existing_admin.password = generate_password_hash('admin')
            existing_admin.role = 'admin'
            if existing_admin.credits < 10000:
                existing_admin.credits = 10000
            
            db.session.commit()
            print("\n✅ Updated existing admin user:")
            print("   Username: admin")
            print("   Password: admin")
            print(f"   Role: {existing_admin.role}")
            print(f"   Credits: {existing_admin.credits}")
        else:
            # Create new admin user
            hashed_password = generate_password_hash('admin')
            admin_user = User(
                username='admin',
                email='admin@gvmpanel.local',
                password=hashed_password,
                role='admin',
                credits=10000
            )
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("✅ Admin user created successfully!")
            print("   Username: admin")
            print("   Password: admin")
            print("   Email: admin@gvmpanel.local")
            print("   Role: admin")
            print("   Credits: 10000")
        
        print("\n📋 All users in database:")
        all_users = User.query.all()
        for user in all_users:
            print(f"   - {user.username} ({user.role}) - Credits: {user.credits}")

if __name__ == '__main__':
    add_admin_user()
