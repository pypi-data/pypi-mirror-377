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

from peertube.models.file_storage import FileStorage
from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.video_resolution_constant import VideoResolutionConstant


T = TypeVar("T", bound="VideoFile")


@_attrs_define
class VideoFile:
    """Attributes:
    id (Union[Unset, int]):  Example: 42.
    magnet_uri (Union[Unset, str]): magnet URI allowing to resolve the video via BitTorrent without a metainfo file
    resolution (Union[Unset, VideoResolutionConstant]): resolutions and their labels for the video
    size (Union[Unset, int]): Video file size in bytes
    torrent_url (Union[Unset, str]): Direct URL of the torrent file
    torrent_download_url (Union[Unset, str]): URL endpoint that transfers the torrent file as an attachment (so that
        the browser opens a download dialog)
    file_url (Union[Unset, str]): Direct URL of the video
    playlist_url (Union[Unset, str]): Playlist URL of the file if it is owned by a playlist
    file_download_url (Union[Unset, str]): URL endpoint that transfers the video file as an attachment (so that the
        browser opens a download dialog)
    fps (Union[Unset, float]): Frames per second of the video file
    width (Union[Unset, float]): **PeerTube >= 6.1** Video stream width
    height (Union[Unset, float]): **PeerTube >= 6.1** Video stream height
    metadata_url (Union[Unset, str]): URL dereferencing the output of ffprobe on the file
    has_audio (Union[Unset, bool]): **PeerTube >= 6.2** The file container has an audio stream
    has_video (Union[Unset, bool]): **PeerTube >= 6.2** The file container has a video stream
    storage (Union[Unset, FileStorage]): The file storage type:
          - `0` File system
          - `1` Object storage
    """

    id: Unset | int = UNSET
    magnet_uri: Unset | str = UNSET
    resolution: Union[Unset, "VideoResolutionConstant"] = UNSET
    size: Unset | int = UNSET
    torrent_url: Unset | str = UNSET
    torrent_download_url: Unset | str = UNSET
    file_url: Unset | str = UNSET
    playlist_url: Unset | str = UNSET
    file_download_url: Unset | str = UNSET
    fps: Unset | float = UNSET
    width: Unset | float = UNSET
    height: Unset | float = UNSET
    metadata_url: Unset | str = UNSET
    has_audio: Unset | bool = UNSET
    has_video: Unset | bool = UNSET
    storage: Unset | FileStorage = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        id = self.id

        magnet_uri = self.magnet_uri

        resolution: Unset | dict[str, Any] = UNSET
        if not isinstance(self.resolution, Unset):
            resolution = self.resolution.to_dict()

        size = self.size

        torrent_url = self.torrent_url

        torrent_download_url = self.torrent_download_url

        file_url = self.file_url

        playlist_url = self.playlist_url

        file_download_url = self.file_download_url

        fps = self.fps

        width = self.width

        height = self.height

        metadata_url = self.metadata_url

        has_audio = self.has_audio

        has_video = self.has_video

        storage: Unset | int = UNSET
        if not isinstance(self.storage, Unset):
            storage = self.storage.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if magnet_uri is not UNSET:
            field_dict["magnetUri"] = magnet_uri
        if resolution is not UNSET:
            field_dict["resolution"] = resolution
        if size is not UNSET:
            field_dict["size"] = size
        if torrent_url is not UNSET:
            field_dict["torrentUrl"] = torrent_url
        if torrent_download_url is not UNSET:
            field_dict["torrentDownloadUrl"] = torrent_download_url
        if file_url is not UNSET:
            field_dict["fileUrl"] = file_url
        if playlist_url is not UNSET:
            field_dict["playlistUrl"] = playlist_url
        if file_download_url is not UNSET:
            field_dict["fileDownloadUrl"] = file_download_url
        if fps is not UNSET:
            field_dict["fps"] = fps
        if width is not UNSET:
            field_dict["width"] = width
        if height is not UNSET:
            field_dict["height"] = height
        if metadata_url is not UNSET:
            field_dict["metadataUrl"] = metadata_url
        if has_audio is not UNSET:
            field_dict["hasAudio"] = has_audio
        if has_video is not UNSET:
            field_dict["hasVideo"] = has_video
        if storage is not UNSET:
            field_dict["storage"] = storage

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.video_resolution_constant import VideoResolutionConstant

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        magnet_uri = d.pop("magnetUri", UNSET)

        _resolution = d.pop("resolution", UNSET)
        resolution: Unset | VideoResolutionConstant
        if isinstance(_resolution, Unset):
            resolution = UNSET
        else:
            resolution = VideoResolutionConstant.from_dict(_resolution)

        size = d.pop("size", UNSET)

        torrent_url = d.pop("torrentUrl", UNSET)

        torrent_download_url = d.pop("torrentDownloadUrl", UNSET)

        file_url = d.pop("fileUrl", UNSET)

        playlist_url = d.pop("playlistUrl", UNSET)

        file_download_url = d.pop("fileDownloadUrl", UNSET)

        fps = d.pop("fps", UNSET)

        width = d.pop("width", UNSET)

        height = d.pop("height", UNSET)

        metadata_url = d.pop("metadataUrl", UNSET)

        has_audio = d.pop("hasAudio", UNSET)

        has_video = d.pop("hasVideo", UNSET)

        _storage = d.pop("storage", UNSET)
        storage: Unset | FileStorage
        if isinstance(_storage, Unset):
            storage = UNSET
        else:
            storage = FileStorage(_storage)

        video_file = cls(
            id=id,
            magnet_uri=magnet_uri,
            resolution=resolution,
            size=size,
            torrent_url=torrent_url,
            torrent_download_url=torrent_download_url,
            file_url=file_url,
            playlist_url=playlist_url,
            file_download_url=file_download_url,
            fps=fps,
            width=width,
            height=height,
            metadata_url=metadata_url,
            has_audio=has_audio,
            has_video=has_video,
            storage=storage,
        )

        video_file.additional_properties = d
        return video_file

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
