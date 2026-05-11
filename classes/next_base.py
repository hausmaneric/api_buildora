import json
import jsonpickle
from typing import Any
from datetime import datetime
from classes.express import FDORMClass


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


class NXDataClass(NXBase, FDORMClass):
    def __init__(self) -> Any:
        super().__init__()


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
