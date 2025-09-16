import datetime
from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse
from typing_extensions import Self

from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.video_stats_overall_countries_item import (
        VideoStatsOverallCountriesItem,
    )
    from peertube.models.video_stats_overall_subdivisions_item import (
        VideoStatsOverallSubdivisionsItem,
    )


T = TypeVar("T", bound="VideoStatsOverall")


@_attrs_define
class VideoStatsOverall:
    """Attributes:
    average_watch_time (Union[Unset, float]):
    total_watch_time (Union[Unset, float]):
    viewers_peak (Union[Unset, float]):
    total_viewers (Union[Unset, float]):
    viewers_peak_date (Union[Unset, datetime.datetime]):
    countries (Union[Unset, list['VideoStatsOverallCountriesItem']]):
    subdivisions (Union[Unset, list['VideoStatsOverallSubdivisionsItem']]):
    """

    average_watch_time: Unset | float = UNSET
    total_watch_time: Unset | float = UNSET
    viewers_peak: Unset | float = UNSET
    total_viewers: Unset | float = UNSET
    viewers_peak_date: Unset | datetime.datetime = UNSET
    countries: Unset | list["VideoStatsOverallCountriesItem"] = UNSET
    subdivisions: Unset | list["VideoStatsOverallSubdivisionsItem"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        average_watch_time = self.average_watch_time

        total_watch_time = self.total_watch_time

        viewers_peak = self.viewers_peak

        total_viewers = self.total_viewers

        viewers_peak_date: Unset | str = UNSET
        if not isinstance(self.viewers_peak_date, Unset):
            viewers_peak_date = self.viewers_peak_date.isoformat()

        countries: Unset | list[dict[str, Any]] = UNSET
        if not isinstance(self.countries, Unset):
            countries = []
            for countries_item_data in self.countries:
                countries_item = countries_item_data.to_dict()
                countries.append(countries_item)

        subdivisions: Unset | list[dict[str, Any]] = UNSET
        if not isinstance(self.subdivisions, Unset):
            subdivisions = []
            for subdivisions_item_data in self.subdivisions:
                subdivisions_item = subdivisions_item_data.to_dict()
                subdivisions.append(subdivisions_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if average_watch_time is not UNSET:
            field_dict["averageWatchTime"] = average_watch_time
        if total_watch_time is not UNSET:
            field_dict["totalWatchTime"] = total_watch_time
        if viewers_peak is not UNSET:
            field_dict["viewersPeak"] = viewers_peak
        if total_viewers is not UNSET:
            field_dict["totalViewers"] = total_viewers
        if viewers_peak_date is not UNSET:
            field_dict["viewersPeakDate"] = viewers_peak_date
        if countries is not UNSET:
            field_dict["countries"] = countries
        if subdivisions is not UNSET:
            field_dict["subdivisions"] = subdivisions

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.video_stats_overall_countries_item import (
            VideoStatsOverallCountriesItem,
        )
        from peertube.models.video_stats_overall_subdivisions_item import (
            VideoStatsOverallSubdivisionsItem,
        )

        d = dict(src_dict)
        average_watch_time = d.pop("averageWatchTime", UNSET)

        total_watch_time = d.pop("totalWatchTime", UNSET)

        viewers_peak = d.pop("viewersPeak", UNSET)

        total_viewers = d.pop("totalViewers", UNSET)

        _viewers_peak_date = d.pop("viewersPeakDate", UNSET)
        viewers_peak_date: Unset | datetime.datetime
        if isinstance(_viewers_peak_date, Unset):
            viewers_peak_date = UNSET
        else:
            viewers_peak_date = isoparse(_viewers_peak_date)

        countries = []
        _countries = d.pop("countries", UNSET)
        for countries_item_data in _countries or []:
            countries_item = VideoStatsOverallCountriesItem.from_dict(
                countries_item_data
            )

            countries.append(countries_item)

        subdivisions = []
        _subdivisions = d.pop("subdivisions", UNSET)
        for subdivisions_item_data in _subdivisions or []:
            subdivisions_item = VideoStatsOverallSubdivisionsItem.from_dict(
                subdivisions_item_data
            )

            subdivisions.append(subdivisions_item)

        video_stats_overall = cls(
            average_watch_time=average_watch_time,
            total_watch_time=total_watch_time,
            viewers_peak=viewers_peak,
            total_viewers=total_viewers,
            viewers_peak_date=viewers_peak_date,
            countries=countries,
            subdivisions=subdivisions,
        )

        video_stats_overall.additional_properties = d
        return video_stats_overall

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
