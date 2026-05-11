from flask import request
from app import app
from classes.auth_utils import authenticate_master, authenticate_tenant
from classes.next_base import NXResult
from classes.obrax_utils import NXMasterConnection


@app.route('/api/v1/auth/master/login/', methods=['POST'])
def master_login():
    result = NXResult()
    data = request.get_json(silent=True)
    if not data:
        result.make_error(0, 'Dados inválidos enviados')
        return result.toJSON()

    login = data.get('login', '').strip().lower()
    password = data.get('password', '')
    if not login or not password:
        result.make_error(0, 'Login e senha são obrigatórios')
        return result.toJSON()

    return authenticate_master(login, password).toJSON()


@app.route('/api/v1/auth/tenant/login/', methods=['POST'])
def tenant_login():
    result = NXResult()
    data = request.get_json(silent=True)
    if not data:
        result.make_error(0, 'Dados inválidos enviados')
        return result.toJSON()

    account_code = request.headers.get('X-Account-Code', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not account_code:
        result.make_error(0, 'Cabeçalho X-Account-Code é obrigatório')
        return result.toJSON()

    if not email or not password:
        result.make_error(0, 'E-mail e senha são obrigatórios')
        return result.toJSON()

    return authenticate_tenant(account_code, email, password).toJSON()


@app.route('/api/v1/auth/health/', methods=['GET'])
def health():
    result = NXResult()
    nx = NXMasterConnection()
    opened = nx.active()
    if opened.error:
        return opened.toJSON()

    try:
        rs = nx.xp_nx.FDXQuery('SELECT NOW() AS server_time, current_database() AS database_name')
        if rs.error:
            result.make_error(0, 'Erro ao validar conexão', rs.message)
        else:
            result.status = True
            result.data = rs.dataset.recordset[0] if rs.dataset.recordset else {}
    except Exception as e:
        result.make_error(0, 'Erro interno ao validar saúde da API', str(e))
    finally:
        nx.stop()

    return result.toJSON()
