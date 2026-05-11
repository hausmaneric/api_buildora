from flask import request
from source.app import app
from source.core.system.utils import NXResult
from source.logic import orb_auth


@app.route('/api/v1/auth/master/login/', methods=['POST'])
def master_login():
    result = NXResult()
    data = request.get_json(silent=True)
    if not data:
        result.make_error(0, 'Dados invalidos enviados')
        return result.toJSON()

    login = data.get('login', '').strip().lower()
    password = data.get('password', '')
    if not login or not password:
        result.make_error(0, 'Login e senha sao obrigatorios')
        return result.toJSON()

    return orb_auth.master_login(login, password)


@app.route('/api/v1/auth/tenant/login/', methods=['POST'])
def tenant_login():
    result = NXResult()
    data = request.get_json(silent=True)
    if not data:
        result.make_error(0, 'Dados invalidos enviados')
        return result.toJSON()

    account_code = request.headers.get('X-Account-Code', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not account_code:
        result.make_error(0, 'Cabecalho X-Account-Code e obrigatorio')
        return result.toJSON()
    if not email or not password:
        result.make_error(0, 'E-mail e senha sao obrigatorios')
        return result.toJSON()

    return orb_auth.tenant_login(account_code, email, password)
