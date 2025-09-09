
from flask import Blueprint, request, jsonify
from emphub.core.supabase_client import supabase
from emphub.core.decorators import token_required
from emphub.utils import generate_unique_code

groups_bp = Blueprint('groups', __name__)

@groups_bp.route('/create', methods=['POST'])
@token_required
def create_group(current_user):
    data = request.get_json()
    group_name = data.get('name')

    if not group_name:
        return jsonify({'message': 'O nome do grupo é obrigatório!'}), 400
    
    user_id = current_user.id
    unique_code = generate_unique_code()

    try:
        group_res = supabase.table('groups').insert({
            'name': group_name, 'owner_id': user_id, 'invite_code': unique_code
        }).execute()
        
        new_group = group_res.data[0]
        
        supabase.table('group_members').insert({
            'group_id': new_group['id'], 'user_id': user_id
        }).execute()
        
        return jsonify({
            'message': 'Grupo criado com sucesso!',
            'group': new_group
        }), 201
    except Exception as e:
        return jsonify({'message': f"Erro ao criar grupo: {e}"}), 500

@groups_bp.route('/join', methods=['POST'])
@token_required
def join_group(current_user):
    data = request.get_json()
    invite_code = data.get('invite_code')

    if not invite_code:
        return jsonify({'message': 'Código de convite é obrigatório!'}), 400
    
    try:
        group_res = supabase.table('groups').select('id').eq('invite_code', invite_code).single().execute()
        group_id = group_res.data['id']
        user_id = current_user.id

        membership_check = supabase.table('group_members').select('user_id').eq('group_id', group_id).eq('user_id', user_id).execute()
        if membership_check.data:
            return jsonify({'message': 'Você já é membro deste grupo!'}), 409

        supabase.table('group_members').insert({'group_id': group_id, 'user_id': user_id}).execute()
        
        return jsonify({'message': 'Você entrou no grupo com sucesso!', 'group_id': group_id}), 200
    except Exception:
        return jsonify({'message': 'Código de convite inválido ou erro ao processar.'}), 404