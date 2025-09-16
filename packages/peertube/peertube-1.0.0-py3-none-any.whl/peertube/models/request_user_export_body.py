from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="RequestUserExportBody")


@_attrs_define
class RequestUserExportBody:
    """Attributes:
    with_video_files (Union[Unset, bool]): Whether to include video files in the archive
    """

    with_video_files: Unset | bool = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        with_video_files = self.with_video_files

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if with_video_files is not UNSET:
            field_dict["withVideoFiles"] = with_video_files

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create from dictionary."""
        d = dict(src_dict)
        with_video_files = d.pop("withVideoFiles", UNSET)

        request_user_export_body = cls(
            with_video_files=with_video_files,
        )

        request_user_export_body.additional_properties = d
        return request_user_export_body

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
