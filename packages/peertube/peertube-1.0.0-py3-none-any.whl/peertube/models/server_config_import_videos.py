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
    from peertube.models.server_config_import_videos_http import (
        ServerConfigImportVideosHttp,
    )
    from peertube.models.server_config_import_videos_torrent import (
        ServerConfigImportVideosTorrent,
    )


T = TypeVar("T", bound="ServerConfigImportVideos")


@_attrs_define
class ServerConfigImportVideos:
    """Attributes:
    http (Union[Unset, ServerConfigImportVideosHttp]):
    torrent (Union[Unset, ServerConfigImportVideosTorrent]):
    """

    http: Union[Unset, "ServerConfigImportVideosHttp"] = UNSET
    torrent: Union[Unset, "ServerConfigImportVideosTorrent"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        http: Unset | dict[str, Any] = UNSET
        if not isinstance(self.http, Unset):
            http = self.http.to_dict()

        torrent: Unset | dict[str, Any] = UNSET
        if not isinstance(self.torrent, Unset):
            torrent = self.torrent.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if http is not UNSET:
            field_dict["http"] = http
        if torrent is not UNSET:
            field_dict["torrent"] = torrent

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.server_config_import_videos_http import (
            ServerConfigImportVideosHttp,
        )
        from peertube.models.server_config_import_videos_torrent import (
            ServerConfigImportVideosTorrent,
        )

        d = dict(src_dict)
        _http = d.pop("http", UNSET)
        http: Unset | ServerConfigImportVideosHttp
        if isinstance(_http, Unset):
            http = UNSET
        else:
            http = ServerConfigImportVideosHttp.from_dict(_http)

        _torrent = d.pop("torrent", UNSET)
        torrent: Unset | ServerConfigImportVideosTorrent
        if isinstance(_torrent, Unset):
            torrent = UNSET
        else:
            torrent = ServerConfigImportVideosTorrent.from_dict(_torrent)

        server_config_import_videos = cls(
            http=http,
            torrent=torrent,
        )

        server_config_import_videos.additional_properties = d
        return server_config_import_videos

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
