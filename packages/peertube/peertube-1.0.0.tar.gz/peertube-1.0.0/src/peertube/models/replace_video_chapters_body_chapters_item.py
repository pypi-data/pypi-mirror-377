from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="ReplaceVideoChaptersBodyChaptersItem")


@_attrs_define
class ReplaceVideoChaptersBodyChaptersItem:
    """Attributes:
    title (Union[Unset, str]):
    timecode (Union[Unset, int]):
    """

    title: Unset | str = UNSET
    timecode: Unset | int = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        title = self.title

        timecode = self.timecode

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if title is not UNSET:
            field_dict["title"] = title
        if timecode is not UNSET:
            field_dict["timecode"] = timecode

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        title = d.pop("title", UNSET)

        timecode = d.pop("timecode", UNSET)

        replace_video_chapters_body_chapters_item = cls(
            title=title,
            timecode=timecode,
        )

        replace_video_chapters_body_chapters_item.additional_properties = d
        return replace_video_chapters_body_chapters_item

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
