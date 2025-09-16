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

T = TypeVar("T", bound="Runner")


@_attrs_define
class Runner:
    """Attributes:
    id (Union[Unset, int]):
    name (Union[Unset, str]):
    description (Union[Unset, str]):
    ip (Union[Unset, str]):
    updated_at (Union[Unset, datetime.datetime]):
    created_at (Union[Unset, datetime.datetime]):
    last_contact (Union[Unset, datetime.datetime]):
    """

    id: Unset | int = UNSET
    name: Unset | str = UNSET
    description: Unset | str = UNSET
    ip: Unset | str = UNSET
    updated_at: Unset | datetime.datetime = UNSET
    created_at: Unset | datetime.datetime = UNSET
    last_contact: Unset | datetime.datetime = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        id = self.id

        name = self.name

        description = self.description

        ip = self.ip

        updated_at: Unset | str = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        created_at: Unset | str = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        last_contact: Unset | str = UNSET
        if not isinstance(self.last_contact, Unset):
            last_contact = self.last_contact.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if ip is not UNSET:
            field_dict["ip"] = ip
        if updated_at is not UNSET:
            field_dict["updatedAt"] = updated_at
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if last_contact is not UNSET:
            field_dict["lastContact"] = last_contact

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create from dictionary."""
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        ip = d.pop("ip", UNSET)

        _updated_at = d.pop("updatedAt", UNSET)
        updated_at: Unset | datetime.datetime
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        _created_at = d.pop("createdAt", UNSET)
        created_at: Unset | datetime.datetime
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _last_contact = d.pop("lastContact", UNSET)
        last_contact: Unset | datetime.datetime
        if isinstance(_last_contact, Unset):
            last_contact = UNSET
        else:
            last_contact = isoparse(_last_contact)

        runner = cls(
            id=id,
            name=name,
            description=description,
            ip=ip,
            updated_at=updated_at,
            created_at=created_at,
            last_contact=last_contact,
        )

        runner.additional_properties = d
        return runner

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
