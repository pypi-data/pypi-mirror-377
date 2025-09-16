from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

if TYPE_CHECKING:
    from peertube.models.block_status_accounts_additional_property import (
        BlockStatusAccountsAdditionalProperty,
    )


T = TypeVar("T", bound="BlockStatusAccounts")


@_attrs_define
class BlockStatusAccounts:
    """Block status accounts data model."""

    additional_properties: dict[str, "BlockStatusAccountsAdditionalProperty"] = (
        _attrs_field(init=False, factory=dict)
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.block_status_accounts_additional_property import (
            BlockStatusAccountsAdditionalProperty,
        )

        d = dict(src_dict)
        block_status_accounts = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = BlockStatusAccountsAdditionalProperty.from_dict(
                prop_dict
            )

            additional_properties[prop_name] = additional_property

        block_status_accounts.additional_properties = additional_properties
        return block_status_accounts

    @property
    def additional_keys(self) -> list[str]:
        """Get additional property keys."""
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> "BlockStatusAccountsAdditionalProperty":
        return self.additional_properties[key]

    def __setitem__(
        self, key: str, value: "BlockStatusAccountsAdditionalProperty"
    ) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
