from collections.abc import Mapping
from io import BytesIO
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.models.post_api_v1_runners_jobs_job_uuid_update_body_payload_type_0_type import (
    PostApiV1RunnersJobsJobUUIDUpdateBodyPayloadType0Type,
)
from peertube.types import UNSET, File, FileTypes, Unset

T = TypeVar("T", bound="PostApiV1RunnersJobsJobUUIDUpdateBodyPayloadType0")


@_attrs_define
class PostApiV1RunnersJobsJobUUIDUpdateBodyPayloadType0:
    """Provide live transcoding chunks update

    Attributes:
        type_ (Union[Unset, PostApiV1RunnersJobsJobUUIDUpdateBodyPayloadType0Type]):
        master_playlist_file (Union[Unset, File]):
        resolution_playlist_file (Union[Unset, File]):
        resolution_playlist_filename (Union[Unset, str]):
        video_chunk_file (Union[Unset, File]):
        video_chunk_filename (Union[Unset, str]):
    """

    type_: Unset | PostApiV1RunnersJobsJobUUIDUpdateBodyPayloadType0Type = UNSET
    master_playlist_file: Unset | File = UNSET
    resolution_playlist_file: Unset | File = UNSET
    resolution_playlist_filename: Unset | str = UNSET
    video_chunk_file: Unset | File = UNSET
    video_chunk_filename: Unset | str = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        type_: Unset | str = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        master_playlist_file: Unset | FileTypes = UNSET
        if not isinstance(self.master_playlist_file, Unset):
            master_playlist_file = self.master_playlist_file.to_tuple()

        resolution_playlist_file: Unset | FileTypes = UNSET
        if not isinstance(self.resolution_playlist_file, Unset):
            resolution_playlist_file = self.resolution_playlist_file.to_tuple()

        resolution_playlist_filename = self.resolution_playlist_filename

        video_chunk_file: Unset | FileTypes = UNSET
        if not isinstance(self.video_chunk_file, Unset):
            video_chunk_file = self.video_chunk_file.to_tuple()

        video_chunk_filename = self.video_chunk_filename

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type_ is not UNSET:
            field_dict["type"] = type_
        if master_playlist_file is not UNSET:
            field_dict["masterPlaylistFile"] = master_playlist_file
        if resolution_playlist_file is not UNSET:
            field_dict["resolutionPlaylistFile"] = resolution_playlist_file
        if resolution_playlist_filename is not UNSET:
            field_dict["resolutionPlaylistFilename"] = resolution_playlist_filename
        if video_chunk_file is not UNSET:
            field_dict["videoChunkFile"] = video_chunk_file
        if video_chunk_filename is not UNSET:
            field_dict["videoChunkFilename"] = video_chunk_filename

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        _type_ = d.pop("type", UNSET)
        type_: Unset | PostApiV1RunnersJobsJobUUIDUpdateBodyPayloadType0Type
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = PostApiV1RunnersJobsJobUUIDUpdateBodyPayloadType0Type(_type_)

        _master_playlist_file = d.pop("masterPlaylistFile", UNSET)
        master_playlist_file: Unset | File
        if isinstance(_master_playlist_file, Unset):
            master_playlist_file = UNSET
        else:
            master_playlist_file = File(payload=BytesIO(_master_playlist_file))

        _resolution_playlist_file = d.pop("resolutionPlaylistFile", UNSET)
        resolution_playlist_file: Unset | File
        if isinstance(_resolution_playlist_file, Unset):
            resolution_playlist_file = UNSET
        else:
            resolution_playlist_file = File(payload=BytesIO(_resolution_playlist_file))

        resolution_playlist_filename = d.pop("resolutionPlaylistFilename", UNSET)

        _video_chunk_file = d.pop("videoChunkFile", UNSET)
        video_chunk_file: Unset | File
        if isinstance(_video_chunk_file, Unset):
            video_chunk_file = UNSET
        else:
            video_chunk_file = File(payload=BytesIO(_video_chunk_file))

        video_chunk_filename = d.pop("videoChunkFilename", UNSET)

        post_api_v1_runners_jobs_job_uuid_update_body_payload_type_0 = cls(
            type_=type_,
            master_playlist_file=master_playlist_file,
            resolution_playlist_file=resolution_playlist_file,
            resolution_playlist_filename=resolution_playlist_filename,
            video_chunk_file=video_chunk_file,
            video_chunk_filename=video_chunk_filename,
        )

        post_api_v1_runners_jobs_job_uuid_update_body_payload_type_0.additional_properties = d
        return post_api_v1_runners_jobs_job_uuid_update_body_payload_type_0

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
