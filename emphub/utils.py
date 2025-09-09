# emphub/utils.py
import string
import random
from emphub.core.supabase_client import supabase

def generate_unique_code(length=8):
    """Gera um código alfanumérico único e verifica se já não existe na tabela 'groups'."""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        try:
            response = supabase.table('groups').select('id').eq('invite_code', code).execute()
            if not response.data:
                return code
        except Exception as e:
            # Lida com possíveis erros de banco de dados e evita loop infinito
            print(f"Erro ao verificar código único: {e}")
            return None # Retorna None em caso de erro