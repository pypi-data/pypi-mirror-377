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
    from peertube.models.list_user_exports_response_200_state import (
        ListUserExportsResponse200State,
    )


T = TypeVar("T", bound="ListUserExportsResponse200")


@_attrs_define
class ListUserExportsResponse200:
    """Attributes:
    id (Union[Unset, int]):
    state (Union[Unset, ListUserExportsResponse200State]):
    size (Union[Unset, int]): Size of the archive file in bytes
    private_download_url (Union[Unset, str]): This URL already contains the JWT token, so no additional
        authentication credentials are required
    created_at (Union[Unset, datetime.datetime]):
    expires_on (Union[Unset, datetime.datetime]):
    """

    id: Unset | int = UNSET
    state: Union[Unset, "ListUserExportsResponse200State"] = UNSET
    size: Unset | int = UNSET
    private_download_url: Unset | str = UNSET
    created_at: Unset | datetime.datetime = UNSET
    expires_on: Unset | datetime.datetime = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        id = self.id

        state: Unset | dict[str, Any] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.to_dict()

        size = self.size

        private_download_url = self.private_download_url

        created_at: Unset | str = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        expires_on: Unset | str = UNSET
        if not isinstance(self.expires_on, Unset):
            expires_on = self.expires_on.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if state is not UNSET:
            field_dict["state"] = state
        if size is not UNSET:
            field_dict["size"] = size
        if private_download_url is not UNSET:
            field_dict["privateDownloadUrl"] = private_download_url
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if expires_on is not UNSET:
            field_dict["expiresOn"] = expires_on

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.list_user_exports_response_200_state import (
            ListUserExportsResponse200State,
        )

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        _state = d.pop("state", UNSET)
        state: Unset | ListUserExportsResponse200State
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = ListUserExportsResponse200State.from_dict(_state)

        size = d.pop("size", UNSET)

        private_download_url = d.pop("privateDownloadUrl", UNSET)

        _created_at = d.pop("createdAt", UNSET)
        created_at: Unset | datetime.datetime
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _expires_on = d.pop("expiresOn", UNSET)
        expires_on: Unset | datetime.datetime
        if isinstance(_expires_on, Unset):
            expires_on = UNSET
        else:
            expires_on = isoparse(_expires_on)

        list_user_exports_response_200 = cls(
            id=id,
            state=state,
            size=size,
            private_download_url=private_download_url,
            created_at=created_at,
            expires_on=expires_on,
        )

        list_user_exports_response_200.additional_properties = d
        return list_user_exports_response_200

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
