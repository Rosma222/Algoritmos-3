from flask import Blueprint, request, jsonify, session
from app.models import db
from app.models.user import User
from app.models.rubro import Rubro

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'client') # 'client' or 'representative'
    rubro_id = data.get('rubro_id')

    if not username or not email or not password:
        return jsonify({'error': 'Faltan datos obligatorios (username, email, password)'}), 400

    # Verificar duplicación de usuarios
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        return jsonify({'error': 'El nombre de usuario o correo electrónico ya está registrado.'}), 400

    if role == 'representative' and not rubro_id:
        return jsonify({'error': 'Los representantes deben estar asociados a un rubro de especialización.'}), 400

    user = User(username=username, email=email, role=role, rubro_id=rubro_id if role == 'representative' else None)
    user.set_password(password)

    db.session.add(user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

    return jsonify({'message': 'Usuario registrado con éxito', 'user': user.to_dict()}), 201

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        session['user_id'] = user.id
        session['role'] = user.role
        session['username'] = user.username
        return jsonify({'message': 'Login exitoso', 'user': user.to_dict()}), 200

    return jsonify({'error': 'Credenciales inválidas'}), 401

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Sesión cerrada'}), 200

@auth_bp.route('/api/session', methods=['GET'])
def get_session():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'logged_in': False}), 200
    user = User.query.get(user_id)
    if not user:
        session.clear()
        return jsonify({'logged_in': False}), 200
    return jsonify({'logged_in': True, 'user': user.to_dict()}), 200

@auth_bp.route('/api/users', methods=['GET'])
def list_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users]), 200

@auth_bp.route('/api/representatives', methods=['GET'])
def list_representatives():
    reps = User.query.filter_by(role='representative').all()
    return jsonify([r.to_dict() for r in reps]), 200
