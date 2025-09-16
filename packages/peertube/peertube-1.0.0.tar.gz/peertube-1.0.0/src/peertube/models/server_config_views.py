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
    from peertube.models.server_config_views_views import ServerConfigViewsViews


T = TypeVar("T", bound="ServerConfigViews")


@_attrs_define
class ServerConfigViews:
    """PeerTube >= 6.1

    Attributes:
        views (Union[Unset, ServerConfigViewsViews]):
    """

    views: Union[Unset, "ServerConfigViewsViews"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        views: Unset | dict[str, Any] = UNSET
        if not isinstance(self.views, Unset):
            views = self.views.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if views is not UNSET:
            field_dict["views"] = views

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.server_config_views_views import ServerConfigViewsViews

        d = dict(src_dict)
        _views = d.pop("views", UNSET)
        views: Unset | ServerConfigViewsViews
        if isinstance(_views, Unset):
            views = UNSET
        else:
            views = ServerConfigViewsViews.from_dict(_views)

        server_config_views = cls(
            views=views,
        )

        server_config_views.additional_properties = d
        return server_config_views

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
