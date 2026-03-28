from pydantic import BaseModel
from typing import Literal, TypeVar
from collections.abc import Iterable, Generator
from pytils.typing import FilePath

V = TypeVar("V", bound=BaseModel)


def ndjson_read[V: BaseModel](
    model_class: type[V], file: FilePath, encoding: str = "utf-8"
) -> Generator[V]:
    with open(file, encoding=encoding) as f:
        for line in f.readlines():
            yield model_class.model_validate_json(line)


def json_read[V: BaseModel](
    model_class: type[V], file: FilePath, encoding: str = "utf-8"
) -> V:
    with open(file, encoding=encoding) as f:
        return model_class.model_validate_json(f.read())


def ndjson_write(
    models: Iterable[BaseModel],
    file: FilePath,
    mode: Literal["a"] | Literal["w"],
    encoding: str = "utf-8",
) -> None:
    with open(file, mode=mode, encoding=encoding) as f:
        _ = f.write("\n".join([model.model_dump_json(indent=None) for model in models]))
        _ = f.write("\n")


def json_write(
    model: BaseModel,
    file: FilePath,
    mode: Literal["a"] | Literal["w"] = "w",
    encoding: str = "utf-8",
) -> None:
    with open(file, mode=mode, encoding=encoding) as f:
        _ = f.write(model.model_dump_json())
