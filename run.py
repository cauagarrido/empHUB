# run.py
from emphub import create_app

app = create_app()

if __name__ == '__main__':
    # debug=True reinicia o servidor automaticamente a cada mudança
    # Em produção, use um servidor WSGI como Gunicorn ou Waitress.
    app.run(debug=True)