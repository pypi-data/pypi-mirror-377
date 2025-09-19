import dataclasses
import typing
from typing import Optional, Union, get_type_hints

noneType = type(None)

def unflatten(value, py_type):
    org = typing.get_origin(py_type)
    if org == Union:
        types = typing.get_args(py_type)
        non_null = [t for t in types if t != noneType]
        py_type = non_null[0]
    elif org == list:
        py_type = typing.get_args(py_type)[0]
        hints = get_type_hints(py_type)
        ary = []
        for item in value:
            obj = {}
            for name in hints:
                obj[name] = unflatten(item[name], hints[name])
            ary.append(py_type(**obj))
        return ary
    
    if dataclasses.is_dataclass(py_type):
        return import_paraflow_object(value, py_type)
    else:
        return value

def import_paraflow_object(flat_obj, cls):
    hints = get_type_hints(cls)
    obj = {}
    for name in hints:
        obj[name] = unflatten(flat_obj[name], hints[name])
    data = cls(**obj)
    return data
