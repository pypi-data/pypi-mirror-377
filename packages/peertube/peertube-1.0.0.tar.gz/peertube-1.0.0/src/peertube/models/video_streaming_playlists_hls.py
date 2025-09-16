from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.video_file import VideoFile
    from peertube.models.video_streaming_playlists_hls_redundancies_item import (
        VideoStreamingPlaylistsHLSRedundanciesItem,
    )


T = TypeVar("T", bound="VideoStreamingPlaylistsHLS")


@_attrs_define
class VideoStreamingPlaylistsHLS:
    """Attributes:
    playlist_url (Union[Unset, str]):
    segments_sha_256_url (Union[Unset, str]):
    files (Union[Unset, list['VideoFile']]): Video files associated to this playlist.

        The difference with the root `files` property is that these files are fragmented, so they can be used in this
        streaming playlist (HLS, etc.)
    redundancies (Union[Unset, list['VideoStreamingPlaylistsHLSRedundanciesItem']]):
    """

    playlist_url: Unset | str = UNSET
    segments_sha_256_url: Unset | str = UNSET
    files: Unset | list["VideoFile"] = UNSET
    redundancies: Unset | list["VideoStreamingPlaylistsHLSRedundanciesItem"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        playlist_url = self.playlist_url

        segments_sha_256_url = self.segments_sha_256_url

        files: Unset | list[dict[str, Any]] = UNSET
        if not isinstance(self.files, Unset):
            files = []
            for files_item_data in self.files:
                files_item = files_item_data.to_dict()
                files.append(files_item)

        redundancies: Unset | list[dict[str, Any]] = UNSET
        if not isinstance(self.redundancies, Unset):
            redundancies = []
            for redundancies_item_data in self.redundancies:
                redundancies_item = redundancies_item_data.to_dict()
                redundancies.append(redundancies_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if playlist_url is not UNSET:
            field_dict["playlistUrl"] = playlist_url
        if segments_sha_256_url is not UNSET:
            field_dict["segmentsSha256Url"] = segments_sha_256_url
        if files is not UNSET:
            field_dict["files"] = files
        if redundancies is not UNSET:
            field_dict["redundancies"] = redundancies

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.video_file import VideoFile
        from peertube.models.video_streaming_playlists_hls_redundancies_item import (
            VideoStreamingPlaylistsHLSRedundanciesItem,
        )

        d = dict(src_dict)
        playlist_url = d.pop("playlistUrl", UNSET)

        segments_sha_256_url = d.pop("segmentsSha256Url", UNSET)

        files = []
        _files = d.pop("files", UNSET)
        for files_item_data in _files or []:
            files_item = VideoFile.from_dict(files_item_data)

            files.append(files_item)

        redundancies = []
        _redundancies = d.pop("redundancies", UNSET)
        for redundancies_item_data in _redundancies or []:
            redundancies_item = VideoStreamingPlaylistsHLSRedundanciesItem.from_dict(
                redundancies_item_data
            )

            redundancies.append(redundancies_item)

        video_streaming_playlists_hls = cls(
            playlist_url=playlist_url,
            segments_sha_256_url=segments_sha_256_url,
            files=files,
            redundancies=redundancies,
        )

        video_streaming_playlists_hls.additional_properties = d
        return video_streaming_playlists_hls

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
