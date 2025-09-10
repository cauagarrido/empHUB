from flask import Blueprint, request, jsonify
from emphub.core.supabase_client import supabase
from emphub.core.decorators import token_required
from emphub.utils import generate_unique_code

groups_bp = Blueprint('groups', __name__)

# --- FUNÇÃO AUXILIAR PARA VERIFICAR O LIMITE DE USUÁRIOS ---
# Colocamos a lógica aqui para manter a rota 'join_group' mais limpa e legível.
def _check_user_limit(group_id):
    """
    Verifica se um grupo atingiu o limite de usuários do seu plano.
    Retorna uma tupla: (pode_adicionar_membro, mensagem_de_erro)
    """
    try:
        # 1. Busca o grupo e, através de um JOIN, pega o limite de usuários do seu plano.
        group_plan_res = supabase.table('groups').select('plan:plan_id(max_users)').eq('id', group_id).single().execute()
        
        # Se o grupo ou o plano não forem encontrados, algo está errado.
        if not group_plan_res.data or not group_plan_res.data.get('plan'):
            return False, "Não foi possível verificar o plano de assinatura do grupo."

        plan_limits = group_plan_res.data.get('plan')
        limit = plan_limits.get('max_users')

        # 2. Se o limite for NULL, significa que é ilimitado (plano Pro), então permite a entrada.
        if limit is None:
            return True, ""

        # 3. Se houver um limite, conta o número atual de membros.
        count_res = supabase.table('group_members').select('user_id', count='exact').eq('group_id', group_id).execute()
        current_count = count_res.count
        
        # 4. Compara o número atual com o limite.
        if current_count >= limit:
            # Se o limite foi atingido ou ultrapassado, bloqueia a entrada.
            return False, f"Limite de {limit} usuários atingido. Peça ao administrador para fazer upgrade do plano."
        
        # Se o limite não foi atingido, permite a entrada.
        return True, ""

    except Exception as e:
        return False, f"Erro interno ao verificar o limite de usuários: {str(e)}"

# --- ROTAS ---

@groups_bp.route('/create', methods=['POST'])
@token_required
def create_group(current_user):
    # Esta rota permanece inalterada, pois criar um grupo e adicionar o primeiro
    # membro nunca violará o limite do plano.
    data = request.get_json()
    group_name = data.get('name')

    if not group_name:
        return jsonify({'message': 'O nome do grupo é obrigatório!'}), 400
    
    user_id = current_user.id
    unique_code = generate_unique_code()

    try:
        group_res = supabase.table('groups').insert({
            'name': group_name, 'owner_id': user_id, 'invite_code': unique_code
            # A coluna 'plan_id' usará o valor padrão 'free' definido no banco de dados.
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
        # Primeiro, encontramos o grupo para obter seu ID.
        group_res = supabase.table('groups').select('id').eq('invite_code', invite_code).single().execute()
        group_id = group_res.data['id']
        user_id = current_user.id
        
        # --- NOVA LÓGICA DE VERIFICAÇÃO DE PLANO ---
        # Antes de prosseguir, chamamos nossa função auxiliar para verificar o limite de usuários.
        can_add_member, error_message = _check_user_limit(group_id)
        if not can_add_member:
            return jsonify({"message": error_message}), 403 # 403 Forbidden
        # --- FIM DA NOVA LÓGICA ---

        # Se a verificação passar, continuamos com a lógica original.
        membership_check = supabase.table('group_members').select('user_id').eq('group_id', group_id).eq('user_id', user_id).execute()
        if membership_check.data:
            return jsonify({'message': 'Você já é membro deste grupo!'}), 409

        supabase.table('group_members').insert({'group_id': group_id, 'user_id': user_id}).execute()
        
        return jsonify({'message': 'Você entrou no grupo com sucesso!', 'group_id': group_id}), 200
        
    except Exception:
        # Este erro geralmente ocorre se o 'invite_code' for inválido.
        return jsonify({'message': 'Código de convite inválido ou erro ao processar.'}), 404