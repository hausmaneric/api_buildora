import base64
import json
from datetime import datetime, timedelta
from typing import Any

import jsonpickle
import jwt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from source.core.config.config import appConfig  # noqa: E402


class DatetimeHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data):
        return obj.isoformat()


def objToJSON(o, native=True):
    jsonpickle.handlers.registry.register(datetime, DatetimeHandler)
    return jsonpickle.encode(o, unpicklable=native)


def jsonToObj(s) -> Any:
    return jsonpickle.decode(s)


class NXBase:
    def __init__(self, *args: Any, **kwds: Any) -> Any:
        self._json = kwds.get('json')
        self._json_error = None
        self.jsonImport()

    def jsonImport(self, js=None):
        payload = js if js is not None else self._json
        if payload not in ('', None):
            obj = jsonToObj(payload)
            if isinstance(obj, dict):
                self.__dict__.update(obj)
                self._json_error = False
            elif type(obj) is self.__class__:
                self.__dict__.update(obj.__dict__)
                self._json_error = False
            else:
                self._json_error = True
        self._json = None

    def jsonError(self):
        return self._json_error

    def toJSON(self):
        data = {
            key: value
            for key, value in self.__dict__.items()
            if not key.startswith('_') and value is not None
        }
        return json.dumps(data, default=lambda o: o.__dict__, ensure_ascii=False, indent=4)


class NXResult(NXBase):
    def __init__(self, *args: Any, **kwds: Any) -> Any:
        super().__init__(*args, **kwds)
        self.nx_result = True
        self.status = False
        self.code = -1
        self.info = False
        self.warning = False
        self.error = False
        self.message = ''
        self.error_msg = ''
        self.data = None

    def make_error(self, code, message, error_msg=''):
        self.status = False
        self.code = code
        self.info = False
        self.warning = False
        self.error = True
        self.message = message
        self.error_msg = error_msg

    def make_warning(self, code, message):
        self.status = False
        self.code = code
        self.info = False
        self.warning = True
        self.error = False
        self.message = message
        self.error_msg = ''

    def make_info(self, code, message):
        self.status = False
        self.code = code
        self.info = True
        self.warning = False
        self.error = False
        self.message = message
        self.error_msg = ''


def success_message(entity: str, action: str) -> str:
    action_map = {
        'create': 'cadastrado com sucesso',
        'update': 'atualizado com sucesso',
        'delete': 'excluido com sucesso',
        'list': 'carregado com sucesso',
        'bootstrap': 'executado com sucesso',
        'compatibility': 'carregada com sucesso',
        'status': 'carregado com sucesso',
    }
    suffix = action_map.get(action, 'processado com sucesso')
    return f'{entity} {suffix}'


def process_error_message(entity: str, action: str) -> str:
    action_map = {
        'create': 'Falha no processo de cadastro',
        'update': 'Falha no processo de atualizacao',
        'delete': 'Falha no processo de exclusao',
        'list': 'Falha no processo de consulta',
        'bootstrap': 'Falha no processo de bootstrap',
        'compatibility': 'Falha no processo de compatibilidade',
        'status': 'Falha no processo de consulta',
    }
    prefix = action_map.get(action, 'Falha no processo')
    return f'{prefix} de {entity}'


def generate_aes_key_iv():
    import os
    return os.urandom(32), os.urandom(16)


def encrypt_aes_b64(data: str, key: bytes, iv: bytes) -> str:
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    data_padded = data + (16 - len(data) % 16) * chr(16 - len(data) % 16)
    encrypted = encryptor.update(data_padded.encode('utf-8')) + encryptor.finalize()
    return base64.urlsafe_b64encode(encrypted).decode('utf-8')


def decrypt_aes_b64(encrypted_data: str, key: bytes, iv: bytes) -> str:
    padded = encrypted_data + '=' * (-len(encrypted_data) % 4)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    encrypted_bytes = base64.urlsafe_b64decode(padded.encode('utf-8'))
    decrypted_padded = decryptor.update(encrypted_bytes) + decryptor.finalize()
    padding_length = decrypted_padded[-1]
    return decrypted_padded[:-padding_length].decode('utf-8')


def encode_token(payload: dict[str, Any]) -> str:
    safe_payload = dict(payload)
    safe_payload['exp'] = datetime.utcnow() + timedelta(days=1)
    return jwt.encode(safe_payload, appConfig.secretKey, algorithm='HS256')


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, appConfig.secretKey, algorithms=['HS256'])


__all__ = [
    'NXBase',
    'NXResult',
    'objToJSON',
    'jsonToObj',
    'decode_token',
    'encode_token',
    'decrypt_aes_b64',
    'encrypt_aes_b64',
    'generate_aes_key_iv',
]
