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

    def __init__(self):
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
    def __init__(self, _: Any):
        self._cls_type_ = self.fqcn()
        json_register_class(self.__class__)

    def to_dict(self) -> dict[str, str]:
        return {"_cls_type_": self._cls_type_, "name": self.name}

    @classmethod
    def fqcn(cls: Type[JSONEnum]) -> str:
        return f"{cls.__module__}#{cls.__qualname__}"

    @classmethod
    def from_dict(cls, obj: dict[str, str]) -> JSONEnum:
        return cls[obj['name']]


class DefaultJSONEncoder(JSONEncoder):
    """Generic JSON Encoder to encode generic types and objects that are instances of JSONSerializable."""

    def default(self, o: Any) -> Any:
        if isinstance(o, JSONSerializable) or isinstance(o, JSONEnum):
            return o.to_dict()
        return super().default(o)


def default_json_dumps(obj: Any) -> (str | bytes):
    return dumps(obj, cls=DefaultJSONEncoder)


class DefaultJSONDecoder(JSONDecoder):
    """Generic JSON Decoder for generic types and classes that implement JSONSerializable."""

    def __init__(self, *args: tuple[Any], **kwargs: dict[str, Any]):
        super().__init__(object_hook=self.as_json_serializable, *args, **kwargs)

    @staticmethod
    def as_json_serializable(o: dict[str, Any]) -> Any:
        if '_cls_type_' in o:
            cls_type = o.get('_cls_type_')
            if isinstance(cls_type, str):
                cls = _type_map[cls_type]
                return cls.from_dict(o)
        return o


def default_json_loads(json_string: str | bytes) -> Any:
    return loads(json_string, cls=DefaultJSONDecoder)
