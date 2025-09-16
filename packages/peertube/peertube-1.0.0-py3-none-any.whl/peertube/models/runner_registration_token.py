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

T = TypeVar("T", bound="RunnerRegistrationToken")


@_attrs_define
class RunnerRegistrationToken:
    """Attributes:
    id (Union[Unset, int]):
    registration_token (Union[Unset, str]):
    created_at (Union[Unset, datetime.datetime]):
    updated_at (Union[Unset, datetime.datetime]):
    registered_runners_count (Union[Unset, int]):
    """

    id: Unset | int = UNSET
    registration_token: Unset | str = UNSET
    created_at: Unset | datetime.datetime = UNSET
    updated_at: Unset | datetime.datetime = UNSET
    registered_runners_count: Unset | int = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        id = self.id

        registration_token = self.registration_token

        created_at: Unset | str = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: Unset | str = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        registered_runners_count = self.registered_runners_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if registration_token is not UNSET:
            field_dict["registrationToken"] = registration_token
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if updated_at is not UNSET:
            field_dict["updatedAt"] = updated_at
        if registered_runners_count is not UNSET:
            field_dict["registeredRunnersCount"] = registered_runners_count

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        registration_token = d.pop("registrationToken", UNSET)

        _created_at = d.pop("createdAt", UNSET)
        created_at: Unset | datetime.datetime
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _updated_at = d.pop("updatedAt", UNSET)
        updated_at: Unset | datetime.datetime
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        registered_runners_count = d.pop("registeredRunnersCount", UNSET)

        runner_registration_token = cls(
            id=id,
            registration_token=registration_token,
            created_at=created_at,
            updated_at=updated_at,
            registered_runners_count=registered_runners_count,
        )

        runner_registration_token.additional_properties = d
        return runner_registration_token

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
