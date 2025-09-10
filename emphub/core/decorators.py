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


# --- NOVO DECORADOR PARA VERIFICAÇÃO DE PLANOS ---

def check_plan_limits(limit_type):
    """
    Decorador que funciona como uma fábrica: ele recebe o tipo de limite a ser verificado
    ('users' ou 'projects') e retorna o decorador configurado para essa verificação.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # O ID do grupo precisa ser passado como um argumento na URL da rota.
            # Por exemplo: @app.route('/groups/<int:group_id>/projects')
            # O Flask passa 'group_id' para a função através de **kwargs.
            group_id = kwargs.get('group_id')
            if not group_id:
                # Este é um erro de configuração do desenvolvedor, então retornamos 500.
                return jsonify({"message": "ID do grupo não foi fornecido na definição da rota para verificação de plano."}), 500

            try:
                # 1. Obter o plano atual do grupo e suas limitações de uma só vez.
                # A sintaxe 'plan:plan_id(*)' faz um JOIN com a tabela 'plans' usando a chave estrangeira 'plan_id'.
                group_plan_res = supabase.table('groups').select('*, plan:plan_id(max_users, max_projects)').eq('id', group_id).single().execute()
                
                if not group_plan_res.data:
                    return jsonify({"message": "Grupo não encontrado."}), 404

                plan_limits = group_plan_res.data.get('plan')
                if not plan_limits:
                     return jsonify({"message": "Plano de assinatura não encontrado para este grupo."}), 500

                # 2. Verificar o limite específico que foi passado como argumento ('users' ou 'projects').
                current_count = 0
                limit = None
                
                if limit_type == 'users':
                    # Pega o limite de usuários definido na tabela 'plans'
                    limit = plan_limits.get('max_users')
                    if limit is not None: # Se o limite for NULL, significa que é ilimitado.
                        # Conta quantos membros o grupo já possui na tabela 'group_members'.
                        count_res = supabase.table('group_members').select('user_id', count='exact').eq('group_id', group_id).execute()
                        current_count = count_res.count
                
                elif limit_type == 'projects':
                    # Pega o limite de projetos definido na tabela 'plans'
                    limit = plan_limits.get('max_projects')
                    if limit is not None:
                        # Conta quantos projetos o grupo já possui.
                        count_res = supabase.table('projects').select('id', count='exact').eq('group_id', group_id).execute()
                        current_count = count_res.count

                # 3. Comparar o uso atual com o limite do plano.
                if limit is not None and current_count >= limit:
                    # Se o limite foi atingido, retorna um erro 403 Forbidden (Acesso Proibido).
                    return jsonify({"message": f"Limite de {limit} {limit_type} atingido. Faça upgrade do seu plano para adicionar mais."}), 403

                # 4. Se o limite não foi atingido, permite que a função original da rota seja executada.
                return f(*args, **kwargs)
            
            except Exception as e:
                return jsonify({"message": f"Erro interno ao verificar os limites do plano: {str(e)}"}), 500

        return decorated_function
    return decorator