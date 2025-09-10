# ---- Estágio 1: Builder ----
# Usamos uma imagem Python leve como base para construir nosso ambiente.
FROM python:3.11-slim as builder

# Define o diretório de trabalho dentro do contêiner.
WORKDIR /app

# Cria um ambiente virtual para isolar as dependências (boa prática).
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copia apenas o arquivo de dependências primeiro.
# O Docker armazena isso em cache, então as dependências só serão reinstaladas se o requirements.txt mudar.
COPY requirements.txt .

# Instala as dependências dentro do ambiente virtual.
RUN pip install --no-cache-dir -r requirements.txt


# ---- Estágio 2: Final ----
# Começamos de novo com a mesma imagem base limpa para manter a imagem final pequena.
FROM python:3.11-slim

WORKDIR /app

# Copia o ambiente virtual com as dependências já instaladas do estágio "builder".
COPY --from=builder /opt/venv /opt/venv

# Define o PATH para usar o Python e os pacotes do ambiente virtual.
ENV PATH="/opt/venv/bin:$PATH"

# Copia o resto do código da sua aplicação para o contêiner.
COPY . .

# Expõe a porta que o Gunicorn irá usar. O Render sugere a porta 10000.
EXPOSE 10000

# O comando que será executado quando o contêiner iniciar.
# Ele inicia o Gunicorn, aponta para o seu arquivo `app.py` e a instância `app` do Flask.
# --bind 0.0.0.0:10000 : Permite que o servidor aceite conexões de fora do contêiner.
# app:app : Refere-se ao arquivo `app.py` e à variável `app = Flask(__name__)` dentro dele.
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]