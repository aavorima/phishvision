from flask import Blueprint, request, jsonify, session
from datetime import datetime
from database import db
from models import User, Settings

bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.json

    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Username, email and password are required'}), 400

    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400

    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        role='admin' if User.query.count() == 0 else 'user'  # First user is admin
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    # Create default settings for user
    settings = Settings(user_id=user.id)
    db.session.add(settings)
    db.session.commit()

    # Set session
    session['user_id'] = user.id
    session.permanent = True

    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict()
    }), 201


@bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    data = request.json

    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400

    # Find user by username or email
    user = User.query.filter(
        (User.username == data['username']) | (User.email == data['username'])
    ).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401

    if not user.is_active:
        return jsonify({'error': 'Account is disabled'}), 403

    # Update last login
    user.last_login_at = datetime.utcnow()
    db.session.commit()

    # Set session
    session['user_id'] = user.id
    session.permanent = True

    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    })


@bp.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'})


@bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current logged in user"""
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401

    user = User.query.get(user_id)

    if not user:
        session.pop('user_id', None)
        return jsonify({'error': 'User not found'}), 404

    return jsonify(user.to_dict())


@bp.route('/me', methods=['PUT'])
def update_current_user():
    """Update current user profile"""
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.json

    if data.get('first_name') is not None:
        user.first_name = data['first_name']
    if data.get('last_name') is not None:
        user.last_name = data['last_name']
    if data.get('email'):
        # Check if email is taken by another user
        existing = User.query.filter(User.email == data['email'], User.id != user.id).first()
        if existing:
            return jsonify({'error': 'Email already in use'}), 400
        user.email = data['email']

    db.session.commit()

    return jsonify({
        'message': 'Profile updated successfully',
        'user': user.to_dict()
    })


@bp.route('/change-password', methods=['POST'])
def change_password():
    """Change user password"""
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.json

    if not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Current and new password are required'}), 400

    if not user.check_password(data['current_password']):
        return jsonify({'error': 'Current password is incorrect'}), 400

    if len(data['new_password']) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    user.set_password(data['new_password'])
    db.session.commit()

    return jsonify({'message': 'Password changed successfully'})
