import datetime
from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse
from typing_extensions import Self

from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.video_resolution_constant import VideoResolutionConstant


T = TypeVar("T", bound="VideoSource")


@_attrs_define
class VideoSource:
    """Attributes:
    filename (Union[Unset, str]): Deprecated in 6.1, use inputFilename instead
    input_filename (Union[Unset, str]): Uploaded/imported filename
    file_download_url (Union[Unset, str]): **PeerTube >= 6.1** If enabled by the admin, the video source file is
        kept on the server and can be downloaded by the owner
    resolution (Union[Unset, VideoResolutionConstant]): resolutions and their labels for the video
    size (Union[Unset, int]): **PeerTube >= 6.1** Video file size in bytes
    fps (Union[Unset, float]): **PeerTube >= 6.1** Frames per second of the video file
    width (Union[Unset, int]): **PeerTube >= 6.1** Video stream width
    height (Union[Unset, int]): **PeerTube >= 6.1** Video stream height
    created_at (Union[Unset, datetime.datetime]):
    """

    filename: Unset | str = UNSET
    input_filename: Unset | str = UNSET
    file_download_url: Unset | str = UNSET
    resolution: Union[Unset, "VideoResolutionConstant"] = UNSET
    size: Unset | int = UNSET
    fps: Unset | float = UNSET
    width: Unset | int = UNSET
    height: Unset | int = UNSET
    created_at: Unset | datetime.datetime = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        filename = self.filename

        input_filename = self.input_filename

        file_download_url = self.file_download_url

        resolution: Unset | dict[str, Any] = UNSET
        if not isinstance(self.resolution, Unset):
            resolution = self.resolution.to_dict()

        size = self.size

        fps = self.fps

        width = self.width

        height = self.height

        created_at: Unset | str = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if filename is not UNSET:
            field_dict["filename"] = filename
        if input_filename is not UNSET:
            field_dict["inputFilename"] = input_filename
        if file_download_url is not UNSET:
            field_dict["fileDownloadUrl"] = file_download_url
        if resolution is not UNSET:
            field_dict["resolution"] = resolution
        if size is not UNSET:
            field_dict["size"] = size
        if fps is not UNSET:
            field_dict["fps"] = fps
        if width is not UNSET:
            field_dict["width"] = width
        if height is not UNSET:
            field_dict["height"] = height
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.video_resolution_constant import VideoResolutionConstant

        d = dict(src_dict)
        filename = d.pop("filename", UNSET)

        input_filename = d.pop("inputFilename", UNSET)

        file_download_url = d.pop("fileDownloadUrl", UNSET)

        _resolution = d.pop("resolution", UNSET)
        resolution: Unset | VideoResolutionConstant
        if isinstance(_resolution, Unset):
            resolution = UNSET
        else:
            resolution = VideoResolutionConstant.from_dict(_resolution)

        size = d.pop("size", UNSET)

        fps = d.pop("fps", UNSET)

        width = d.pop("width", UNSET)

        height = d.pop("height", UNSET)

        _created_at = d.pop("createdAt", UNSET)
        created_at: Unset | datetime.datetime
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        video_source = cls(
            filename=filename,
            input_filename=input_filename,
            file_download_url=file_download_url,
            resolution=resolution,
            size=size,
            fps=fps,
            width=width,
            height=height,
            created_at=created_at,
        )

        video_source.additional_properties = d
        return video_source

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
