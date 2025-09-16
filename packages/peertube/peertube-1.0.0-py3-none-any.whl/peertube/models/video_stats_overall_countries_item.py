from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="VideoStatsOverallCountriesItem")


@_attrs_define
class VideoStatsOverallCountriesItem:
    """Attributes:
    iso_code (Union[Unset, str]):
    viewers (Union[Unset, float]):
    """

    iso_code: Unset | str = UNSET
    viewers: Unset | float = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        iso_code = self.iso_code

        viewers = self.viewers

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if iso_code is not UNSET:
            field_dict["isoCode"] = iso_code
        if viewers is not UNSET:
            field_dict["viewers"] = viewers

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        iso_code = d.pop("isoCode", UNSET)

        viewers = d.pop("viewers", UNSET)

        video_stats_overall_countries_item = cls(
            iso_code=iso_code,
            viewers=viewers,
        )

        video_stats_overall_countries_item.additional_properties = d
        return video_stats_overall_countries_item

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
