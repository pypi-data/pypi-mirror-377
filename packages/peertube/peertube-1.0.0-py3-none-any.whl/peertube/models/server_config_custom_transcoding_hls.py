from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="ServerConfigCustomTranscodingHls")


@_attrs_define
class ServerConfigCustomTranscodingHls:
    """HLS specific settings

    Attributes:
        enabled (Union[Unset, bool]):
        split_audio_and_video (Union[Unset, bool]):
    """

    enabled: Unset | bool = UNSET
    split_audio_and_video: Unset | bool = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        enabled = self.enabled

        split_audio_and_video = self.split_audio_and_video

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if split_audio_and_video is not UNSET:
            field_dict["splitAudioAndVideo"] = split_audio_and_video

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        enabled = d.pop("enabled", UNSET)

        split_audio_and_video = d.pop("splitAudioAndVideo", UNSET)

        server_config_custom_transcoding_hls = cls(
            enabled=enabled,
            split_audio_and_video=split_audio_and_video,
        )

        server_config_custom_transcoding_hls.additional_properties = d
        return server_config_custom_transcoding_hls

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
