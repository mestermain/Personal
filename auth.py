from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, AdminUser

auth_bp = Blueprint('auth', __name__, url_prefix='/admin')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False
        
        user = AdminUser.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('Invalid username or password. Please try again.', 'danger')
            return redirect(url_for('auth.login'))
            
        login_user(user, remember=remember)
        flash(f'Welcome back, {user.username}!', 'success')
        
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/admin'):
            return redirect(next_page)
        return redirect(url_for('admin.dashboard'))
        
    return render_template('admin/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
