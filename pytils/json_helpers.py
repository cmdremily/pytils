from __future__ import annotations

from enum import Enum
from json import JSONDecoder, dumps, loads, JSONEncoder
from typing import Any, Type

_type_map: dict[str, Type[JSONSerializable | JSONEnum]] = {}


def json_register_class(cls: Type[JSONSerializable | JSONEnum]) -> None:
    fqcn = cls.fqcn()
    if fqcn not in _type_map:
        _type_map[fqcn] = cls


class JSONSerializable:
    """Base class for JSON Serializable classes.

    Simple classes just need to inherit from JSONSerializable and call the super class's constructor.
    More advanced serialization cases can be accommodated by overriding to_dict() and from_dict().
    """

    def __init__(self, **kwargs):
        self._cls_type_ = self.fqcn()
        json_register_class(self.__class__)

    def to_dict(self) -> dict[str, Any]:
        """Converts this class into a dictionary representation that can be serialized to JSON.

        Override this and from_dict() to match is order to customize serialization.

        MUST preserve the `_cls_type_` member variable in the returned dictionary, otherwise
        the deserialization code cannot identify the correct class type.

        :return:
            A dictionary with all the fields that are required to uniquely reconstruct this object.
        """
        return self.__dict__

    @classmethod
    def fqcn(cls: Type[JSONSerializable]) -> str:
        return f"{cls.__module__}#{cls.__qualname__}"

    @classmethod
    def from_dict(cls: Type[JSONSerializable], obj: dict[str, Any]) -> JSONSerializable:
        """Creates a new class object from a dictionary previously created by to_dict().

        :param obj: The dictionary containing all the fields required to reconstruct the object.
        :return: An instance of `cls`.
        """
        from inspect import signature

        sig = signature(cls)
        filtered_args = {k: v for k, v in obj.items() if k in sig.parameters}
        return cls(**filtered_args)


class JSONEnum(Enum):
    def __init__(self, value: Any):
        super().__init__(value)
        fqcn = f"{self.__module__}#{self.__class__.__qualname__}"
        self._cls_type_ = fqcn
        if fqcn not in _type_map:
            _type_map[fqcn] = self.__class__

    def to_dict(self) -> dict[str, str]:
        return {"_cls_type_": self._cls_type_, "name": self.name}

    @classmethod
    def from_dict(cls, obj: dict[str, str]) -> JSONEnum:
        return cls[obj['name']]


class DefaultJSONEncoder(JSONEncoder):
    """Generic JSON Encoder to encode generic types and objects that are instances of JSONSerializable."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, JSONSerializable) or isinstance(obj, JSONEnum):
            return obj.to_dict()
        return super().default(obj)


def default_json_dumps(obj: Any) -> str:
    return dumps(obj, cls=DefaultJSONEncoder)


class DefaultJSONDecoder(JSONDecoder):
    """Generic JSON Decoder for generic types and classes that implement JSONSerializable."""

    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    @staticmethod
    def object_hook(obj: dict[str, Any]) -> Any:
        if '_cls_type_' in obj:
            cls_type = obj.get('_cls_type_')
            cls = _type_map[cls_type]
            return cls.from_dict(obj)
        return obj


def default_json_loads(json_string: str) -> Any:
    return loads(json_string, cls=DefaultJSONDecoder)
