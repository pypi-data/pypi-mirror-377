from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from typing_extensions import Self

T = TypeVar("T", bound="UpdatePluginBodyType0")


@_attrs_define
class UpdatePluginBodyType0:
    """Attributes:
    npm_name (str):  Example: peertube-plugin-auth-ldap.
    """

    npm_name: str

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        npm_name = self.npm_name

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "npmName": npm_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        npm_name = d.pop("npmName")

        update_plugin_body_type_0 = cls(
            npm_name=npm_name,
        )

        return update_plugin_body_type_0
