from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="ServerConfigCustomFollowersInstance")


@_attrs_define
class ServerConfigCustomFollowersInstance:
    """Attributes:
    enabled (Union[Unset, bool]):
    manual_approval (Union[Unset, bool]):
    """

    enabled: Unset | bool = UNSET
    manual_approval: Unset | bool = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        enabled = self.enabled

        manual_approval = self.manual_approval

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if manual_approval is not UNSET:
            field_dict["manualApproval"] = manual_approval

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create from dictionary."""
        d = dict(src_dict)
        enabled = d.pop("enabled", UNSET)

        manual_approval = d.pop("manualApproval", UNSET)

        server_config_custom_followers_instance = cls(
            enabled=enabled,
            manual_approval=manual_approval,
        )

        server_config_custom_followers_instance.additional_properties = d
        return server_config_custom_followers_instance

    @property
    def additional_keys(self) -> list[str]:
        """Get additional keys."""
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
