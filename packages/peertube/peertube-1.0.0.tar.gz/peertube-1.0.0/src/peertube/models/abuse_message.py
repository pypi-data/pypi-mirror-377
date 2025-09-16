import datetime
from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse
from typing_extensions import Self

from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.account_summary import AccountSummary


T = TypeVar("T", bound="AbuseMessage")


@_attrs_define
class AbuseMessage:
    """Attributes:
    id (Union[Unset, int]):  Example: 42.
    message (Union[Unset, str]):
    by_moderator (Union[Unset, bool]):
    created_at (Union[Unset, datetime.datetime]):
    account (Union[Unset, AccountSummary]):
    """

    id: Unset | int = UNSET
    message: Unset | str = UNSET
    by_moderator: Unset | bool = UNSET
    created_at: Unset | datetime.datetime = UNSET
    account: Union[Unset, "AccountSummary"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        id = self.id

        message = self.message

        by_moderator = self.by_moderator

        created_at: Unset | str = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        account: Unset | dict[str, Any] = UNSET
        if not isinstance(self.account, Unset):
            account = self.account.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if message is not UNSET:
            field_dict["message"] = message
        if by_moderator is not UNSET:
            field_dict["byModerator"] = by_moderator
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if account is not UNSET:
            field_dict["account"] = account

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.account_summary import AccountSummary

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        message = d.pop("message", UNSET)

        by_moderator = d.pop("byModerator", UNSET)

        _created_at = d.pop("createdAt", UNSET)
        created_at: Unset | datetime.datetime
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _account = d.pop("account", UNSET)
        account: Unset | AccountSummary
        if isinstance(_account, Unset):
            account = UNSET
        else:
            account = AccountSummary.from_dict(_account)

        abuse_message = cls(
            id=id,
            message=message,
            by_moderator=by_moderator,
            created_at=created_at,
            account=account,
        )

        abuse_message.additional_properties = d
        return abuse_message

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
