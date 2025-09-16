from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="AddPluginBodyType1")


@_attrs_define
class AddPluginBodyType1:
    """Attributes:
    path (str):
    """

    path: str

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        path = self.path

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "path": path,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        path = d.pop("path")

        add_plugin_body_type_1 = cls(
            path=path,
        )

        return add_plugin_body_type_1
