from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="ServerConfigInstanceCustomizations")


@_attrs_define
class ServerConfigInstanceCustomizations:
    """Attributes:
    javascript (Union[Unset, str]):
    css (Union[Unset, str]):
    """

    javascript: Unset | str = UNSET
    css: Unset | str = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        javascript = self.javascript

        css = self.css

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if javascript is not UNSET:
            field_dict["javascript"] = javascript
        if css is not UNSET:
            field_dict["css"] = css

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        javascript = d.pop("javascript", UNSET)

        css = d.pop("css", UNSET)

        server_config_instance_customizations = cls(
            javascript=javascript,
            css=css,
        )

        server_config_instance_customizations.additional_properties = d
        return server_config_instance_customizations

    @property
    def additional_keys(self) -> list[str]:
        """Get additional property keys."""
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
