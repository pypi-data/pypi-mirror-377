from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="BlockStatusAccountsAdditionalProperty")


@_attrs_define
class BlockStatusAccountsAdditionalProperty:
    """Attributes:
    blocked_by_server (Union[Unset, bool]):
    blocked_by_user (Union[Unset, bool]):
    """

    blocked_by_server: Unset | bool = UNSET
    blocked_by_user: Unset | bool = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        blocked_by_server = self.blocked_by_server

        blocked_by_user = self.blocked_by_user

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if blocked_by_server is not UNSET:
            field_dict["blockedByServer"] = blocked_by_server
        if blocked_by_user is not UNSET:
            field_dict["blockedByUser"] = blocked_by_user

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        blocked_by_server = d.pop("blockedByServer", UNSET)

        blocked_by_user = d.pop("blockedByUser", UNSET)

        block_status_accounts_additional_property = cls(
            blocked_by_server=blocked_by_server,
            blocked_by_user=blocked_by_user,
        )

        block_status_accounts_additional_property.additional_properties = d
        return block_status_accounts_additional_property

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
