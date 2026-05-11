from datetime import datetime
from typing import Any
import base64
import json

import psycopg2
from psycopg2.extras import RealDictCursor


class FDDataSchema:
    def __init__(self, name: str, dataset) -> None:
        self.name = name
        self.dataset = dataset

    def to_dict(self):
        return {'name': self.name, 'data': self.dataset}


class FDMetaData:
    def __init__(self, col_name: str, col_type: int | None = None, col_size: int | None = None) -> None:
        self.column_name = col_name
        self.column_type = col_type
        self.column_size = col_size

    def to_dict(self):
        return {
            'column_name': self.column_name,
            'column_type': self.column_type,
            'column_size': self.column_size,
        }


class FDFieldMap:
    def __init__(self, var: str, field: str, required: bool, text: str = '') -> None:
        self.var = var
        self.field = field
        self.required = required
        self.label = text


class FDFieldInfo:
    def __init__(self, name: str, value: Any) -> None:
        self.name = name
        self.value = value


class FDDateTime:
    def __init__(self) -> None:
        self.dt = None
        self.date = None
        self.time = None


class FDORMClass:
    classfieldmap = []

    def mapping(self, args: list[FDFieldMap]):
        for item in args:
            self.classfieldmap.append(item)

    def nullable(self, onlyrequired: bool = True) -> bool:
        for field in self.classfieldmap:
            value = getattr(self, field.var, None)
            if onlyrequired and field.required and value is None:
                return True
            if not onlyrequired and value is None:
                return True
        return False

    def makefieldinfo(self, notnull: bool = True) -> list[FDFieldInfo]:
        result = []
        for field in self.classfieldmap:
            value = getattr(self, field.var, None)
            if (notnull and value is not None) or not notnull:
                result.append(FDFieldInfo(field.field, value))
        return result


class FDDataSet:
    def __init__(self, rows: list[dict[str, Any]], columns: list[str] | None = None) -> None:
        self.recordset = rows
        self.recordcount = len(rows)
        self.recno = 0 if rows else -1
        self.fieldnames = columns or (list(rows[0].keys()) if rows else [])
        self.fieldcount = len(self.fieldnames)
        self.eof = self.recordcount == 0

    def goto(self, index: int):
        if 0 <= index < self.recordcount:
            self.recno = index
            self.eof = False

    def first(self):
        if self.recordcount > 0:
            self.recno = 0
            self.eof = False

    def next(self):
        if self.recordcount > 0 and self.recno < self.recordcount - 1:
            self.recno += 1
        else:
            self.eof = True

    def fieldbyname(self, name: str, default_value=None):
        if self.recordcount == 0:
            return default_value
        value = self.recordset[self.recno].get(name)
        if value is None:
            value = self.recordset[self.recno].get(name.lower(), default_value)
        return value if value is not None else default_value

    def toStruct(self, all: bool = False):
        rows = self.recordset if all else (self.recordset[:1] if self.recordset else [])
        return {
            'header': [FDMetaData(column).to_dict() for column in self.fieldnames],
            'data': rows,
        }

    def toJson(self, all: bool = False, header: bool = False):
        struct = self.toStruct(all)
        if header:
            return json.dumps(struct, default=str)
        return json.dumps(struct['data'], default=str)


class FDResulSet:
    def __init__(self):
        self.dataset = FDDataSet([])
        self.error = False
        self.message = ''


class FDDataCollection:
    def __init__(self) -> None:
        self.schemas = []
        self.headers = {}

    def DataSet(self, name: str, source: FDDataSet):
        self.schemas.append(FDDataSchema(name, source.toStruct(True)).to_dict())

    def Header(self, name: str, value: Any):
        if isinstance(value, bytes):
            value = base64.b64encode(value).decode('utf-8')
        self.headers[name] = value

    def Collection(self, asJson: bool = False):
        payload = {'schemas': self.schemas, 'headers': self.headers}
        return json.dumps(payload, default=str) if asJson else payload


class FDExpress:
    def __init__(self, connection: psycopg2.extensions.connection) -> None:
        self.conn = connection
        self.batch_mode = False

    def _make_cursor(self):
        return self.conn.cursor(cursor_factory=RealDictCursor)

    def _is_write_sql(self, sql: str) -> bool:
        normalized = (sql or '').lstrip().upper()
        return normalized.startswith(('INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP', 'TRUNCATE'))

    def FDXQuery(self, sql: str, *params: Any) -> FDResulSet:
        result = FDResulSet()
        cur = self._make_cursor()
        try:
            cur.execute(sql, params)
            rows = cur.fetchall() if cur.description else []
            columns = [desc.name for desc in cur.description] if cur.description else []
            result.dataset = FDDataSet([dict(row) for row in rows], columns)
            if self._is_write_sql(sql) and not self.batch_mode:
                self.conn.commit()
        except Exception as e:
            result.error = True
            result.message = str(e)
            if not self.batch_mode:
                self.conn.rollback()
        finally:
            cur.close()
        return result

    def FDXSQL(self, sql: str, *params: Any) -> FDResulSet:
        result = FDResulSet()
        cur = self._make_cursor()
        try:
            cur.execute(sql, params)
            if not self.batch_mode:
                self.conn.commit()
        except Exception as e:
            result.error = True
            result.message = str(e)
            if not self.batch_mode:
                self.conn.rollback()
        finally:
            cur.close()
        return result

    def FDXInsert(self, table: str, args: list[FDFieldInfo]) -> FDResulSet:
        columns = ', '.join(item.name for item in args)
        placeholders = ', '.join(['%s'] * len(args))
        values = [item.value for item in args]
        sql = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
        return self.FDXSQL(sql, *values)

    def FDXUpdate(self, table: str, args: list[FDFieldInfo], keys: list[FDFieldInfo]):
        set_clause = ', '.join(f'{item.name} = %s' for item in args)
        where_clause = ' AND '.join(f'{item.name} = %s' for item in keys)
        values = [item.value for item in args] + [item.value for item in keys]
        sql = f'UPDATE {table} SET {set_clause} WHERE {where_clause}'
        return self.FDXSQL(sql, *values)

    def FDXDelete(self, table: str, keys: list[FDFieldInfo]):
        where_clause = ' AND '.join(f'{item.name} = %s' for item in keys)
        values = [item.value for item in keys]
        sql = f'DELETE FROM {table} WHERE {where_clause}'
        return self.FDXSQL(sql, *values)

    def AutoInc(self, table: str, field: str, filter: str = '') -> int:
        sql = f'SELECT COALESCE(MAX({field}), 0) AS pk FROM {table}'
        if filter:
            sql += f' WHERE {filter}'
        rs = self.FDXQuery(sql)
        if rs.error:
            raise ValueError(rs.message)
        value = rs.dataset.fieldbyname('pk', 0) or 0
        return int(value) + 1

    def ServerNow(self) -> FDDateTime:
        result = FDDateTime()
        rs = self.FDXQuery('SELECT NOW() AS now')
        if not rs.error and rs.dataset.recordcount > 0:
            result.dt = rs.dataset.fieldbyname('now')
            if isinstance(result.dt, datetime):
                result.date = result.dt.date()
                result.time = result.dt.time()
        return result
