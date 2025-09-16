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
    from peertube.models.server_config_search_remote_uri import (
        ServerConfigSearchRemoteUri,
    )


T = TypeVar("T", bound="ServerConfigSearch")


@_attrs_define
class ServerConfigSearch:
    """Attributes:
    remote_uri (Union[Unset, ServerConfigSearchRemoteUri]):
    """

    remote_uri: Union[Unset, "ServerConfigSearchRemoteUri"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        remote_uri: Unset | dict[str, Any] = UNSET
        if not isinstance(self.remote_uri, Unset):
            remote_uri = self.remote_uri.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if remote_uri is not UNSET:
            field_dict["remoteUri"] = remote_uri

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.server_config_search_remote_uri import (
            ServerConfigSearchRemoteUri,
        )

        d = dict(src_dict)
        _remote_uri = d.pop("remoteUri", UNSET)
        remote_uri: Unset | ServerConfigSearchRemoteUri
        if isinstance(_remote_uri, Unset):
            remote_uri = UNSET
        else:
            remote_uri = ServerConfigSearchRemoteUri.from_dict(_remote_uri)

        server_config_search = cls(
            remote_uri=remote_uri,
        )

        server_config_search.additional_properties = d
        return server_config_search

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
