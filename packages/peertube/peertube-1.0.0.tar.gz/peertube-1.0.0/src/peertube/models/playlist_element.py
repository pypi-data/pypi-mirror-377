from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.video import Video


T = TypeVar("T", bound="PlaylistElement")


@_attrs_define
class PlaylistElement:
    """Attributes:
    position (Union[Unset, int]):
    start_timestamp (Union[Unset, int]):
    stop_timestamp (Union[Unset, int]):
    video (Union['Video', None, Unset]):
    """

    position: Unset | int = UNSET
    start_timestamp: Unset | int = UNSET
    stop_timestamp: Unset | int = UNSET
    video: Union["Video", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        from peertube.models.video import Video

        position = self.position

        start_timestamp = self.start_timestamp

        stop_timestamp = self.stop_timestamp

        video: None | Unset | dict[str, Any]
        if isinstance(self.video, Unset):
            video = UNSET
        elif isinstance(self.video, Video):
            video = self.video.to_dict()
        else:
            video = self.video

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if position is not UNSET:
            field_dict["position"] = position
        if start_timestamp is not UNSET:
            field_dict["startTimestamp"] = start_timestamp
        if stop_timestamp is not UNSET:
            field_dict["stopTimestamp"] = stop_timestamp
        if video is not UNSET:
            field_dict["video"] = video

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.video import Video

        d = dict(src_dict)
        position = d.pop("position", UNSET)

        start_timestamp = d.pop("startTimestamp", UNSET)

        stop_timestamp = d.pop("stopTimestamp", UNSET)

        def _parse_video(data: object) -> Union["Video", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError
                video_type_1 = Video.from_dict(data)

                return video_type_1
            except:  # noqa: E722
                pass
            return cast("Video | None | Unset", data)

        video = _parse_video(d.pop("video", UNSET))

        playlist_element = cls(
            position=position,
            start_timestamp=start_timestamp,
            stop_timestamp=stop_timestamp,
            video=video,
        )

        playlist_element.additional_properties = d
        return playlist_element

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
