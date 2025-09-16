from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="VideoPassword")


@_attrs_define
class VideoPassword:
    """Attributes:
    id (Union[Unset, int]):  Example: 42.
    password (Union[Unset, str]):
    video_id (Union[Unset, int]):  Example: 42.
    """

    id: Unset | int = UNSET
    password: Unset | str = UNSET
    video_id: Unset | int = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        id = self.id

        password = self.password

        video_id = self.video_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if password is not UNSET:
            field_dict["password"] = password
        if video_id is not UNSET:
            field_dict["videoId"] = video_id

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create from dictionary."""
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        password = d.pop("password", UNSET)

        video_id = d.pop("videoId", UNSET)

        video_password = cls(
            id=id,
            password=password,
            video_id=video_id,
        )

        video_password.additional_properties = d
        return video_password

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
