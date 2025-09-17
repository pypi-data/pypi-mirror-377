import json
import os
from dataclasses import dataclass, field, fields, is_dataclass
from typing import Any, Optional, TypeVar


@dataclass
class Configs:
    """
    Add any properties expected to be in the config.json file here.
    If you need to add an object define a new dataclass and add a property with that type.
    """

    ...


T = TypeVar("T")


def _replaceWithDataclass(raw_configs: dict[str, Any], cls: type[T]) -> T:
    for field in fields(cls):
        if is_dataclass(field.type):
            raw_configs[field.name] = _replaceWithDataclass(
                raw_configs[field.name], field.type
            )
    return cls(**raw_configs)


def load_configs() -> Configs:
    abs_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "..", "configs.json"
    )
    raw_json = {}
    with open(abs_path) as configs:
        raw_json = json.load(configs)
    return _replaceWithDataclass(raw_json, Configs)
