from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="VODAudioMergeTranscodingInput")


@_attrs_define
class VODAudioMergeTranscodingInput:
    """Attributes:
    audio_file_url (Union[Unset, str]):
    preview_file_url (Union[Unset, str]):
    """

    audio_file_url: Unset | str = UNSET
    preview_file_url: Unset | str = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        audio_file_url = self.audio_file_url

        preview_file_url = self.preview_file_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if audio_file_url is not UNSET:
            field_dict["audioFileUrl"] = audio_file_url
        if preview_file_url is not UNSET:
            field_dict["previewFileUrl"] = preview_file_url

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        audio_file_url = d.pop("audioFileUrl", UNSET)

        preview_file_url = d.pop("previewFileUrl", UNSET)

        vod_audio_merge_transcoding_input = cls(
            audio_file_url=audio_file_url,
            preview_file_url=preview_file_url,
        )

        vod_audio_merge_transcoding_input.additional_properties = d
        return vod_audio_merge_transcoding_input

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
