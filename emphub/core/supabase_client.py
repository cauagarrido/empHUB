
from supabase import create_client, Client
from config import Config


supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
print("Instância do cliente Supabase criada com sucesso!")