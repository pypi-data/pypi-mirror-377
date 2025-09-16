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
    from peertube.models.get_latest_user_import_response_200_state import (
        GetLatestUserImportResponse200State,
    )


T = TypeVar("T", bound="GetLatestUserImportResponse200")


@_attrs_define
class GetLatestUserImportResponse200:
    """Attributes:
    id (Union[Unset, int]):
    state (Union[Unset, GetLatestUserImportResponse200State]):
    created_at (Union[Unset, datetime.datetime]):
    """

    id: Unset | int = UNSET
    state: Union[Unset, "GetLatestUserImportResponse200State"] = UNSET
    created_at: Unset | datetime.datetime = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        id = self.id

        state: Unset | dict[str, Any] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.to_dict()

        created_at: Unset | str = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if state is not UNSET:
            field_dict["state"] = state
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.get_latest_user_import_response_200_state import (
            GetLatestUserImportResponse200State,
        )

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        _state = d.pop("state", UNSET)
        state: Unset | GetLatestUserImportResponse200State
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = GetLatestUserImportResponse200State.from_dict(_state)

        _created_at = d.pop("createdAt", UNSET)
        created_at: Unset | datetime.datetime
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        get_latest_user_import_response_200 = cls(
            id=id,
            state=state,
            created_at=created_at,
        )

        get_latest_user_import_response_200.additional_properties = d
        return get_latest_user_import_response_200

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
