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
    from peertube.models.add_user_response_user import AddUserResponseUser


T = TypeVar("T", bound="AddUserResponse")


@_attrs_define
class AddUserResponse:
    """Attributes:
    user (Union[Unset, AddUserResponseUser]):
    """

    user: Union[Unset, "AddUserResponseUser"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        user: Unset | dict[str, Any] = UNSET
        if not isinstance(self.user, Unset):
            user = self.user.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if user is not UNSET:
            field_dict["user"] = user

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.add_user_response_user import AddUserResponseUser

        d = dict(src_dict)
        _user = d.pop("user", UNSET)
        user: Unset | AddUserResponseUser
        if isinstance(_user, Unset):
            user = UNSET
        else:
            user = AddUserResponseUser.from_dict(_user)

        add_user_response = cls(
            user=user,
        )

        add_user_response.additional_properties = d
        return add_user_response

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
