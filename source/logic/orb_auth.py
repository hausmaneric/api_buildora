from source.core.system.core import NXConnection


def master_login(login: str, password: str):
    nx = NXConnection()
    return nx.authenticate_master(login, password).toJSON()


def tenant_login(account_code: str, email: str, password: str):
    nx = NXConnection()
    return nx.authenticate_tenant(account_code, email, password).toJSON()
