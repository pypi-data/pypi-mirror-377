import datetime
from collections.abc import Mapping
from io import BytesIO
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse
from typing_extensions import Self

from peertube.types import UNSET, File, FileTypes, Unset

if TYPE_CHECKING:
    from peertube.models.video import Video
    from peertube.models.video_import_state_constant import VideoImportStateConstant


T = TypeVar("T", bound="VideoImport")


@_attrs_define
class VideoImport:
    """Attributes:
    id (Union[Unset, int]):  Example: 42.
    target_url (Union[Unset, str]): remote URL where to find the import's source video Example:
        https://framatube.org/videos/watch/9c9de5e8-0a1e-484a-b099-e80766180a6d.
    magnet_uri (Union[Unset, str]): magnet URI allowing to resolve the import's source video
    torrentfile (Union[Unset, File]): Torrent file containing only the video file
    torrent_name (Union[Unset, str]):
    state (Union[Unset, VideoImportStateConstant]):
    error (Union[Unset, str]):
    created_at (Union[Unset, datetime.datetime]):
    updated_at (Union[Unset, datetime.datetime]):
    video (Union['Video', None, Unset]):
    """

    id: Unset | int = UNSET
    target_url: Unset | str = UNSET
    magnet_uri: Unset | str = UNSET
    torrentfile: Unset | File = UNSET
    torrent_name: Unset | str = UNSET
    state: Union[Unset, "VideoImportStateConstant"] = UNSET
    error: Unset | str = UNSET
    created_at: Unset | datetime.datetime = UNSET
    updated_at: Unset | datetime.datetime = UNSET
    video: Union["Video", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        from peertube.models.video import Video

        id = self.id

        target_url = self.target_url

        magnet_uri = self.magnet_uri

        torrentfile: Unset | FileTypes = UNSET
        if not isinstance(self.torrentfile, Unset):
            torrentfile = self.torrentfile.to_tuple()

        torrent_name = self.torrent_name

        state: Unset | dict[str, Any] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.to_dict()

        error = self.error

        created_at: Unset | str = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: Unset | str = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        video: None | Unset | dict[str, Any]
        if isinstance(self.video, Unset):
            video = UNSET
        elif isinstance(self.video, Video):
            video = self.video.to_dict()
        else:
            video = self.video

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if target_url is not UNSET:
            field_dict["targetUrl"] = target_url
        if magnet_uri is not UNSET:
            field_dict["magnetUri"] = magnet_uri
        if torrentfile is not UNSET:
            field_dict["torrentfile"] = torrentfile
        if torrent_name is not UNSET:
            field_dict["torrentName"] = torrent_name
        if state is not UNSET:
            field_dict["state"] = state
        if error is not UNSET:
            field_dict["error"] = error
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if updated_at is not UNSET:
            field_dict["updatedAt"] = updated_at
        if video is not UNSET:
            field_dict["video"] = video

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.video import Video
        from peertube.models.video_import_state_constant import VideoImportStateConstant

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        target_url = d.pop("targetUrl", UNSET)

        magnet_uri = d.pop("magnetUri", UNSET)

        _torrentfile = d.pop("torrentfile", UNSET)
        torrentfile: Unset | File
        if isinstance(_torrentfile, Unset):
            torrentfile = UNSET
        else:
            torrentfile = File(payload=BytesIO(_torrentfile))

        torrent_name = d.pop("torrentName", UNSET)

        _state = d.pop("state", UNSET)
        state: Unset | VideoImportStateConstant
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = VideoImportStateConstant.from_dict(_state)

        error = d.pop("error", UNSET)

        _created_at = d.pop("createdAt", UNSET)
        created_at: Unset | datetime.datetime
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _updated_at = d.pop("updatedAt", UNSET)
        updated_at: Unset | datetime.datetime
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        def _parse_video(data: object) -> Union["Video", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError
                video_type_1 = Video.from_dict(data)

                return video_type_1
            except:  # noqa: E722
                pass
            return cast("Video | None | Unset", data)

        video = _parse_video(d.pop("video", UNSET))

        video_import = cls(
            id=id,
            target_url=target_url,
            magnet_uri=magnet_uri,
            torrentfile=torrentfile,
            torrent_name=torrent_name,
            state=state,
            error=error,
            created_at=created_at,
            updated_at=updated_at,
            video=video,
        )

        video_import.additional_properties = d
        return video_import

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
