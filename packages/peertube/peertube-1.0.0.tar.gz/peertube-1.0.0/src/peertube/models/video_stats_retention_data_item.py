from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="VideoStatsRetentionDataItem")


@_attrs_define
class VideoStatsRetentionDataItem:
    """Attributes:
    second (Union[Unset, float]):
    retention_percent (Union[Unset, float]):
    """

    second: Unset | float = UNSET
    retention_percent: Unset | float = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        second = self.second

        retention_percent = self.retention_percent

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if second is not UNSET:
            field_dict["second"] = second
        if retention_percent is not UNSET:
            field_dict["retentionPercent"] = retention_percent

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        second = d.pop("second", UNSET)

        retention_percent = d.pop("retentionPercent", UNSET)

        video_stats_retention_data_item = cls(
            second=second,
            retention_percent=retention_percent,
        )

        video_stats_retention_data_item.additional_properties = d
        return video_stats_retention_data_item

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
