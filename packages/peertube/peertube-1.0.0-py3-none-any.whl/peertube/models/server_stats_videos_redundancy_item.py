from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="ServerStatsVideosRedundancyItem")


@_attrs_define
class ServerStatsVideosRedundancyItem:
    """Attributes:
    strategy (Union[Unset, str]):
    total_size (Union[Unset, float]):
    total_used (Union[Unset, float]):
    total_video_files (Union[Unset, float]):
    total_videos (Union[Unset, float]):
    """

    strategy: Unset | str = UNSET
    total_size: Unset | float = UNSET
    total_used: Unset | float = UNSET
    total_video_files: Unset | float = UNSET
    total_videos: Unset | float = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        strategy = self.strategy

        total_size = self.total_size

        total_used = self.total_used

        total_video_files = self.total_video_files

        total_videos = self.total_videos

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if strategy is not UNSET:
            field_dict["strategy"] = strategy
        if total_size is not UNSET:
            field_dict["totalSize"] = total_size
        if total_used is not UNSET:
            field_dict["totalUsed"] = total_used
        if total_video_files is not UNSET:
            field_dict["totalVideoFiles"] = total_video_files
        if total_videos is not UNSET:
            field_dict["totalVideos"] = total_videos

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        strategy = d.pop("strategy", UNSET)

        total_size = d.pop("totalSize", UNSET)

        total_used = d.pop("totalUsed", UNSET)

        total_video_files = d.pop("totalVideoFiles", UNSET)

        total_videos = d.pop("totalVideos", UNSET)

        server_stats_videos_redundancy_item = cls(
            strategy=strategy,
            total_size=total_size,
            total_used=total_used,
            total_video_files=total_video_files,
            total_videos=total_videos,
        )

        server_stats_videos_redundancy_item.additional_properties = d
        return server_stats_videos_redundancy_item

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
