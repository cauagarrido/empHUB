# emphub/api/projects.py
from flask import Blueprint, request, jsonify
from emphub.core.supabase_client import supabase
from emphub.core.decorators import token_required

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/<int:group_id>/projects', methods=['GET'])
@token_required
def get_projects(current_user, group_id):
    # Em produção: verificar se o usuário pertence ao grupo group_id
    try:
        res = supabase.table('projects').select('*').eq('group_id', group_id).execute()
        return jsonify(res.data), 200
    except Exception as e:
        return jsonify({'message': f"Erro ao buscar projetos: {e}"}), 500

@projects_bp.route('/<int:group_id>/projects', methods=['POST'])
@token_required
def create_project(current_user, group_id):
    data = request.get_json()
    if not data.get('title'):
        return jsonify({'message': 'O título do projeto é obrigatório.'}), 400
    
    new_project = {
        'group_id': group_id,
        'title': data['title'],
        'description': data.get('description', ''),
        'status': 'Novo Projeto'
    }
    try:
        res = supabase.table('projects').insert(new_project).execute()
        return jsonify(res.data[0]), 201
    except Exception as e:
        return jsonify({'message': f"Erro ao criar projeto: {e}"}), 500

@projects_bp.route('/<int:project_id>/status', methods=['PUT'])
@token_required
def update_project_status(current_user, project_id):
    data = request.get_json()
    new_status = data.get('status')
    # Adicionar validação de status
    try:
        res = supabase.table('projects').update({'status': new_status}).eq('id', project_id).execute()
        return jsonify(res.data[0]), 200
    except Exception as e:
        return jsonify({'message': f"Erro ao atualizar status: {e}"}), 500

@projects_bp.route('/<int:project_id>/assign', methods=['POST'])
@token_required
def assign_project(current_user, project_id):
    try:
        res = supabase.table('projects').update({'assignee_id': current_user.id}).eq('id', project_id).execute()
        return jsonify(res.data[0]), 200
    except Exception as e:
        return jsonify({'message': f"Erro ao se atribuir ao projeto: {e}"}), 500