# config.py
import os
from dotenv import load_dotenv

load_dotenv() # Carrega as variáveis do arquivo .env

class Config:
    """Classe de configuração da aplicação."""
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL e SUPABASE_KEY devem ser definidos no arquivo .env")