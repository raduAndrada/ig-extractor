"""Authentication routes blueprint."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models.user import User
from app.forms import SignupForm, LoginForm
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """User signup page."""
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = SignupForm()
    
    if form.validate_on_submit():
        try:
            # Create new user
            user = User(
                email=form.email.data.lower(),
                username=form.username.data.lower()
            )
            user.set_password(form.password.data)
            
            # Save to database
            db.session.add(user)
            db.session.commit()
            
            # Log the user in
            login_user(user)
            
            logger.info(f"New user registered: {user.username}")
            flash(f'Welcome {user.username}! Your account has been created.', 'success')
            
            return redirect(url_for('main.index'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Signup failed: {e}")
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template('auth/signup.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Find user by email or username
        user = User.query.filter(
            (User.email == form.email.data.lower()) |
            (User.username == form.email.data.lower())
        ).first()
        
        # Check password
        if user and user.check_password(form.password.data):
            # Update last login
            from datetime import datetime
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Log the user in
            login_user(user, remember=form.remember.data)
            
            logger.info(f"User logged in: {user.username}")
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Invalid email/username or password. Please try again.', 'danger')
    
    return render_template('auth/login.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    """Logout user."""
    username = current_user.username
    logout_user()
    logger.info(f"User logged out: {username}")
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
