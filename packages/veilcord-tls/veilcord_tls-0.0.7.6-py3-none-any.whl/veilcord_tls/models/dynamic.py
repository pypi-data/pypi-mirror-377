from __future__ import annotations
from collections.abc import Iterable
from typing import List, Any, Dict, Union


class DataObject:
    def __init__(self, data: dict) -> None:
        self.__dict__.update(
            {key: self._convert_value(value) for key, value in data.items()}
        )

    def _convert_value(
        self, value: Union[dict, List, Any]
    ) -> Union["DataObject", List, Any]:
        return (
            [
                self._convert_value(item) if isinstance(item, (dict, list)) else item
                for item in value
            ]
            if isinstance(value, list)
            else DataObject(value) if isinstance(value, dict) else value
        )

    def __getattr__(self, name: str) -> Union[Any, "DataObject"]:
        if hasattr(self, name):
            return self.__dict__[name]
        raise AttributeError(f"'DataObject' object has no attribute '{name}'")

    def __dir__(self) -> List[Any]:
        return list(self.__dict__.keys())

    def __repr__(self) -> str:
        attributes = ', '.join(f"{key}: {type(value).__name__}" for key, value in self.__dict__.items())
        return f"DataObject({attributes})"
