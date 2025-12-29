#!/usr/bin/env python3
"""
user_manager.py - User Authentication and Storage Management

This module handles user registration, authentication, and storage allocation
for the VM simulation web interface.
"""

import os
try:
    from params import from_email as PARAMS_FROM_EMAIL, app_password as PARAMS_APP_PASSWORD
except ImportError:
    PARAMS_FROM_EMAIL = None
    PARAMS_APP_PASSWORD = None
import json
import hashlib
import secrets
import time
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from firebase_admin_init import db

class UserManager:
    """Manages user accounts and storage allocation"""
    
    def __init__(self, users_db_path='users.json'):
        self.users_db_path = users_db_path
<<<<<<< HEAD
        self.sessions_db_path = 'sessions.json'
        self.users = self.load_users()
        self.sessions = self.load_sessions()  # Persistent session storage
        self.otp_codes = {}  # In-memory OTP storage (OTP codes don't need persistence)
=======
        self.users = self.load_users()
        self.sessions = {}  # In-memory session storage
        self.otp_codes = {}  # In-memory OTP storage
>>>>>>> dcc23283299fd52299056f72a0ebb8c36529738e
        self.DEFAULT_STORAGE_GB = 2  # 2GB per user
        
        # Email configuration - read from environment variables to avoid hardcoding secrets
        # Set these in your environment before running the server:
        # SMTP_SERVER (default: smtp.gmail.com), SMTP_PORT (default: 587)
        # SMTP_USER (the sending email), SMTP_APP_PASSWORD or SMTP_PASS (app/password)
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        try:
            self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        except Exception:
            self.smtp_port = 587
        self.from_email = os.getenv('SMTP_USER') or PARAMS_FROM_EMAIL
        self.app_password = os.getenv('SMTP_APP_PASSWORD') or os.getenv('SMTP_PASS') or PARAMS_APP_PASSWORD
    
    def load_users(self):
        """Load users from JSON database"""
        if os.path.exists(self.users_db_path):
            try:
                with open(self.users_db_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}
<<<<<<< HEAD

    def load_sessions(self):
        """Load sessions from JSON database"""
        if os.path.exists(self.sessions_db_path):
            try:
                with open(self.sessions_db_path, 'r') as f:
                    sessions = json.load(f)
                    # Clean expired sessions
                    current_time = time.time()
                    valid_sessions = {k: v for k, v in sessions.items() if current_time < v.get('expires_at', 0)}
                    if len(valid_sessions) != len(sessions):
                        self.save_sessions(valid_sessions)
                    return valid_sessions
            except json.JSONDecodeError:
                return {}
        return {}

=======
    
>>>>>>> dcc23283299fd52299056f72a0ebb8c36529738e
    def save_users(self):
        """Save users to JSON database"""
        with open(self.users_db_path, 'w') as f:
            json.dump(self.users, f, indent=2)
<<<<<<< HEAD

    def save_sessions(self, sessions=None):
        """Save sessions to JSON database"""
        if sessions is None:
            sessions = self.sessions
        with open(self.sessions_db_path, 'w') as f:
            json.dump(sessions, f, indent=2)
=======
>>>>>>> dcc23283299fd52299056f72a0ebb8c36529738e
    
    def hash_password(self, password):
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', 
                                          password.encode('utf-8'), 
                                          salt.encode('utf-8'), 
                                          100000)
        return salt + password_hash.hex()
    
    def verify_password(self, password, hashed):
        """Verify password against hash"""
        if len(hashed) < 32:
            return False
        salt = hashed[:32]
        stored_hash = hashed[32:]
        password_hash = hashlib.pbkdf2_hmac('sha256',
                                          password.encode('utf-8'),
                                          salt.encode('utf-8'),
                                          100000)
        return password_hash.hex() == stored_hash
    
    def validate_registration_data(self, username, email, phone, password):
        """Validate registration data without creating user"""
        # Validate input
        if not username or not email or not phone or not password:
            return {'success': False, 'message': 'All fields are required'}
        
        if len(username) < 3:
            return {'success': False, 'message': 'Username must be at least 3 characters'}
        
        if len(password) < 6:
            return {'success': False, 'message': 'Password must be at least 6 characters'}
        
        # Validate email format
        import re
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, email):
            return {'success': False, 'message': 'Invalid email format'}
        
        # Check if user already exists
        if any(user.get('email', '').lower() == email.lower() for user in self.users.values()):
            return {'success': False, 'message': 'Email already registered'}
        
        if any(user.get('phone', '') == phone for user in self.users.values()):
            return {'success': False, 'message': 'Phone number already registered'}
        
        return {'success': True, 'message': 'Validation passed'}
    
    def register_user(self, username, email, phone, password):
        """Register a new user"""
        # Validate input first
        validation = self.validate_registration_data(username, email, phone, password)
        if not validation['success']:
            return validation
        
        # Create user account
        user_id = f"user_{int(time.time())}_{secrets.token_hex(4)}"
        user_data = {
            'user_id': user_id,
            'username': username,
            'email': email,
            'phone': phone,
            'password_hash': self.hash_password(password),
            'storage_allocated_gb': self.DEFAULT_STORAGE_GB,
            'storage_used_bytes': 0,
            'verified': True,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'is_active': True,
<<<<<<< HEAD
            'is_admin': False,  # New users are not admins by default
=======
>>>>>>> dcc23283299fd52299056f72a0ebb8c36529738e
            'files': []
        }
        
        # Create user storage directory
        user_storage_path = f'cloud_storage/user_files/{username}'
        os.makedirs(user_storage_path, exist_ok=True)
        
        # Save user (use email as key)
        self.users[email] = user_data
        self.save_users()
        
        return {
            'success': True, 
            'message': f'User {username} registered successfully with {self.DEFAULT_STORAGE_GB}GB storage',
            'user_id': user_id,
            'storage_allocated': self.DEFAULT_STORAGE_GB
        }
    
    def authenticate_user(self, email, password):
        """Authenticate user login using email"""
        if email not in self.users:
            return {'success': False, 'message': 'Invalid email or password'}
        
        user = self.users[email]
        if not user.get('is_active', True):
            return {'success': False, 'message': 'Account is disabled'}
        
        if not self.verify_password(password, user['password_hash']):
            return {'success': False, 'message': 'Invalid email or password'}
        
        # Update last login
        user['last_login'] = datetime.now().isoformat()
        self.save_users()
        
        # Create session
        session_token = secrets.token_urlsafe(32)
        self.sessions[session_token] = {
            'email': email,
            'username': user['username'],
            'user_id': user['user_id'],
            'created_at': time.time(),
<<<<<<< HEAD
            'expires_at': time.time() + 315360000  # 10 years (365*10 days)
        }
        self.save_sessions()  # Persist session
=======
            'expires_at': time.time() + 86400  # 24 hours
        }
>>>>>>> dcc23283299fd52299056f72a0ebb8c36529738e
        
        return {
            'success': True,
            'message': 'Login successful',
            'session_token': session_token,
            'user': {
                'username': user['username'],
                'user_id': user['user_id'],
                'email': user['email'],
                'phone': user['phone'],
                'storage_allocated_gb': user['storage_allocated_gb'],
                'storage_used_bytes': user['storage_used_bytes']
            }
        }
    
    def get_user_from_session(self, session_token):
        """Get user data from session token"""
        if not session_token or session_token not in self.sessions:
            return None
        
        session = self.sessions[session_token]
        if time.time() > session['expires_at']:
            del self.sessions[session_token]
            return None
        
        email = session['email']
        if email not in self.users:
            return None
        
        return self.users[email]
    
    def logout_user(self, session_token):
        """Logout user by removing session"""
        if session_token in self.sessions:
            del self.sessions[session_token]
<<<<<<< HEAD
            self.save_sessions()  # Persist changes
        return {'success': True, 'message': 'Logged out successfully'}

    def create_permanent_session(self, email):
        """Create a permanent session for a user (never expires)"""
        if email not in self.users:
            return None

        user = self.users[email]
        session_token = secrets.token_urlsafe(32)
        self.sessions[session_token] = {
            'email': email,
            'username': user['username'],
            'user_id': user['user_id'],
            'created_at': time.time(),
            'expires_at': time.time() + 3153600000  # 100 years (effectively never expires)
        }
        self.save_sessions()
        return session_token
    
    def is_user_admin(self, session_token):
        """Check if user has admin privileges"""
        user = self.get_user_from_session(session_token)
        if not user:
            return False
        return user.get('is_admin', False)
    
    def verify_admin_password(self, session_token, password):
        """Verify admin access with password re-authentication"""
        user = self.get_user_from_session(session_token)
        if not user:
            return {'success': False, 'message': 'Invalid session'}
        
        if not user.get('is_admin', False):
            return {'success': False, 'message': 'Access denied: Admin privileges required'}
        
        if not self.verify_password(password, user['password_hash']):
            return {'success': False, 'message': 'Invalid password'}
        
        return {'success': True, 'message': 'Admin access granted'}
=======
        return {'success': True, 'message': 'Logged out successfully'}
>>>>>>> dcc23283299fd52299056f72a0ebb8c36529738e
    
    def generate_otp(self):
        """Generate a cryptographically secure 6-digit OTP code"""
        return f"{secrets.randbelow(900000) + 100000}"
    
    def send_otp_email(self, email, otp_code, purpose='verification'):
        """Send OTP via email"""
        try:
            # Basic SMTP config presence check
            if not self.from_email or not self.app_password:
                return {'success': False, 'message': 'SMTP credentials not configured. Set SMTP_USER and SMTP_APP_PASSWORD (or SMTP_PASS) in environment.'}

            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = email
            
            if purpose == 'verification':
<<<<<<< HEAD
                msg['Subject'] = 'GUI Storage - Email Verification'
=======
                msg['Subject'] = 'VM Cloud Storage - Email Verification'
>>>>>>> dcc23283299fd52299056f72a0ebb8c36529738e
                html_body = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }}
                        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
                        .header {{ text-align: center; margin-bottom: 30px; }}
                        .logo {{ font-size: 2em; margin-bottom: 10px; }}
                        .title {{ color: #2c3e50; font-size: 1.5em; margin-bottom: 20px; }}
                        .otp-box {{ background: linear-gradient(135deg, #3498db, #2980b9); color: white; padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0; }}
                        .otp-code {{ font-size: 2em; font-weight: bold; letter-spacing: 5px; margin: 10px 0; }}
                        .info {{ background: #e8f4fd; padding: 15px; border-radius: 8px; border-left: 4px solid #3498db; margin: 20px 0; }}
                        .footer {{ text-align: center; color: #7f8c8d; font-size: 0.9em; margin-top: 30px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <div class="logo">🌐</div>
                            <div class="title">VM Cloud Storage</div>
                        </div>
                        
                        <h2>Email Verification Required</h2>
<<<<<<< HEAD
                        <p>Welcome to GUI Storage! To complete your registration, please verify your email address using the code below:</p>
=======
                        <p>Welcome to VM Cloud Storage! To complete your registration, please verify your email address using the code below:</p>
>>>>>>> dcc23283299fd52299056f72a0ebb8c36529738e
                        
                        <div class="otp-box">
                            <div>Your Verification Code</div>
                            <div class="otp-code">{otp_code}</div>
                        </div>
                        
                        <div class="info">
                            <strong>📋 Instructions:</strong>
                            <ul>
                                <li>Enter this code in the verification form</li>
                                <li>This code is valid for 10 minutes</li>
                                <li>Don't share this code with anyone</li>
                                <li>If you didn't request this, please ignore this email</li>
                            </ul>
                        </div>
                        
                        <p>Once verified, you'll get access to:</p>
                        <ul>
                            <li>✅ 2GB of free cloud storage</li>
                            <li>✅ File upload and management</li>
                            <li>✅ VM node creation and management</li>
                            <li>✅ Secure file sharing</li>
                        </ul>
                        
                        <div class="footer">
<<<<<<< HEAD
                            <p>This is an automated message from GUI Storage<br>
=======
                            <p>This is an automated message from VM Cloud Storage<br>
>>>>>>> dcc23283299fd52299056f72a0ebb8c36529738e
                            © 2024 VM Simulation System</p>
                        </div>
                    </div>
                </body>
                </html>
                """
            else:  # login verification
<<<<<<< HEAD
                msg['Subject'] = 'GUI Storage - Login Verification'
=======
                msg['Subject'] = 'VM Cloud Storage - Login Verification'
>>>>>>> dcc23283299fd52299056f72a0ebb8c36529738e
                html_body = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }}
                        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
                        .header {{ text-align: center; margin-bottom: 30px; }}
                        .logo {{ font-size: 2em; margin-bottom: 10px; }}
                        .title {{ color: #2c3e50; font-size: 1.5em; margin-bottom: 20px; }}
                        .otp-box {{ background: linear-gradient(135deg, #27ae60, #2ecc71); color: white; padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0; }}
                        .otp-code {{ font-size: 2em; font-weight: bold; letter-spacing: 5px; margin: 10px 0; }}
                        .warning {{ background: #fff3cd; color: #856404; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107; margin: 20px 0; }}
                        .footer {{ text-align: center; color: #7f8c8d; font-size: 0.9em; margin-top: 30px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <div class="logo">🔐</div>
<<<<<<< HEAD
                            <div class="title">GUI Storage</div>
                        </div>
                        
                        <h2>Login Verification</h2>
                        <p>Someone is trying to access your GUI Storage account. If this was you, use the verification code below to complete your login:</p>
=======
                            <div class="title">VM Cloud Storage</div>
                        </div>
                        
                        <h2>Login Verification</h2>
                        <p>Someone is trying to access your VM Cloud Storage account. If this was you, use the verification code below to complete your login:</p>
>>>>>>> dcc23283299fd52299056f72a0ebb8c36529738e
                        
                        <div class="otp-box">
                            <div>Your Login Code</div>
                            <div class="otp-code">{otp_code}</div>
                        </div>
                        
                        <div class="warning">
                            <strong>🛡️ Security Notice:</strong>
                            <ul>
                                <li>This code expires in 5 minutes</li>
                                <li>Never share this code with anyone</li>
                                <li>If you didn't try to login, change your password immediately</li>
                            </ul>
                        </div>
                        
                        <p><strong>Login Details:</strong></p>
                        <ul>
                            <li>📧 Email: {email}</li>
                            <li>⏰ Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</li>
                        </ul>
                        
                        <div class="footer">
<<<<<<< HEAD
                            <p>This is an automated security message from GUI Storage<br>
=======
                            <p>This is an automated security message from VM Cloud Storage<br>
>>>>>>> dcc23283299fd52299056f72a0ebb8c36529738e
                            © 2024 VM Simulation System</p>
                        </div>
                    </div>
                </body>
                </html>
                """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=20)
            server.ehlo()
            try:
                server.starttls()
                server.ehlo()
            except Exception:
                # If STARTTLS fails or is not supported, continue and attempt login
                pass
            server.login(self.from_email, self.app_password)

            # Send email
            text = msg.as_string()
            server.sendmail(self.from_email, email, text)
            server.quit()

            return {'success': True, 'message': 'OTP sent successfully'}
            
        except Exception as e:
            print(f"Failed to send OTP email: {str(e)}")
            return {'success': False, 'message': f'Failed to send email: {str(e)}'}
    
    def send_registration_otp(self, email):
        """Send OTP for registration verification"""
        otp_code = self.generate_otp()
        
        # Store OTP with expiration (10 minutes for registration)
        self.otp_codes[email] = {
            'code': otp_code,
            'purpose': 'registration',
            'expires_at': time.time() + 600,  # 10 minutes
            'attempts': 0
        }
        
        result = self.send_otp_email(email, otp_code, 'verification')
        if result['success']:
            return {'success': True, 'message': 'Verification code sent to your email'}
        else:
            return result
    
    def send_login_otp(self, email):
        """Send OTP for login verification"""
        otp_code = self.generate_otp()
        
        # Store OTP with expiration (5 minutes for login)
        self.otp_codes[email] = {
            'code': otp_code,
            'purpose': 'login',
            'expires_at': time.time() + 300,  # 5 minutes
            'attempts': 0
        }
        
        result = self.send_otp_email(email, otp_code, 'login')
        if result['success']:
            return {'success': True, 'message': 'Login code sent to your email'}
        else:
            return result
    
    def verify_otp(self, email, entered_otp, purpose='registration'):
        """Verify OTP code"""
        if email not in self.otp_codes:
            return {'success': False, 'message': 'No verification code found. Please request a new one.'}
        
        otp_data = self.otp_codes[email]
        
        # Check expiration
        if time.time() > otp_data['expires_at']:
            del self.otp_codes[email]
            return {'success': False, 'message': 'Verification code has expired. Please request a new one.'}
        
        # Check purpose
        if otp_data['purpose'] != purpose:
            return {'success': False, 'message': 'Invalid verification code for this operation.'}
        
        # Check attempts (max 3 attempts)
        if otp_data['attempts'] >= 3:
            del self.otp_codes[email]
            return {'success': False, 'message': 'Too many failed attempts. Please request a new code.'}
        
        # Verify code
        if entered_otp != otp_data['code']:
            otp_data['attempts'] += 1
            remaining = 3 - otp_data['attempts']
            if remaining > 0:
                return {'success': False, 'message': f'Invalid code. {remaining} attempts remaining.'}
            else:
                del self.otp_codes[email]
                return {'success': False, 'message': 'Invalid code. Maximum attempts exceeded.'}
        
        # Success - remove OTP
        del self.otp_codes[email]
        return {'success': True, 'message': 'Verification successful'}
    
    def update_user_storage(self, username, file_size, operation='add'):
        """Update user storage usage"""
        # Users are keyed by email in the users DB. Find the email for the provided username.
        user_email = None
        for e, u in self.users.items():
            if u.get('username') == username or e == username:
                user_email = e
                break

        if not user_email:
            return False

        user = self.users[user_email]
        if operation == 'add':
            new_usage = user['storage_used_bytes'] + file_size
            if new_usage > user['storage_allocated_gb'] * 1024 * 1024 * 1024:
                return False  # Storage exceeded
            user['storage_used_bytes'] = new_usage
        elif operation == 'remove':
            user['storage_used_bytes'] = max(0, user['storage_used_bytes'] - file_size)
<<<<<<< HEAD

        self.save_users()
        return True

    def update_user_storage_allocation(self, username, new_allocation_gb):
        """Update user's storage allocation"""
        user_email = None
        for e, u in self.users.items():
            if u.get('username') == username or e == username:
                user_email = e
                break

        if not user_email:
            return False

        user = self.users[user_email]
        user['storage_allocated_gb'] = new_allocation_gb
=======
        
>>>>>>> dcc23283299fd52299056f72a0ebb8c36529738e
        self.save_users()
        return True
    
    def get_user_files(self, username):
        """Get user's files list"""
        # Resolve username to stored email key (users dict keyed by email)
        user_email = None
        for e, u in self.users.items():
            if u.get('username') == username or e == username:
                user_email = e
                break

        if not user_email:
            return []
        
        user_files = []
        user_storage_path = f'cloud_storage/user_files/{username}'
        metadata_dir = 'cloud_storage/metadata'
        
        # Scan user's uploaded files
        if os.path.exists(metadata_dir):
            for metadata_file in os.listdir(metadata_dir):
                if metadata_file.endswith('.json'):
                    try:
                        with open(os.path.join(metadata_dir, metadata_file), 'r') as f:
                            file_meta = json.load(f)
                        
                        # Check if file belongs to this user
                        if file_meta.get('owner_username') == username:
                            user_files.append({
                                'file_id': file_meta.get('file_id', ''),
                                'filename': file_meta.get('filename', ''),
                                'size': file_meta.get('size', 0),
                                'upload_date': file_meta.get('upload_date', ''),
                                'checksum': file_meta.get('checksum', ''),
                                'file_type': self.get_file_type(file_meta.get('filename', '')),
                                'shared': file_meta.get('shared', False)
                            })
                    except json.JSONDecodeError:
                        continue
        
        return sorted(user_files, key=lambda x: x['upload_date'], reverse=True)
    
    def get_file_type(self, filename):
        """Determine file type from filename"""
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        type_mapping = {
            # Images
            'jpg': 'image', 'jpeg': 'image', 'png': 'image', 'gif': 'image', 'bmp': 'image', 'svg': 'image',
            # Documents
            'pdf': 'document', 'doc': 'document', 'docx': 'document', 'txt': 'document', 'rtf': 'document',
            # Spreadsheets
            'xls': 'spreadsheet', 'xlsx': 'spreadsheet', 'csv': 'spreadsheet',
            # Presentations
            'ppt': 'presentation', 'pptx': 'presentation',
            # Archives
            'zip': 'archive', 'rar': 'archive', '7z': 'archive', 'tar': 'archive', 'gz': 'archive',
            # Video
            'mp4': 'video', 'avi': 'video', 'mkv': 'video', 'mov': 'video', 'wmv': 'video',
            # Audio
            'mp3': 'audio', 'wav': 'audio', 'flac': 'audio', 'ogg': 'audio',
            # Code
            'py': 'code', 'js': 'code', 'html': 'code', 'css': 'code', 'cpp': 'code', 'java': 'code'
        }
        
        return type_mapping.get(ext, 'file')

class FirestoreUserManager(UserManager):
    def save_user_firestore(self, user_data):
        users_ref = db.collection('users')
        users_ref.document(user_data['email']).set(user_data)

    def get_user_firestore(self, email):
        users_ref = db.collection('users')
        doc = users_ref.document(email).get()
        return doc.to_dict() if doc.exists else None

    def register_user(self, username, email, phone, password):
        validation = self.validate_registration_data(username, email, phone, password)
        if not validation['success']:
            return validation
        user_id = f"user_{int(time.time())}_{secrets.token_hex(4)}"
        user_data = {
            'user_id': user_id,
            'username': username,
            'email': email,
            'phone': phone,
            'password_hash': self.hash_password(password),
            'storage_allocated_gb': self.DEFAULT_STORAGE_GB,
            'storage_used_bytes': 0,
            'verified': True,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'is_active': True,
            'files': []
        }
        self.save_user_firestore(user_data)
        return {
            'success': True,
            'message': f'User {username} registered successfully with {self.DEFAULT_STORAGE_GB}GB storage',
            'user_id': user_id,
            'storage_allocated': self.DEFAULT_STORAGE_GB
        }

    def authenticate_user(self, email, password):
        user = self.get_user_firestore(email)
        if not user:
            return {'success': False, 'message': 'Invalid email or password'}
        if not user.get('is_active', True):
            return {'success': False, 'message': 'Account is disabled'}
        if not self.verify_password(password, user['password_hash']):
            return {'success': False, 'message': 'Invalid email or password'}
        user['last_login'] = datetime.now().isoformat()
        self.save_user_firestore(user)
        session_token = secrets.token_urlsafe(32)
        self.sessions[session_token] = {
            'email': email,
            'username': user['username'],
            'user_id': user['user_id'],
            'created_at': time.time(),
<<<<<<< HEAD
            'expires_at': time.time() + 315360000  # 10 years (365*10 days)
        }
        self.save_sessions()  # Persist session
=======
            'expires_at': time.time() + 86400
        }
>>>>>>> dcc23283299fd52299056f72a0ebb8c36529738e
        return {
            'success': True,
            'message': 'Login successful',
            'session_token': session_token,
            'user': {
                'username': user['username'],
                'user_id': user['user_id'],
                'email': user['email'],
                'phone': user['phone'],
                'storage_allocated_gb': user['storage_allocated_gb'],
                'storage_used_bytes': user['storage_used_bytes']
            }
        }