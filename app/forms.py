"""Authentication forms."""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models.user import User


class SignupForm(FlaskForm):
    """User signup form."""
    
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address')
    ])
    
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=100, message='Username must be between 3 and 100 characters')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    
    submit = SubmitField('Sign Up')
    
    def validate_email(self, email):
        """Check if email already exists."""
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('This email is already registered. Please login instead.')
    
    def validate_username(self, username):
        """Check if username already exists."""
        user = User.query.filter_by(username=username.data.lower()).first()
        if user:
            raise ValidationError('This username is already taken. Please choose another.')


class LoginForm(FlaskForm):
    """User login form."""
    
    email = StringField('Email or Username', validators=[
        DataRequired()
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    
    remember = BooleanField('Remember Me')
    
    submit = SubmitField('Log In')
