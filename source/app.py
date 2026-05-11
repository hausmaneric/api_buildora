from flask import Flask
from flask_cors import CORS
import json
import os
from source.core.config.config import appConfig
from source.core.system.utils import decrypt_aes_b64

app = Flask(__name__)
cors = CORS(
    app,
    resources={
        r"/api/v1/*": {
            "origins": "*",
            "methods": "GET, POST, PUT, DELETE, OPTIONS",
            "headers": "Origin, Content-Type, Authorization, X-Auth-Token, X-Account-Code, charset=utf-8",
        }
    },
)
app.config['JSON_AS_ASCII'] = False

from source.controller import ctrl_admin, ctrl_auth, ctrl_diary, ctrl_main, ctrl_operational, ctrl_production, ctrl_tenant


def _read_runtime_config() -> dict:
    config = {}
    config_file = os.path.join(PARENT_DIR, '_config.server.json')
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as file:
            config.update(json.load(file))

    env_map = {
        'OBRAX_API_NAME': os.getenv('OBRAX_API_NAME'),
        'OBRAX_API_VERSION': os.getenv('OBRAX_API_VERSION'),
        'OBRAX_DATABASE_URL': os.getenv('OBRAX_DATABASE_URL'),
        'OBRAX_DB_HOST': os.getenv('OBRAX_DB_HOST'),
        'OBRAX_DB_PORT': os.getenv('OBRAX_DB_PORT'),
        'OBRAX_DB_NAME': os.getenv('OBRAX_DB_NAME'),
        'OBRAX_DB_USER': os.getenv('OBRAX_DB_USER'),
        'OBRAX_DB_PASSWORD': os.getenv('OBRAX_DB_PASSWORD'),
        'OBRAX_DB_SSLMODE': os.getenv('OBRAX_DB_SSLMODE'),
        'OBRAX_SECRET_KEY': os.getenv('OBRAX_SECRET_KEY'),
        'OBRAX_SETUP_KEY': os.getenv('OBRAX_SETUP_KEY'),
    }
    for key, value in env_map.items():
        if value not in [None, '']:
            config[key] = value
    return config


def _apply_runtime_config(config: dict) -> None:
    appConfig.apiName = config.get('OBRAX_API_NAME', appConfig.apiName)
    appConfig.apiVersion = config.get('OBRAX_API_VERSION', appConfig.apiVersion)
    appConfig.databaseUrl = config.get('OBRAX_DATABASE_URL', appConfig.databaseUrl)
    appConfig.dbHost = config.get('OBRAX_DB_HOST', appConfig.dbHost)
    appConfig.dbPort = int(config.get('OBRAX_DB_PORT', appConfig.dbPort))
    appConfig.dbName = config.get('OBRAX_DB_NAME', appConfig.dbName)
    appConfig.dbUser = config.get('OBRAX_DB_USER', appConfig.dbUser)
    appConfig.dbPassword = config.get('OBRAX_DB_PASSWORD', appConfig.dbPassword)
    appConfig.dbSslMode = config.get('OBRAX_DB_SSLMODE', appConfig.dbSslMode)
    appConfig.secretKey = config.get('OBRAX_SECRET_KEY', appConfig.secretKey)
    appConfig.setupKey = config.get('OBRAX_SETUP_KEY', appConfig.setupKey)

    if appConfig.dbPassword:
        try:
            appConfig.dbPassword = decrypt_aes_b64(
                appConfig.dbPassword,
                appConfig.apiKey,
                appConfig.apiIV,
            )
        except Exception:
            pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
_apply_runtime_config(_read_runtime_config())


if __name__ == '__main__':
    port = int(os.getenv('PORT', '8080'))
    app.run(host='0.0.0.0', port=port, debug=True)
