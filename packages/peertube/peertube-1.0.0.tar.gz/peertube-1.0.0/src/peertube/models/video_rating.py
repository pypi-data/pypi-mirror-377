from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.models.video_rating_rating import VideoRatingRating

if TYPE_CHECKING:
    from peertube.models.video import Video


T = TypeVar("T", bound="VideoRating")


@_attrs_define
class VideoRating:
    """Attributes:
    video (Video):
    rating (VideoRatingRating): Rating of the video
    """

    video: "Video"
    rating: VideoRatingRating
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        video = self.video.to_dict()

        rating = self.rating.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "video": video,
                "rating": rating,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.video import Video

        d = dict(src_dict)
        video = Video.from_dict(d.pop("video"))

        rating = VideoRatingRating(d.pop("rating"))

        video_rating = cls(
            video=video,
            rating=rating,
        )

        video_rating.additional_properties = d
        return video_rating

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
