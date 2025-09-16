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
    from peertube.models.server_config_custom_cache_captions import (
        ServerConfigCustomCacheCaptions,
    )
    from peertube.models.server_config_custom_cache_previews import (
        ServerConfigCustomCachePreviews,
    )


T = TypeVar("T", bound="ServerConfigCustomCache")


@_attrs_define
class ServerConfigCustomCache:
    """Attributes:
    previews (Union[Unset, ServerConfigCustomCachePreviews]):
    captions (Union[Unset, ServerConfigCustomCacheCaptions]):
    """

    previews: Union[Unset, "ServerConfigCustomCachePreviews"] = UNSET
    captions: Union[Unset, "ServerConfigCustomCacheCaptions"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        previews: Unset | dict[str, Any] = UNSET
        if not isinstance(self.previews, Unset):
            previews = self.previews.to_dict()

        captions: Unset | dict[str, Any] = UNSET
        if not isinstance(self.captions, Unset):
            captions = self.captions.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if previews is not UNSET:
            field_dict["previews"] = previews
        if captions is not UNSET:
            field_dict["captions"] = captions

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.server_config_custom_cache_captions import (
            ServerConfigCustomCacheCaptions,
        )
        from peertube.models.server_config_custom_cache_previews import (
            ServerConfigCustomCachePreviews,
        )

        d = dict(src_dict)
        _previews = d.pop("previews", UNSET)
        previews: Unset | ServerConfigCustomCachePreviews
        if isinstance(_previews, Unset):
            previews = UNSET
        else:
            previews = ServerConfigCustomCachePreviews.from_dict(_previews)

        _captions = d.pop("captions", UNSET)
        captions: Unset | ServerConfigCustomCacheCaptions
        if isinstance(_captions, Unset):
            captions = UNSET
        else:
            captions = ServerConfigCustomCacheCaptions.from_dict(_captions)

        server_config_custom_cache = cls(
            previews=previews,
            captions=captions,
        )

        server_config_custom_cache.additional_properties = d
        return server_config_custom_cache

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
