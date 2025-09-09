# emphub/api/auth.py
from flask import Blueprint, request, jsonify
from emphub.core.supabase_client import supabase

# Cria um Blueprint. O primeiro argumento é o nome do blueprint, o segundo é o nome do módulo.
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')

    if not all([email, password, full_name]):
        return jsonify({'message': 'Dados incompletos!'}), 400
    if len(password) < 8:
        return jsonify({'message': 'Senha deve ter no mínimo 8 caracteres.'}), 400

    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        if res.user:
            profile_data = {'id': res.user.id, 'full_name': full_name}
            supabase.table('profiles').insert(profile_data).execute()
            return jsonify({'message': 'Usuário registrado com sucesso! Verifique seu email.'}), 201
        return jsonify({'message': 'Erro ao registrar. O email pode já estar em uso.'}), 400
    except Exception as e:
        return jsonify({'message': f"Erro no registro: {e}"}), 500


@auth_bp.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email e senha são obrigatórios!'}), 400

    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return jsonify({
            'message': 'Login bem-sucedido!',
            'access_token': res.session.access_token,
            'user': res.user.dict()
        }), 200
    except Exception:
        return jsonify({'message': 'Credenciais inválidas!'}), 401