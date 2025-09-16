from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.models.user_admin_flags import UserAdminFlags
from peertube.models.user_role import UserRole
from peertube.types import UNSET, Unset

T = TypeVar("T", bound="AddUser")


@_attrs_define
class AddUser:
    """Attributes:
    username (str): immutable name of the user, used to find or mention its actor Example: chocobozzz.
    password (str):
    email (str): The user email
    role (UserRole): The user role (Admin = `0`, Moderator = `1`, User = `2`) Example: 2.
    video_quota (Union[Unset, int]): The user video quota in bytes Example: -1.
    video_quota_daily (Union[Unset, int]): The user daily video quota in bytes Example: -1.
    channel_name (Union[Unset, str]): immutable name of the channel, used to interact with its actor Example:
        framasoft_videos.
    admin_flags (Union[Unset, UserAdminFlags]): Admin flags for the user (None = `0`, Bypass video blocklist = `1`)
        Example: 1.
    """

    username: str
    password: str
    email: str
    role: UserRole
    video_quota: Unset | int = UNSET
    video_quota_daily: Unset | int = UNSET
    channel_name: Unset | str = UNSET
    admin_flags: Unset | UserAdminFlags = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        username = self.username

        password = self.password

        email = self.email

        role = self.role.value

        video_quota = self.video_quota

        video_quota_daily = self.video_quota_daily

        channel_name = self.channel_name

        admin_flags: Unset | int = UNSET
        if not isinstance(self.admin_flags, Unset):
            admin_flags = self.admin_flags.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "username": username,
                "password": password,
                "email": email,
                "role": role,
            }
        )
        if video_quota is not UNSET:
            field_dict["videoQuota"] = video_quota
        if video_quota_daily is not UNSET:
            field_dict["videoQuotaDaily"] = video_quota_daily
        if channel_name is not UNSET:
            field_dict["channelName"] = channel_name
        if admin_flags is not UNSET:
            field_dict["adminFlags"] = admin_flags

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        username = d.pop("username")

        password = d.pop("password")

        email = d.pop("email")

        role = UserRole(d.pop("role"))

        video_quota = d.pop("videoQuota", UNSET)

        video_quota_daily = d.pop("videoQuotaDaily", UNSET)

        channel_name = d.pop("channelName", UNSET)

        _admin_flags = d.pop("adminFlags", UNSET)
        admin_flags: Unset | UserAdminFlags
        if isinstance(_admin_flags, Unset):
            admin_flags = UNSET
        else:
            admin_flags = UserAdminFlags(_admin_flags)

        add_user = cls(
            username=username,
            password=password,
            email=email,
            role=role,
            video_quota=video_quota,
            video_quota_daily=video_quota_daily,
            channel_name=channel_name,
            admin_flags=admin_flags,
        )

        add_user.additional_properties = d
        return add_user

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
