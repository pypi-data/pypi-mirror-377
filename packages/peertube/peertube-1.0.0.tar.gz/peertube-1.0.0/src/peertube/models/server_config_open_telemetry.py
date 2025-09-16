from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.server_config_open_telemetry_metrics import (
        ServerConfigOpenTelemetryMetrics,
    )


T = TypeVar("T", bound="ServerConfigOpenTelemetry")


@_attrs_define
class ServerConfigOpenTelemetry:
    """PeerTube >= 6.1

    Attributes:
        metrics (Union[Unset, ServerConfigOpenTelemetryMetrics]):
    """

    metrics: Union[Unset, "ServerConfigOpenTelemetryMetrics"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        metrics: Unset | dict[str, Any] = UNSET
        if not isinstance(self.metrics, Unset):
            metrics = self.metrics.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if metrics is not UNSET:
            field_dict["metrics"] = metrics

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.server_config_open_telemetry_metrics import (
            ServerConfigOpenTelemetryMetrics,
        )

        d = dict(src_dict)
        _metrics = d.pop("metrics", UNSET)
        metrics: Unset | ServerConfigOpenTelemetryMetrics
        if isinstance(_metrics, Unset):
            metrics = UNSET
        else:
            metrics = ServerConfigOpenTelemetryMetrics.from_dict(_metrics)

        server_config_open_telemetry = cls(
            metrics=metrics,
        )

        server_config_open_telemetry.additional_properties = d
        return server_config_open_telemetry

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
