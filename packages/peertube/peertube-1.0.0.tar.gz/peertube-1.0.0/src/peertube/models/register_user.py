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
    from peertube.models.register_user_channel import RegisterUserChannel


T = TypeVar("T", bound="RegisterUser")


@_attrs_define
class RegisterUser:
    """Attributes:
    username (str): immutable name of the user, used to find or mention its actor Example: chocobozzz.
    password (str):
    email (str): email of the user, used for login or service communications
    display_name (Union[Unset, str]): editable name of the user, displayed in its representations
    channel (Union[Unset, RegisterUserChannel]): channel base information used to create the first channel of the
        user
    """

    username: str
    password: str
    email: str
    display_name: Unset | str = UNSET
    channel: Union[Unset, "RegisterUserChannel"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        username = self.username

        password = self.password

        email = self.email

        display_name = self.display_name

        channel: Unset | dict[str, Any] = UNSET
        if not isinstance(self.channel, Unset):
            channel = self.channel.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "username": username,
                "password": password,
                "email": email,
            }
        )
        if display_name is not UNSET:
            field_dict["displayName"] = display_name
        if channel is not UNSET:
            field_dict["channel"] = channel

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.register_user_channel import RegisterUserChannel

        d = dict(src_dict)
        username = d.pop("username")

        password = d.pop("password")

        email = d.pop("email")

        display_name = d.pop("displayName", UNSET)

        _channel = d.pop("channel", UNSET)
        channel: Unset | RegisterUserChannel
        if isinstance(_channel, Unset):
            channel = UNSET
        else:
            channel = RegisterUserChannel.from_dict(_channel)

        register_user = cls(
            username=username,
            password=password,
            email=email,
            display_name=display_name,
            channel=channel,
        )

        register_user.additional_properties = d
        return register_user

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
