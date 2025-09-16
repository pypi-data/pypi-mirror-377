from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="VODAudioMergeTranscodingOutput")


@_attrs_define
class VODAudioMergeTranscodingOutput:
    """Attributes:
    resolution (Union[Unset, float]):
    fps (Union[Unset, float]):
    """

    resolution: Unset | float = UNSET
    fps: Unset | float = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        resolution = self.resolution

        fps = self.fps

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if resolution is not UNSET:
            field_dict["resolution"] = resolution
        if fps is not UNSET:
            field_dict["fps"] = fps

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        resolution = d.pop("resolution", UNSET)

        fps = d.pop("fps", UNSET)

        vod_audio_merge_transcoding_output = cls(
            resolution=resolution,
            fps=fps,
        )

        vod_audio_merge_transcoding_output.additional_properties = d
        return vod_audio_merge_transcoding_output

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
