# coding=utf-8
from typing import Any

import orjson
import ujson
import json

TyDic = dict[Any, Any]
TyAoD = list[TyDic]


class Json:

    type2loads = {
        'orjson': orjson.loads,
        'ujson': ujson.loads,
        'json': json.loads}

    type2dumps = {
        'orjson': orjson.dumps,
        'ujson': ujson.dumps,
        'json': json.dumps}

    type2dump = {
        'orjson': json.dump,
        'ujson': json.dump,
        'json': json.dump}

    @classmethod
    def loads(cls, obj, **kwargs):
        json_type = kwargs.get('json_type', 'orjson')
        loads = cls.type2loads.get(json_type)
        return loads(obj)

    @classmethod
    def dumps(cls, obj, **kwargs):
        json_type = kwargs.get('json_type', 'orjson')
        indent = kwargs.get('indent')
        dumps = cls.type2dumps.get(json_type)
        dumps(obj, indent=indent)
        return obj

    @classmethod
    def dump(cls, obj, fd, **kwargs):
        json_type = kwargs.get('json_type', 'orjson')
        dump = cls.type2dump.get(json_type)
        indent = kwargs.get('indent', 2)
        sort_keys = kwargs.get('sort_keys', False)
        ensure_ascii = kwargs.get('ensure_ascii', False)
        # separator = kwargs.get('separator', None),
        dump(
            obj, fd,
            indent=indent,
            sort_keys=sort_keys,
            ensure_ascii=ensure_ascii)

    @classmethod
    def write(cls, obj, path, **kwargs):
        if obj is None:
            return
        json_type = kwargs.get('json', 'orjson')
        dump = cls.type2dump.get(json_type)
        with open(path, 'w') as fd:
            dump(obj, fd, **kwargs)

    @classmethod
    def read(cls, path_file, **kwargs):
        mode = kwargs.get('mode', 'rb')
        with open(path_file, mode) as fd:
            return cls.loads(fd.read(), **kwargs)
        return None
