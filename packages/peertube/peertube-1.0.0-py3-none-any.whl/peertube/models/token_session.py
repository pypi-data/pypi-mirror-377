import datetime
from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="TokenSession")


@_attrs_define
class TokenSession:
    """Attributes:
    id (Union[Unset, int]):
    current_session (Union[Unset, bool]): Is this session the current one?
    login_device (Union[Unset, str]): Device used to login
    login_ip (Union[Unset, str]): IP address used to login
    login_date (Union[Unset, datetime.datetime]): Date of the login
    last_activity_device (Union[Unset, str]):
    last_activity_ip (Union[Unset, str]):
    last_activity_date (Union[Unset, datetime.datetime]):
    created_at (Union[Unset, datetime.datetime]):
    """

    id: Unset | int = UNSET
    current_session: Unset | bool = UNSET
    login_device: Unset | str = UNSET
    login_ip: Unset | str = UNSET
    login_date: Unset | datetime.datetime = UNSET
    last_activity_device: Unset | str = UNSET
    last_activity_ip: Unset | str = UNSET
    last_activity_date: Unset | datetime.datetime = UNSET
    created_at: Unset | datetime.datetime = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        id = self.id

        current_session = self.current_session

        login_device = self.login_device

        login_ip = self.login_ip

        login_date: Unset | str = UNSET
        if not isinstance(self.login_date, Unset):
            login_date = self.login_date.isoformat()

        last_activity_device = self.last_activity_device

        last_activity_ip = self.last_activity_ip

        last_activity_date: Unset | str = UNSET
        if not isinstance(self.last_activity_date, Unset):
            last_activity_date = self.last_activity_date.isoformat()

        created_at: Unset | str = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if current_session is not UNSET:
            field_dict["currentSession"] = current_session
        if login_device is not UNSET:
            field_dict["loginDevice"] = login_device
        if login_ip is not UNSET:
            field_dict["loginIP"] = login_ip
        if login_date is not UNSET:
            field_dict["loginDate"] = login_date
        if last_activity_device is not UNSET:
            field_dict["lastActivityDevice"] = last_activity_device
        if last_activity_ip is not UNSET:
            field_dict["lastActivityIP"] = last_activity_ip
        if last_activity_date is not UNSET:
            field_dict["lastActivityDate"] = last_activity_date
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        current_session = d.pop("currentSession", UNSET)

        login_device = d.pop("loginDevice", UNSET)

        login_ip = d.pop("loginIP", UNSET)

        _login_date = d.pop("loginDate", UNSET)
        login_date: Unset | datetime.datetime
        if isinstance(_login_date, Unset):
            login_date = UNSET
        else:
            login_date = isoparse(_login_date)

        last_activity_device = d.pop("lastActivityDevice", UNSET)

        last_activity_ip = d.pop("lastActivityIP", UNSET)

        _last_activity_date = d.pop("lastActivityDate", UNSET)
        last_activity_date: Unset | datetime.datetime
        if isinstance(_last_activity_date, Unset):
            last_activity_date = UNSET
        else:
            last_activity_date = isoparse(_last_activity_date)

        _created_at = d.pop("createdAt", UNSET)
        created_at: Unset | datetime.datetime
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        token_session = cls(
            id=id,
            current_session=current_session,
            login_device=login_device,
            login_ip=login_ip,
            login_date=login_date,
            last_activity_device=last_activity_device,
            last_activity_ip=last_activity_ip,
            last_activity_date=last_activity_date,
            created_at=created_at,
        )

        token_session.additional_properties = d
        return token_session

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
