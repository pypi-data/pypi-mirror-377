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
    from peertube.models.add_user_response_user_account import (
        AddUserResponseUserAccount,
    )


T = TypeVar("T", bound="AddUserResponseUser")


@_attrs_define
class AddUserResponseUser:
    """Attributes:
    id (Union[Unset, int]):  Example: 42.
    account (Union[Unset, AddUserResponseUserAccount]):
    """

    id: Unset | int = UNSET
    account: Union[Unset, "AddUserResponseUserAccount"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        id = self.id

        account: Unset | dict[str, Any] = UNSET
        if not isinstance(self.account, Unset):
            account = self.account.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if account is not UNSET:
            field_dict["account"] = account

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.add_user_response_user_account import (
            AddUserResponseUserAccount,
        )

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        _account = d.pop("account", UNSET)
        account: Unset | AddUserResponseUserAccount
        if isinstance(_account, Unset):
            account = UNSET
        else:
            account = AddUserResponseUserAccount.from_dict(_account)

        add_user_response_user = cls(
            id=id,
            account=account,
        )

        add_user_response_user.additional_properties = d
        return add_user_response_user

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
