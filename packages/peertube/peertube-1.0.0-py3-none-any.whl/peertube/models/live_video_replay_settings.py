from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.models.video_privacy_set import VideoPrivacySet
from peertube.types import UNSET, Unset

T = TypeVar("T", bound="LiveVideoReplaySettings")


@_attrs_define
class LiveVideoReplaySettings:
    """Attributes:
    privacy (Union[Unset, VideoPrivacySet]): privacy id of the video (see
        [/videos/privacies](#operation/getVideoPrivacyPolicies))
    """

    privacy: Unset | VideoPrivacySet = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        privacy: Unset | int = UNSET
        if not isinstance(self.privacy, Unset):
            privacy = self.privacy.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if privacy is not UNSET:
            field_dict["privacy"] = privacy

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create from dictionary."""
        d = dict(src_dict)
        _privacy = d.pop("privacy", UNSET)
        privacy: Unset | VideoPrivacySet
        if isinstance(_privacy, Unset):
            privacy = UNSET
        else:
            privacy = VideoPrivacySet(_privacy)

        live_video_replay_settings = cls(
            privacy=privacy,
        )

        live_video_replay_settings.additional_properties = d
        return live_video_replay_settings

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
