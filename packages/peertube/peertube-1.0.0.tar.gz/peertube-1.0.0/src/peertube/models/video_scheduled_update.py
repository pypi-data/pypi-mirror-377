import datetime
from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse
from typing_extensions import Self

from peertube.models.video_privacy_set import VideoPrivacySet
from peertube.types import UNSET, Unset

T = TypeVar("T", bound="VideoScheduledUpdate")


@_attrs_define
class VideoScheduledUpdate:
    """Attributes:
    update_at (datetime.datetime): When to update the video
    privacy (Union[Unset, VideoPrivacySet]): privacy id of the video (see
        [/videos/privacies](#operation/getVideoPrivacyPolicies))
    """

    update_at: datetime.datetime
    privacy: Unset | VideoPrivacySet = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        update_at = self.update_at.isoformat()

        privacy: Unset | int = UNSET
        if not isinstance(self.privacy, Unset):
            privacy = self.privacy.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "updateAt": update_at,
            }
        )
        if privacy is not UNSET:
            field_dict["privacy"] = privacy

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        update_at = isoparse(d.pop("updateAt"))

        _privacy = d.pop("privacy", UNSET)
        privacy: Unset | VideoPrivacySet
        if isinstance(_privacy, Unset):
            privacy = UNSET
        else:
            privacy = VideoPrivacySet(_privacy)

        video_scheduled_update = cls(
            update_at=update_at,
            privacy=privacy,
        )

        video_scheduled_update.additional_properties = d
        return video_scheduled_update

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
