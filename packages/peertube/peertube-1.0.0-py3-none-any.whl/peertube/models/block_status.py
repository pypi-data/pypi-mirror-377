from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.block_status_accounts import BlockStatusAccounts
    from peertube.models.block_status_hosts import BlockStatusHosts


T = TypeVar("T", bound="BlockStatus")


@_attrs_define
class BlockStatus:
    """Attributes:
    accounts (Union[Unset, BlockStatusAccounts]):
    hosts (Union[Unset, BlockStatusHosts]):
    """

    accounts: Union[Unset, "BlockStatusAccounts"] = UNSET
    hosts: Union[Unset, "BlockStatusHosts"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        accounts: Unset | dict[str, Any] = UNSET
        if not isinstance(self.accounts, Unset):
            accounts = self.accounts.to_dict()

        hosts: Unset | dict[str, Any] = UNSET
        if not isinstance(self.hosts, Unset):
            hosts = self.hosts.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if accounts is not UNSET:
            field_dict["accounts"] = accounts
        if hosts is not UNSET:
            field_dict["hosts"] = hosts

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.block_status_accounts import BlockStatusAccounts
        from peertube.models.block_status_hosts import BlockStatusHosts

        d = dict(src_dict)
        _accounts = d.pop("accounts", UNSET)
        accounts: Unset | BlockStatusAccounts
        if isinstance(_accounts, Unset):
            accounts = UNSET
        else:
            accounts = BlockStatusAccounts.from_dict(_accounts)

        _hosts = d.pop("hosts", UNSET)
        hosts: Unset | BlockStatusHosts
        if isinstance(_hosts, Unset):
            hosts = UNSET
        else:
            hosts = BlockStatusHosts.from_dict(_hosts)

        block_status = cls(
            accounts=accounts,
            hosts=hosts,
        )

        block_status.additional_properties = d
        return block_status

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
