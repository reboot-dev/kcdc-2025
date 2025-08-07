from google.protobuf.json_format import MessageToDict, ParseDict
from google.protobuf.struct_pb2 import Value
from typing import TypeVar

T = TypeVar('T')


def _from(t: T, expected_type: type[T]) -> Value:
    if type(t) != expected_type:
        raise TypeError(
            f"Expecting argument of type '{expected_type.__name__}'"
        )
    return ParseDict(t, Value())


def from_string(s: str) -> Value:
    return _from(s, str)


def from_bool(b: bool) -> Value:
    return _from(b, bool)


def from_float(f: float) -> Value:
    return _from(f, float)


def from_int(i: int) -> Value:
    return _from(i, int)


def from_dict(d: dict) -> Value:
    return _from(s, dict)


def from_list(l: list) -> Value:
    return _from(l, list)


def _as(value: Value, expected_type: type[T]) -> T:
    t = MessageToDict(value)
    if type(t) != expected_type:
        raise TypeError(f"Expecting value of type '{expected_type.__name__}'")
    return t


def as_string(value: Value) -> str:
    return _as(value, str)


def as_bool(value: Value) -> bool:
    return _as(value, bool)


def as_float(value: Value) -> float:
    return _as(value, float)


def as_int(value: Value) -> int:
    f = as_float(value)
    if not f.is_integer():
        raise TypeError("Expecting an 'int' but got a 'float'")
    return f


def as_dict(value: Value) -> dict:
    return _as(value, dict)


def as_list(value: Value) -> list:
    return _as(value, list)
