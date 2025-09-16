from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.models.create_video_transcoding_body_transcoding_type import (
    CreateVideoTranscodingBodyTranscodingType,
)
from peertube.types import UNSET, Unset

T = TypeVar("T", bound="CreateVideoTranscodingBody")


@_attrs_define
class CreateVideoTranscodingBody:
    """Attributes:
    transcoding_type (CreateVideoTranscodingBodyTranscodingType):
    force_transcoding (Union[Unset, bool]): If the video is stuck in transcoding state, do it anyway Default: False.
    """

    transcoding_type: CreateVideoTranscodingBodyTranscodingType
    force_transcoding: Unset | bool = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        transcoding_type = self.transcoding_type.value

        force_transcoding = self.force_transcoding

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "transcodingType": transcoding_type,
            }
        )
        if force_transcoding is not UNSET:
            field_dict["forceTranscoding"] = force_transcoding

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        transcoding_type = CreateVideoTranscodingBodyTranscodingType(
            d.pop("transcodingType")
        )

        force_transcoding = d.pop("forceTranscoding", UNSET)

        create_video_transcoding_body = cls(
            transcoding_type=transcoding_type,
            force_transcoding=force_transcoding,
        )

        create_video_transcoding_body.additional_properties = d
        return create_video_transcoding_body

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
