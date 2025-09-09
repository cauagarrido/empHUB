# emphub/core/decorators.py
from functools import wraps
from flask import request, jsonify
from emphub.core.supabase_client import supabase

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Formato do token inválido. Use "Bearer <token>".'}), 401

        if not token:
            return jsonify({'message': 'Token de autenticação está faltando!'}), 401

        try:
            user_response = supabase.auth.get_user(token)
            current_user = user_response.user
            if not current_user:
                 return jsonify({'message': 'Token inválido ou expirado!'}), 401
        except Exception:
            return jsonify({'message': 'Erro na validação do token!'}), 401
        
        return f(current_user=current_user, *args, **kwargs)
    return decorated