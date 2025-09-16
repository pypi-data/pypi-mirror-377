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
    from peertube.models.server_config_views_views_watching_interval import (
        ServerConfigViewsViewsWatchingInterval,
    )


T = TypeVar("T", bound="ServerConfigViewsViews")


@_attrs_define
class ServerConfigViewsViews:
    """Attributes:
    watching_interval (Union[Unset, ServerConfigViewsViewsWatchingInterval]):
    """

    watching_interval: Union[Unset, "ServerConfigViewsViewsWatchingInterval"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        watching_interval: Unset | dict[str, Any] = UNSET
        if not isinstance(self.watching_interval, Unset):
            watching_interval = self.watching_interval.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if watching_interval is not UNSET:
            field_dict["watchingInterval"] = watching_interval

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.server_config_views_views_watching_interval import (
            ServerConfigViewsViewsWatchingInterval,
        )

        d = dict(src_dict)
        _watching_interval = d.pop("watchingInterval", UNSET)
        watching_interval: Unset | ServerConfigViewsViewsWatchingInterval
        if isinstance(_watching_interval, Unset):
            watching_interval = UNSET
        else:
            watching_interval = ServerConfigViewsViewsWatchingInterval.from_dict(
                _watching_interval
            )

        server_config_views_views = cls(
            watching_interval=watching_interval,
        )

        server_config_views_views.additional_properties = d
        return server_config_views_views

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
