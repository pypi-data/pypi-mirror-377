from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="ServerConfigOpenTelemetryMetrics")


@_attrs_define
class ServerConfigOpenTelemetryMetrics:
    """Attributes:
    enabled (Union[Unset, bool]):
    playback_stats_interval (Union[Unset, float]): Milliseconds
    """

    enabled: Unset | bool = UNSET
    playback_stats_interval: Unset | float = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        enabled = self.enabled

        playback_stats_interval = self.playback_stats_interval

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if playback_stats_interval is not UNSET:
            field_dict["playbackStatsInterval"] = playback_stats_interval

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        enabled = d.pop("enabled", UNSET)

        playback_stats_interval = d.pop("playbackStatsInterval", UNSET)

        server_config_open_telemetry_metrics = cls(
            enabled=enabled,
            playback_stats_interval=playback_stats_interval,
        )

        server_config_open_telemetry_metrics.additional_properties = d
        return server_config_open_telemetry_metrics

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
