from flask import request
from source.app import app
from source.logic.orb_diary import *
from source.core.system.core import *


def _diary_permission_result(nx, token_id, method, diary_id=None):
    r = nx.login(NXLoginType.SYSTEM, token_id)
    if r.status is not True:
        return r

    permission_codes = {
        'GET': ('diary.read',),
        'POST': ('diary.write',),
        'PUT': ('diary.write',),
    }
    if diary_id is not None and method == 'POST':
        permission_codes = ('diary.approve',)
    else:
        permission_codes = permission_codes.get(method, ())

    return require_tenant_permissions(nx, *permission_codes)


def _run_diary_action(token_id, action, error_message):
    r = NXResult()
    try:
        nx = NXConnection()
        r = _diary_permission_result(nx, token_id, request.method)
        if r.status is True:
            r = action(nx)
    except Exception as e:
        r.make_error(0, error_message, str(e))

    return r.toJSON()


@app.route('/api/v1/diary/<token_id>', methods=['GET', 'POST', 'PUT'])
def diary_index(token_id):
    r = NXResult()
    data = request.get_json(silent=True)

    try:
        nx = NXConnection()
        r = _diary_permission_result(nx, token_id, request.method)

        if r.status is True:
            if request.method == 'GET':
                r = diary_list(nx, request.args.to_dict())
            elif request.method == 'POST':
                if data:
                    r = diary_create(nx, data)
                else:
                    r.make_error(0, 'Dados invalidos enviados')
            elif request.method == 'PUT':
                if data:
                    r = diary_update(nx, data)
                else:
                    r.make_error(0, 'Dados invalidos enviados')
    except Exception as e:
        r.make_error(0, 'Erro ao processar diario', str(e))

    return r.toJSON()


@app.route('/api/v1/diary/detail/<int:diary_id>/<token_id>', methods=['GET'])
@app.route('/api/v1/diary/<int:diary_id>/<token_id>', methods=['GET'])
def diary_detail_index(diary_id, token_id):
    return _run_diary_action(
        token_id,
        lambda nx: diary_detail(nx, diary_id),
        'Erro ao consultar diario completo',
    )


@app.route('/api/v1/diary/export/<int:diary_id>/<token_id>', methods=['GET'])
@app.route('/api/v1/diary/<int:diary_id>/export/<token_id>', methods=['GET'])
def diary_export_index(diary_id, token_id):
    return _run_diary_action(
        token_id,
        lambda nx: diary_export(nx, diary_id),
        'Erro ao exportar diario',
    )


@app.route('/api/v1/diary/monthly-export/<token_id>', methods=['GET'])
def diary_monthly_export_index(token_id):
    return _run_diary_action(
        token_id,
        lambda nx: diary_monthly_export(nx, request.args.to_dict()),
        'Erro ao exportar relatorio mensal do diario',
    )


@app.route('/api/v1/diary/approve/<int:diary_id>/<token_id>', methods=['POST'])
@app.route('/api/v1/diary/<int:diary_id>/approve/<token_id>', methods=['POST'])
def diary_approve_index(diary_id, token_id):
    r = NXResult()
    try:
        nx = NXConnection()
        r = _diary_permission_result(nx, token_id, request.method, diary_id=diary_id)
        if r.status is True:
            r = diary_approve(nx, diary_id)
    except Exception as e:
        r.make_error(0, 'Erro ao aprovar diario', str(e))
    return r.toJSON()


@app.route('/api/v1/diary/reject/<int:diary_id>/<token_id>', methods=['POST'])
@app.route('/api/v1/diary/<int:diary_id>/reject/<token_id>', methods=['POST'])
def diary_reject_index(diary_id, token_id):
    r = NXResult()
    try:
        nx = NXConnection()
        r = _diary_permission_result(nx, token_id, request.method, diary_id=diary_id)
        if r.status is True:
            r = diary_reject(nx, diary_id)
    except Exception as e:
        r.make_error(0, 'Erro ao reprovar diario', str(e))
    return r.toJSON()
