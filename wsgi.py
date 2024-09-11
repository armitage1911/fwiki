from wiki import create_app

app = create_app()
# python -c 'import secrets; print(secrets.token_hex())'
app.config['SECRET_KEY'] = ''
