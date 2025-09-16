from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="UpdatePluginBodyType1")


@_attrs_define
class UpdatePluginBodyType1:
    """Attributes:
    path (str):
    """

    path: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
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
        """Create from dictionary."""
        d = dict(src_dict)
        path = d.pop("path")

        update_plugin_body_type_1 = cls(
            path=path,
        )

        return update_plugin_body_type_1
